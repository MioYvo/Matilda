# coding=utf-8
# __author__ = 'Mio'
"""
API for NetEaseMusic, from https://github.com/darknessomi/musicbox, thanks the greate work
"""

import os
import json
import base64
import hashlib
import random
import binascii
from typing import List

from Crypto.Cipher import AES

from Matilda.music_sources.song import Song, Album, Singer, Playlist
from Matilda.utils import async_request
from Matilda.utils.async_request import parse_body2json

modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

SEARCH_URL = "http://music.163.com/api/search/get"
SONG_DETAILS_URL = "http://music.163.com/api/song/detail"
PLAYLIST_URL = "http://music.163.com/weapi/v3/playlist/detail"


# 登录加密算法, 基于https://github.com/stkevintan/nw_musicbox脚本实现
def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {'params': encText, 'encSecKey': encSecKey}
    return data


def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext


def rsaEncrypt(text, _pubKey, _modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(_pubKey, 16), int(_modulus, 16))
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return binascii.hexlify(os.urandom(size))[:16]


class NSong(Song):
    def __str__(self):
        return f"NetEaseMusic Song {self.song_name}"

    @property
    def papa(self):
        return 'NetEaseMusic'


class NetEaseMusic(object):
    def __init__(self):
        self.req = async_request

    async def search(self, key_words: str, page=1, number=5) -> List[NSong]:
        data = {
            "s": str(key_words),
            "type": 1,
            "offset": (page - 1) * number,
            "total": "true",
            "limit": number,
        }
        res = await self.req.post(
            url=SEARCH_URL, data=data,
            # headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        search_rst = parse_body2json(res)
        rst = []
        # print(search_rst)
        if search_rst['result']['songCount'] > 0 and search_rst['result'].get('songs'):
            songs_ids = [song['id'] for song in search_rst['result']['songs']]
            songs_detail = await self.song_details(songs_ids)
            songs_url_detail = await self.songs_detail_new_api(songs_ids)
            songs_url_detail_map = {s['id']: s['url'] for s in songs_url_detail}
            for song in songs_detail:
                song['url'] = songs_url_detail_map.get(song['id'], None)
                rst.append(self.make_song(song))

        return rst

    async def song_details(self, song_ids: List[int]) -> dict:
        params = {
            "ids": song_ids
        }
        res = await self.req.get(url=SONG_DETAILS_URL, params=params)
        rst = parse_body2json(res)
        return rst['songs']

    async def songs_detail_new_api(self, song_ids, bit_rate=320000):
        action = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        # self.session.cookies.load()
        csrf = ''
        # for cookie in self.session.cookies:
        #     if cookie.name == '__csrf':
        #         csrf = cookie.value
        # if csrf == '':
        #     notify('You Need Login', 1)
        action += csrf
        data = {'ids': song_ids, 'br': bit_rate, 'csrf_token': csrf}
        res = await self.req.post(url=action,
                                  data=encrypted_request(data),
                                  # headers=self.header,
                                  )
        result = parse_body2json(res)
        return result['data']

    def encrypted_id(self, _id):
        magic = bytearray('3go8&$8*3*3h0k(2)2', 'u8')
        song_id = bytearray(_id, 'u8')
        magic_len = len(magic)
        for i, sid in enumerate(song_id):
            song_id[i] = sid ^ magic[i % magic_len]
        m = hashlib.md5(song_id)
        result = m.digest()
        result = base64.b64encode(result)
        result = result.replace(b'/', b'_')
        result = result.replace(b'+', b'-')
        return result.decode('utf-8')

    def geturl_v3(self, song):
        # quality = Config().get_item('music_quality')
        quality = 0
        if song['h'] and quality <= 0:
            music = song['h']
            quality = 'HD'
        elif song['m'] and quality <= 1:
            music = song['m']
            quality = 'MD'
        elif song['l'] and quality <= 2:
            music = song['l']
            quality = 'LD'
        else:
            return song.get('mp3Url', ''), ''

        quality = quality + ' {0}k'.format(music['br'] // 1000)
        song_id = str(music['fid'])
        enc_id = self.encrypted_id(song_id)
        url = f'http://m{random.randrange(1, 3)}s.music.126.net/{enc_id}/{song_id}.mp3'
        return url, quality

    def make_song(self, song):
        return NSong(
            song_name=song['name'],
            song_id=song['id'],
            song_mid=song['id'],
            song_media_url=song['url'],
            lyric="",
            album=Album(
                id=song['album']['id'],
                mid=song['album']['id'],
                name=song['album']['name'],
                pic_url=song['album']['picUrl']
            ),
            singer=[
                Singer(
                    id=singer['id'],
                    mid=singer['id'],
                    name=singer['name'],
                )
                for singer in song['artists']
            ],
            is_playable=True if song['url'] else False
        )

    async def playlist(self, playlist_id):
        csrf = ''
        data = {'id': playlist_id, 'total': 'true', 'csrf_token': csrf, 'limit': 1000, 'n': 1000, 'offset': 0}
        res = await self.req.post(PLAYLIST_URL,
                                  data=encrypted_request(data),
                                  # headers=self.header, )
                                  )
        result = parse_body2json(res)

        simple_songs = result['playlist']['tracks']
        songs_ids = [x['id'] for x in result['playlist']['trackIds']]

        songs_url_detail = await self.songs_detail_new_api(list(songs_ids))
        songs_url_detail_map = {s['id']: s['url'] for s in songs_url_detail}

        songs = [NSong(
            song_name=song['name'],
            song_id=song['id'], song_mid=song['id'],
            song_media_url=songs_url_detail_map.get(song['id'], ''),
            lyric="",
            album=Album(
                id=song['al']['id'],
                mid=song['al']['id'],
                name=song['al']['name'],
                pic_url=song['al']['picUrl']
            ),
            singer=[
                Singer(
                    id=singer['id'],
                    mid=singer['id'],
                    name=singer['name'],
                )
                for singer in song['ar']
            ],
            is_playable=True if songs_url_detail_map.get(song['id']) else False
        ) for song in simple_songs]
        return Playlist(name=result['playlist']['name'], songs=songs, cover_img_url=result['playlist']['coverImgUrl'])


if __name__ == '__main__':
    client = NetEaseMusic()
    import asyncio

    loop = asyncio.get_event_loop()
    # loop.run_until_complete(client.search("周杰伦"))
    loop.run_until_complete(client.playlist(751385113))
