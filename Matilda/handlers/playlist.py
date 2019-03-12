# coding=utf-8
# __author__ = 'Mio'
import logging

from Matilda.music_sources.nem.playlist import PlayListParser
from Matilda.utils.web import BaseRequestHandler


class PlayList(BaseRequestHandler):
    def get(self):
        self.render("search_playlist.html")


class ImportPlayList(BaseRequestHandler):
    async def get(self):
        """
        QQM: id 2894607664 in "http://url.cn/55TSszn" --> https://y.qq.com/w/taoge.html?id=2894607664
        NEM: id 751385113 in "分享mio刘的歌单《陈粒》http://music.163.com/playlist/751385113/46154092?userid=46154092 (@网易云音乐)"
        :return:
        """
        pl_url = self.get_query_argument("pl", None)
        if not pl_url:
            # TODO Error Page
            logging.error('no pl_url')
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        rst, data = await PlayListParser.parse(pl_url=pl_url)
        if rst is True:
            self.render("playlist.html", playlist=data)
        else:
            logging.error(data)
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return


class ImportPlayListAPI(BaseRequestHandler):
    async def get(self):
        pl_url = self.get_query_argument("pl", None)
        if not pl_url:
            logging.error('wrong pl_url')
            self.write_error_response('wrong pl_url')
            return

        rst, data = await PlayListParser.parse(pl_url=pl_url)
        if rst is True:
            self.write_response(data)
            return
        else:
            logging.error(data)
            self.write_error_response(data)
            return
