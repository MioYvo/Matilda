# coding=utf-8
# __author__ = 'Mio'

from Matilda.utils.web import BaseRequestHandler


class HomeHandler(BaseRequestHandler):
    def get(self):
        self.render("home.html")


