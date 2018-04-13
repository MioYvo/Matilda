FROM mio101/py3-alpine-build-base
COPY . /app

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk --no-cache add tzdata && \
    # change timezone to Asia/Shanghai
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    # install app
    pip install --no-cache-dir -i https://pypi.douban.com/simple/ -r /app/requirements.txt && \
    # do clean
    apk del --no-cache tzdata build-base

WORKDIR /app/
CMD ["python", "app.py", "--port=9090"]
