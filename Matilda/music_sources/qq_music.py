# coding=utf-8
# __author__ = 'Mio'
from random import random
from time import time

from Matilda.music_sources.song import Song, Album, Singer, Playlist
from Matilda.utils import async_request
from Matilda.utils.async_request import parse_body2json

VKEY_URL = "https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg"

SEARCH_URL = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
DETAILS_URL = "https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg"
SONG_MEDIA_URL = "http://ws.stream.qqmusic.qq.com/C100{song_mid}.m4a?fromtag=38"
PLAYLIST_URL = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg"

ALBUM_DETAILS_URL = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg"
ALBUM_PIC_URL = "https://y.gtimg.cn/music/photo_new/T002R300x300M000{album_media_id}.jpg"  # get 300x300 pic of album

QUALITY_192K = "192k"
QUALITY_320K = "320k"
QUALITY_APE = "ape"
QUALITY_FLAC = "flac"

QUALITY_D = {
    QUALITY_192K: ['M500', 'mp3'],
    QUALITY_320K: ['M800', 'mp3'],
    QUALITY_APE: ["A000", 'ape'],
    QUALITY_FLAC: ['F000', 'flac']
}


class QQMusic(object):
    def __init__(self, quality=QUALITY_320K):
        # self.req = async.GAsyncHTTPClient()
        self.req = async_request
        self.quality = quality

    async def search(self, key_words, page=1, number=5, current_page=1):
        params = {
            "format": "json",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": 0,
            "platform": "yqq",
            "g_tk": "5381",
            "cr": current_page,  # current page
            "p": page,  # page
            "n": number,  # number
            "w": key_words,  # key words
        }
        # res = await self.req.fetch(url_concat(url=SEARCH_URL, args=params), validate_cert=False)
        res = await self.req.get(url=SEARCH_URL, params=params, validate_cert=False)
        data = parse_body2json(res)

        song_list = data['data']['song']['list']
        return [await self.make_song(song) for song in song_list]

    async def make_song(self, song):
        return QSong(
            song_name=song['songname'],
            song_id=song['songid'],
            song_mid=song['songmid'],
            song_media_url=await self.song_media_url(song['songmid']),
            lyric="",
            album=Album(
                id=song['albumid'], mid=song['albummid'],
                name=song['albumname'],
                pic_url=self.album_pic_url(song['albummid'])
            ),
            singer=[
                Singer(
                    id=singer['id'], mid=singer['mid'], name=singer['name']
                ) for singer in song['singer']
            ],
            # song['alertid']: 0:无版权, 2:独家+MV, 11:无标签, 100002:独家+MV,
            is_playable=False if song['alertid'] == 0 else True
        )

    async def details(self, song_mid):
        """
        song details included a m4a url
        :param song_mid:
        :return:
        """
        params = {
            "songmid": song_mid,
            "format": "json",
            "g_tk": 5381,
            "inCharset": "utf8",
            "outCharset": "utf-8",
        }
        res = await self.req.get(url=DETAILS_URL, params=params)
        data = parse_body2json(res)

        # print(f"{data['data'][0]['name']:<15}|{data['data'][0]['album']['name']:^15}")
        return data

    async def get_vkey_guid(self, songmid):
        filename = f'C400{songmid}.m4a'
        guid = int(random() * 2147483647) * int(time() * 1000) % 10000000000
        d = {
            'format': 'json',
            'cid': 205361747,
            'uin': 0,
            'songmid': songmid,
            'filename': filename,
            'guid': guid,
        }

        res = await self.req.get(url=VKEY_URL, params=d)
        data = parse_body2json(res)
        return data['data']['items'][0]['vkey'], guid

    async def song_media_url(self, song_mid, quality=None, uin=0):
        # data = await self.details(song_mid=song_mid)
        # return list(data['url'].values())[0] if data['url'] else None
        quality = QUALITY_D.get(quality) if quality else QUALITY_D.get(self.quality)
        filename = f"{quality[0]}{song_mid}.{quality[1]}"
        vkey, guid = await self.get_vkey_guid(song_mid)
        return f'http://streamoc.music.tc.qq.com/{filename}?vkey={vkey}&guid={guid}&uin={uin}&fromtag=1'
        # return SONG_MEDIA_URL.format(song_mid=song_mid)

    def album_pic_url(self, album_mid):
        return ALBUM_PIC_URL.format(album_media_id=album_mid)

    async def album_details(self, album_media_id):
        params = {
            "albummid": album_media_id,
            "g_tk": 5381,
            "format": "json",
            "inCharset": "utf8",
            "outCharset": "utf-8",
        }
        res = await self.req.get(url=ALBUM_DETAILS_URL, params=params)
        data = parse_body2json(res)
        # data['code'] == 0 is good, or is not
        # TODO need a common parse response method
        data['data']['ablum_pic_url'] = self.album_pic_url(album_media_id)
        return data['data']

    async def playlist(self, pl_id):
        params = {
            "type": "1",
            "json": "1",
            "utf8": "1",
            "disstid": str(pl_id),
            "format": "json",
            "g_tk": "5381",
            "inCharset": "utf8",
            "outCharset": "utf - 8",
            "song_begin": "0",
            "song_num": "200",
        }
        headers = {
            "Referer": "https://y.qq.com/n/yqq/playlist",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }
        res = await self.req.get(url=PLAYLIST_URL, params=params, headers=headers)
        result = parse_body2json(res)
        cd_list = result.get('cdlist')
        if cd_list:
            cd = cd_list[0]
            songs_list = cd.get('songlist')
            if songs_list:
                return Playlist(
                    name=cd['dissname'],
                    songs=[await self.make_song(s) for s in songs_list],
                    cover_img_url=cd['logo']
                )
            else:
                raise Exception("songlist not found or is empty")
        else:
            raise Exception("cdlist not found or is empty")


class QSong(Song):
    def __str__(self):
        return f"QQMusic Song {self.song_name}"

    @property
    def papa(self):
        return "QQMusic"


if __name__ == '__main__':
    client = QQMusic()
    import asyncio


    async def test():
        rst = await client.search("田馥甄 渺小")
        rst = await client.playlist("3802473507")
        # print(rst)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
