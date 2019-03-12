# Matilda
A gift from Matilda.


## 歌单
支持的歌单分享url形式:

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
docker run -itd -p 9090:9090 --name matilda registry.cn-hangzhou.aliyuncs.com/mio101/matilda:latest
```

## TODO
1. 前端
    1. h5播放器
    2. 响应式布局，支持手机
1. 提高运行速度（Rust?）
2. 用户系统
    1. 登录
    2. 导入、同步歌单
    3. 创建歌单
3. 热门

## API
> [Postman](https://www.getpostman.com)

Sharing collection:

`https://www.getpostman.com/collections/1cb7a54448f6a28d726f`