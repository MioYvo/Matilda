# coding=utf-8
# __author__ = 'Mio'
# from os import getenv

# --------------------     mongo     --------------------

# from mongoengine import register_connection
#
# MONGO_DB_ALIAS = getenv("MONGO_DB_ALIAS", "matilda")
# MONGO_DB_NAME = getenv("MONGO_DB_NAME", "matilda")
# alias_db = {
#     MONGO_DB_ALIAS: MONGO_DB_NAME
# }
#
# MONGO_HOST = getenv("MONGO_HOST", "mongo")
# MONGO_PORT = int(getenv("MONGO_PORT", "27017"))
#
# NUM_OF_SONGS_SEARCH = int(getenv("NUM_OF_SONGS_SEARCH", 5))
#
#
# def register_db():
#     for alias, db in alias_db.items():
#         register_connection(alias=alias, name=db, host=MONGO_HOST, port=MONGO_PORT)
