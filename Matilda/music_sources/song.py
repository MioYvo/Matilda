# coding=utf-8
# __author__ = 'Mio'
from collections import namedtuple
from typing import List

Album = namedtuple("Album", ['id', 'mid', 'name', 'pic_url'])
Singer = namedtuple("Singer", ['id', 'mid', 'name'])


class Playlist(object):
    def __init__(self, name, songs, cover_img_url):
        self.name = name
        self.songs = songs
        self.cover_img_url = cover_img_url

    def to_dict(self):
        return dict(
            name=self.name,
            cover_img_url=self.cover_img_url,
            songs=[s.to_dict() for s in self.songs]
        )


class Song(object):
    def __init__(self, song_name: str, song_id: int, song_mid: str, song_media_url: str, lyric: str, album: Album,
                 singer: List[Singer], is_playable: bool):
        """
        QQ Song
        :param song_name:
        :param song_id:
        :param song_mid:
        :param song_media_url:
        :param singer: List
        """
        self.song_id = song_id
        self.song_name = song_name
        self.song_mid = song_mid
        self.song_media_url = song_media_url

        self.lyric = lyric
        self.album = album
        self.singer = singer
        self.is_playable = is_playable

    def __str__(self):
        return f"QQMusic Song {self.song_name}"

    def __repr__(self):
        return self.__str__()

    @property
    def papa(self):
        raise NotImplementedError

    def to_dict(self):
        d = self.__dict__
        d['papa'] = self.papa
        d['album'] = dict(self.album._asdict())
        d['singer'] = [dict(s._asdict()) for s in self.singer]
        return d
