# coding=utf-8
# __author__ = 'Mio'
from Matilda.handlers.index import HomeHandler
from Matilda.handlers.search import SearchSongs
from Matilda.handlers.playlist import ImportPlayList, PlayList

urls = [
    (r"/", HomeHandler),
    (r"/search", SearchSongs),
    (r"/playlist", ImportPlayList),
    (r"/search_playlist", PlayList),
]
