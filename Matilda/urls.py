# coding=utf-8
# __author__ = 'Mio'
from Matilda.handlers.index import HomeHandler
from Matilda.handlers.search import SearchSongs, SearchSongsAPI
from Matilda.handlers.playlist import ImportPlayList, PlayList, ImportPlayListAPI

urls = [
    (r"/", HomeHandler),
    (r"/search", SearchSongs),
    (r"/playlist", ImportPlayList),
    (r"/search_playlist", PlayList),
]

# API v1
urls += [
    (r"/api/v1/search", SearchSongsAPI),
    (r"/api/v1/import_playlist", ImportPlayListAPI),
]
