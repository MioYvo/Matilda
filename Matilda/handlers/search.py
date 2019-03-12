# coding=utf-8
# __author__ = 'Mio'
from Matilda.utils.web import BaseRequestHandler
from Matilda.settings import NUM_OF_SONGS_SEARCH
from Matilda.music_sources import qqm_client, nem_client


async def _get(kw):
    num = NUM_OF_SONGS_SEARCH
    qqm_songs = await qqm_client.search(key_words=kw, number=num)
    nem_songs = await nem_client.search(key_words=kw, number=num)

    return qqm_songs, nem_songs


class SearchSongs(BaseRequestHandler):
    async def get(self):
        kw = self.get_query_argument('kw', default=None)
        if not kw:
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        qqm_songs, nem_songs = await _get(kw)
        self.render("songs.html", qqm_songs=qqm_songs, nem_songs=nem_songs)


class SearchSongsAPI(BaseRequestHandler):
    async def get(self):
        kw = self.get_query_argument('kw', default=None)
        if not kw:
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        qqm_songs, nem_songs = await _get(kw)
        self.write_response(
            {
                "qqm_songs": [s.to_dict() for s in qqm_songs],
                "nem_songs": [s.to_dict() for s in nem_songs]
            }
        )
