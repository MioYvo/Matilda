# coding=utf-8
# __author__ = 'Mio'

# --------------------     mongo     --------------------
from os import getenv

from mongoengine import register_connection

MONGO_DB_ALIAS = getenv("MONGO_DB_ALIAS", "matilda")
MONGO_DB_NAME = getenv("MONGO_DB_NAME", "matilda")
alias_db = {
    MONGO_DB_ALIAS: MONGO_DB_NAME
}

MONGO_HOST = getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(getenv("MONGO_PORT", "27017"))


def register_db():
    for alias, db in alias_db.items():
        register_connection(alias=alias, name=db, host=MONGO_HOST, port=MONGO_PORT)
