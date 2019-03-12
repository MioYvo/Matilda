# coding=utf-8
# __author__ = 'Mio'
import logging

from Matilda.utils import async_request
from Matilda.utils.web import BaseRequestHandler
from Matilda.music_sources import qqm_client, nem_client
from tornado.httputil import urlparse, parse_qsl
from urllib.parse import parse_qs

NETLOC_163 = "music.163.com"
NETLOC_QQ = "y.qq.com"


class PlayList(BaseRequestHandler):
    # noinspection PyUnusedLocal
    def get(self, *args, **kwargs):
        self.render("search_playlist.html")


class ImportPlayList(BaseRequestHandler):
    # noinspection PyUnusedLocal
    async def get(self, *args, **kwargs):
        """

        QQM: id 2894607664 in "http://url.cn/55TSszn" --> https://y.qq.com/w/taoge.html?id=2894607664
        NEM: id 751385113 in "分享mio刘的歌单《陈粒》http://music.163.com/playlist/751385113/46154092?userid=46154092 (@网易云音乐)"
        :param args:
        :param kwargs:
        :return:
        """
        pl_url = self.get_query_argument("pl", None)
        if not pl_url:
            # TODO Error Page
            logging.error('no pl_url')
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        pl_url = await self.prepare_url(pl_url)

        if not pl_url:
            logging.error("no pl url")
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        # parse the url
        url_parsed = urlparse(pl_url)
        if url_parsed.netloc not in (NETLOC_163, NETLOC_QQ):
            # TODO Error Page
            logging.error("no NETLOC")
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        # TODO get user's info and play list info
        if url_parsed.netloc == NETLOC_163:
            pl_rst, pl = await self.parse_163_pl(url_parsed)
        else:
            pl_rst, pl = await self.parse_qq_pl(url_parsed)

        if not pl_rst:
            # TODO Error Page
            logging.error(f"no pl_rst {pl}")
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        for index, song in enumerate(pl.songs):
            if song.song_name.find("(") >= 0:
                # 가시나 (Gashina)
                song_name = song.song_name[:song.song_name.find("(")].strip()
            else:
                song_name = song.song_name

            # 区分是否可播放
            if not song.is_playable:
                singer_name = " ".join([singer.name for singer in song.singer])
                num = 1
                if url_parsed.netloc == NETLOC_163:
                    songs = await qqm_client.search(key_words=f'{song_name} {singer_name}', number=num)
                else:
                    songs = await nem_client.search(key_words=f'{song_name} {singer_name}', number=num)

                if songs:
                    pl.songs[index] = songs[0]

        self.render("playlist.html", playlist=pl)
        return

    async def prepare_url(self, pl_url):

        pl_url = pl_url.strip()

        # prepare url
        if NETLOC_163 in pl_url:
            if "分享" in pl_url:
                try:
                    pl_url = pl_url.split()[0].split('》')[1]
                except Exception as e:
                    logging.error(e)
                    pl_url = None
                    # self.render("songs.html", qqm_songs=[], nem_songs=[])
                    # return
            else:
                pass
        elif NETLOC_QQ in pl_url:
            # https://y.qq.com/n/yqq/playlist/3802473507.html#stat=y_new.profile.create_playlist.click&dirid=1
            pl_url_split = pl_url.split("#")
            pl_url = None
            for split in pl_url_split:
                if NETLOC_QQ in split:
                    pl_url = split
        else:
            head_res = await async_request.head(pl_url)
            pl_url = getattr(head_res, 'effective_url', None)

        return pl_url

    async def parse_qq_pl(self, url_parsed):
        if 'n/yqq/playlist' in url_parsed.path:
            # y.qq.com/n/yqq/playlist/3802473507.html
            # ParseResult(scheme='https', netloc='y.qq.com', path='/n/yqq/playlist/3802473507.html', params='', query='', fragment='')
            pl_id = int(url_parsed.path.split('.html')[0].split('playlist/')[1])
            try:
                songs = await qqm_client.playlist(pl_id=pl_id)
            except Exception as e:
                return False, e
            else:
                return True, songs
        elif 'n/yqq/album' in url_parsed.path:
            # https://y.qq.com/n/yqq/album/0024bjiL2aocxT.html
            album_id = url_parsed.path.split('.html')[0].split('album/')[1]
            try:
                songs = await qqm_client.album_details(album_media_id=album_id)
            except Exception as e:
                return False, e
            else:
                return True, songs
        elif 'taoge' in url_parsed.path:
            # http://url.cn/55TSszn
            # https://y.qq.com/w/taoge.html?id=3802473507
            params = dict(parse_qsl(url_parsed.query))
            pl_id = params.get("id")
            if not pl_id:
                return False, "no id of the play list"
            # pl_id = int(url_parsed.path.split('.html')[0].split('playlist/')[1])
            try:
                songs = await qqm_client.playlist(pl_id=pl_id)
            except Exception as e:
                return False, e
            else:
                return True, songs
        else:
            return False, f"Wrong path {url_parsed.path}"

    async def parse_163_pl(self, url_parsed):
        path = url_parsed.path.split('/')
        if len(path) is 4 and path[2].isdigit():
            # http://music.163.com/playlist/751385113/46154092?userid=46154092
            pl_id = int(path[2])
        elif url_parsed.path == '/' and "playlist?id=" in url_parsed.fragment:
            # https://music.163.com/#/playlist?id=2521554648
            url_parsed_question = url_parsed.fragment.split('?id=')
            if len(url_parsed_question) == 2 and url_parsed_question[1].isdigit():
                pl_id = int(url_parsed_question[1])
            else:
                return False, Exception("Wrong NEM share url.")
        elif "my/m/music/" in url_parsed.fragment:
            # https://music.163.com/#/my/m/music/playlist?id=40928655
            try:
                pl_id = parse_qs(url_parsed.fragment.split("?")[1]).get('id')[0]
            except Exception as e:
                return False, e
        else:
            return False, Exception("Url not supported.")

        songs = await nem_client.playlist(pl_id)
        return True, songs
