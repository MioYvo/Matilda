# coding=utf-8
# __author__ = 'Mio'

from music_sources import qqm_client, nem_client
from utils.web import BaseRequestHandler


class HomeHandler(BaseRequestHandler):
    def get(self):
        self.render("home.html")


