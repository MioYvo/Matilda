# coding=utf-8
# __author__ = 'Mio'
from random import randrange

from Matilda.music_sources.song import Song, Album, Singer, Playlist, AlbumDetail
from Matilda.utils import async_request
from Matilda.utils.async_request import parse_body2json
from Matilda.utils.http_code import HTTP_200_OK

VKEY_URL = "http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg"

SEARCH_URL = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
DETAILS_URL = "https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg"
SONG_MEDIA_URL = "http://ws.stream.qqmusic.qq.com/C100{song_mid}.m4a?fromtag=38"
PLAYLIST_URL = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg"

ALBUM_DETAILS_URL = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg"
ALBUM_PIC_URL = "https://y.gtimg.cn/music/photo_new/T002R300x300M000{album_media_id}.jpg"  # get 300x300 pic of album

from collections import namedtuple
Quality = namedtuple('Quality', ['prefix', 'ext'])

QUALITY_128K = Quality(prefix='C400', ext='mp3')
QUALITY_192K = Quality(prefix='M500', ext='mp3')
QUALITY_320K = Quality(prefix='M800', ext='mp3')
QUALITY_APE = Quality(prefix="A000", ext='ape')
QUALITY_FLAC = Quality(prefix='F000', ext='flac')


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
        song_media_url, is_playable = await self.song_media_url(song['songmid'])
        return QSong(
            song_name=song['songname'],
            song_id=song['songid'],
            song_mid=song['songmid'],
            song_media_url=song_media_url,
            is_playable=is_playable,
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
            # is_playable=False if song['alertid'] == 0 else True
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

    async def get_vkey_guid(self):
        guid = str(randrange(1000000000, 10000000000))
        params = {"guid": guid, "format": "json", "json": 3}
        headers = {
            "referer": "http://y.qq.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46"
                          + " (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
        }

        res = await self.req.get(url=VKEY_URL, params=params, headers=headers)
        if res.code != HTTP_200_OK:
            raise Exception(res.body)
        data = parse_body2json(res)
        return data['key'], guid

    async def song_media_url(self, song_mid) -> (str, bool):
        if not song_mid:
            return '', False

        vkey, guid = await self.get_vkey_guid()

        for quality in (QUALITY_320K, QUALITY_192K, QUALITY_128K):
            url = "http://dl.stream.qqmusic.qq.com/%s%s.mp3?vkey=%s&guid=%s&fromtag=1" % (
                quality.prefix,
                song_mid,
                vkey,
                guid,
            )
            if await self.check_playable(url):
                return url, True
        else:
            return '', False

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
        album_detail = parse_body2json(res)
        # data['code'] == 0 is good, or is not
        # TODO need a common parse response method
        if album_detail.get('code', -1) == 0:
            return AlbumDetail(
                name=album_detail['data']['name'],
                songs=[await self.make_song(s) for s in album_detail['data']['list']],
                cover_img_url=self.album_pic_url(album_media_id),
                singer=Singer(
                    id=album_detail['data']['singerid'],
                    mid=album_detail['data']['singermid'],
                    name=album_detail['data']['singername']
                )
            )
        raise Exception(album_detail.get('message', 'album details error'))

    async def check_playable(self, media_url):
        res = await self.req.head(media_url, raise_error=False)
        if res.code != HTTP_200_OK:
            return False
        else:
            return True

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

# if __name__ == '__main__':
#     client = QQMusic()
#     import asyncio
#
#     async def test():
#         rst = await client.search("田馥甄 渺小")
#         rst = await client.playlist("3802473507")
#         print(rst)
#
#
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(test())
