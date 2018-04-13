# coding=utf-8
# __author__ = 'Mio'
import logging
import os.path

import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

from urls import urls

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


def main():
    parse_command_line()
    app = tornado.web.Application(
        handlers=urls,
        # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        # xsrf_cookies=True,
        debug=options.debug,
        blog_title="音乐墨盒",
    )
    app.listen(options.port)
    logging.info(f"app run on {options.port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
