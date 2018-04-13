# coding=utf-8
# __author__ = 'Mio'
from Matilda.handlers.index import HomeHandler
# from Matilda.handlers import SearchSongs
from Matilda.handlers.search import SearchSongs

urls = [
    (r"/", HomeHandler),
    (r"/search", SearchSongs),
]
