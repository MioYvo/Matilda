# Matilda
A gift from Matilda.


## Playlist
Supported url forms:
* `https://music.163.com/#/playlist?id=167149096`
* `https://y.qq.com/n/yqq/playlist/3802473507.html`
* `https://y.qq.com/n/yqq/album/0024bjiL2aocxT.html`
* `http://url.cn/55TSszn` --> `https://y.qq.com/w/taoge.html?id=3802473507`


## Run

```commandline
python app.py --port=9000 --debug=True
```

Or

```commandline
docker run -itd -p 9090:9090 --name matilda ccr.ccs.tencentyun.com/mioo/matilda
```