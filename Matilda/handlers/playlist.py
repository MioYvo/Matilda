# coding=utf-8
# __author__ = 'Mio'

from Matilda.utils.web import BaseRequestHandler
from Matilda.music_sources import qqm_client
from tornado.httputil import urlparse, parse_qsl

NETLOC_163 = "music.163.com"
NETLOC_QQ = "y.qq.com"


class ImportPlayList(BaseRequestHandler):
    def get(self, *args, **kwargs):
        """
        https://y.qq.com/w/taoge.html?hostuin=1152921504613445457&id=2894607664&appshare=iphone_wx&from=singlemessage&isappinstalled=0
        http://music.163.com/playlist/40928655/46154092?userid=46154092
        :param args:
        :param kwargs:
        :return:
        """
        pl_url = self.get_query_argument("pl", None)
        if not pl_url:
            # TODO Error Page
            self.render("search.html", songs=[])
            return

            # parse the url
        url_parsed = urlparse(pl_url.strip())
        if url_parsed.netloc not in (NETLOC_163, NETLOC_QQ):
            # TODO Error Page
            self.render("search.html", songs=[])
            return

        # TODO get user's info and play list info

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
            return False, e.args
        else:
            self.render("songs.html", songs=songs)

    def parse_163_pl(self, url_parsed):
        pass
