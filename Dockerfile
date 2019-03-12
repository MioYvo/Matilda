FROM python:alpine
#FROM mio101/py3-alpine-build-base
COPY . /app

# install app
RUN apk add --no-cache --virtual .build build-base && \
    # <requirements>
    pip3 install --no-cache-dir -r /app/requirements.txt && \
    apk del .build

WORKDIR /app/
CMD ["python", "app.py", "--port=9090"]
