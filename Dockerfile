FROM mio101/py3-alpine-build-base
#FROM python:3-alpine3.7
COPY . /app

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk --no-cache add tzdata && \
    # change timezone to Asia/Shanghai
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    # install app
    pip3 install --no-cache-dir -i https://pypi.douban.com/simple/ -r /app/requirements.txt && \
    # do clean
    apk del --no-cache tzdata

WORKDIR /app/
CMD ["python", "app.py", "--port=9090"]
