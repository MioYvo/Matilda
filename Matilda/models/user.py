# coding=utf-8
# __author__ = 'Mio'

from mongoengine.fields import StringField

from Matilda.settings import MONGO_DB_NAME
from Matilda.utils.gmongoengine import BaseDocument


class User(BaseDocument):
    """
    用户
    """
    nick_name = StringField(max_length=20, null=False, required=True, help_text="昵称")
    name = StringField(max_length=20, null=False, required=True, help_text="用户名")
    password = StringField(null=False, required=True, help_text="密码")

    meta = {
        "collection": "ds_special_config",
        "alias_db": MONGO_DB_NAME,
        "ordering": [
            "-create_time"
        ],
        "indexes": [
            "name"
        ],
    }

