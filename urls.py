# coding=utf-8
# __author__ = 'Mio'
from handlers.index import HomeHandler
from handlers.search import SearchSongs

urls = [
    (r"/", HomeHandler),
    (r"/search", SearchSongs),
]
