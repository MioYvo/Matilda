# coding=utf-8
# __author__ = 'Mio'
import logging

from Matilda.utils import async_request
from Matilda.utils.web import BaseRequestHandler
from Matilda.music_sources import qqm_client, nem_client
from tornado.httputil import urlparse, parse_qsl

NETLOC_163 = "music.163.com"
NETLOC_QQ = "y.qq.com"


class PlayList(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render("search_playlist.html")


class ImportPlayList(BaseRequestHandler):
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

        pl_url = pl_url.strip()

        if NETLOC_163 in pl_url:
            try:
                pl_url = pl_url.split()[0].split('》')[1]
            except Exception as e:
                logging.error(e)
                self.render("songs.html", qqm_songs=[], nem_songs=[])
                return
        else:
            head_res = await async_request.head(pl_url)
            pl_url = getattr(head_res, 'effective_url', None)

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
            logging.error("no pl_rst")
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        not_playable_songs = []
        playable_songs = []
        for song in pl.songs:
            if song.is_playable:
                playable_songs.append(song)
            else:
                not_playable_songs.append(song)

        tried_replace_songs = {}
        num = 1
        for song in not_playable_songs:
            # 가시나 (Gashina)
            if song.song_name.find("("):
                song_name = song.song_name[:song.song_name.find("(")].strip()
            else:
                song_name = song.song_name

            if url_parsed.netloc == NETLOC_163:
                songs = await qqm_client.search(key_words=song_name + " ".join((singer.name for singer in song.singer)), number=num)
            else:
                songs = await nem_client.search(key_words=f'{song_name} {" ".join((singer.name for singer in song.singer))}', number=num)

            if songs:
                tried_replace_songs[song.song_name] = songs[0]
            else:
                tried_replace_songs[song.song_name] = song

        pl.songs = playable_songs + not_playable_songs
        self.render("playlist.html", playlist=pl, tried_replace_songs=list(tried_replace_songs.values()))
        return

    async def parse_qq_pl(self, url_parsed):

        params = dict(parse_qsl(url_parsed.query))
        if not params:
            return False, "no params"

        pl_id = params.get("id", None)
        if not pl_id:
            return False, "no id of the play list"

        try:
            songs = await qqm_client.playlist(pl_id=pl_id)
        except Exception as e:
            return False, e
        else:
            return True, songs

    async def parse_163_pl(self, url_parsed):
        path = url_parsed.path.split('/')  # '/playlist/751385113/46154092'
        try:
            pl_id = int(path[2])
            songs = await nem_client.playlist(pl_id)
        except Exception as e:
            logging.error(e)
            return False, e
        else:
            return True, songs
