from mongoframes import *
from pymongo import MongoClient
Frame._client = MongoClient('mongodb://localhost:27017/mydb')

class Shortlinks(Frame):
    _fields = {
        'slug',
        'ios',
        'android',
        'web'
    }

class ios(SubFrame):

    _fields = {
        'primary',
        'fallback'
        }

class android(SubFrame):

    _fields = {
        'primary',
        'fallback'
        }
