# coding=utf-8
# __author__ = 'Mio'
import logging
import os.path
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

from Matilda.urls import urls

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class MatildaApp(tornado.web.Application):
    def __init__(self):
        super(MatildaApp, self).__init__(
            handlers=urls,
            # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            # xsrf_cookies=True,
            template_path=os.path.join(os.path.dirname(__file__), "Matilda/templates"),
            static_path=os.path.join(os.path.dirname(__file__), "Matilda/static"),
            debug=options.debug,
            blog_title="Matilda",
        )


def main():
    parse_command_line()
    app = MatildaApp()
    app.listen(options.port)
    logging.info(f"app run on {options.port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
