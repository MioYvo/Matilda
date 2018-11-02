#FROM python:3-slim
FROM mio101/py3-alpine-build-base
COPY . /app

# install app
RUN pip3 install --no-cache-dir -i https://pypi.douban.com/simple/ -r /app/requirements.txt

WORKDIR /app/
CMD ["python", "app.py", "--port=9090"]
