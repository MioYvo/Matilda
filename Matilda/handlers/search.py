# coding=utf-8
# __author__ = 'Mio'
from Matilda.music_sources import qqm_client, nem_client
from Matilda.utils.web import BaseRequestHandler


class SearchSongs(BaseRequestHandler):
    async def get(self):
        kw = self.get_query_argument('kw', default=None)
        if not kw:
            self.render("songs.html", qqm_songs=[], nem_songs=[])
            return

        num = 5
        qqm_songs = await qqm_client.search(key_words=kw, number=num)
        nem_songs = await nem_client.search(key_words=kw, number=num)
        # if qqm_songs and qqm_songs[0].is_playable:
        #     songs = qqm_songs + nem_songs
        # else:
        #     songs = nem_songs + qqm_songs

        # self.write_response([song.to_dict() for song in songs])
        self.render("songs.html", qqm_songs=qqm_songs, nem_songs=nem_songs)
