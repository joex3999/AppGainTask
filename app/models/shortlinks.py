from mongoframes import *
from pymongo import MongoClient
Frame._client = MongoClient('mongodb://localhost:27017/testdb')
class Shortlink(Frame):

    _fields = {
        'slug',
        'ios',
        'android',
        'web'
    }

class Ios(SubFrame):

    _fields = {
        'primary',
        'fallback'
        }

class Android(SubFrame):

    _fields = {
        'primary',
        'fallback'
        }
