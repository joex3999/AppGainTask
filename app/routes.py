from app import app
from app.models.shortlinks import *
from flask import render_template,request,jsonify
from pymongo import MongoClient
from functools import wraps
from mongoframes import *
import pymongo
import string
import random


app.config['MONGO_DBNAME'] = 'testdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/testdb'
client = MongoClient(app.config['MONGO_URI'])
db = client.app.config['MONGO_DBNAME']

def generateSlug():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def validateHeader(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if not request.content_type == 'application/json':
            response = jsonify({'status' : 'failed', 'message' : 'Bad Request'})
            response.status_code=401
            return response
        return func(*args, **kwargs)
    return func_wrapper

@app.route('/shortlinks/',methods=['GET'])
@validateHeader
def get_all_links():

    for link in  Shortlink.many():
        output.append({'slug':link['slug'],'ios':link['ios'],'android':link['android'],'web':link['web']})
    response = jsonify(output)
    response.status_code=200
    return response


@app.route('/shortlinks/',methods=['POST'])
@validateHeader
def add_new_link():


    if(not('ios' in request.json and 'android' in request.json and 'web' in request.json)):
        response= jsonify({'status':'failed','message':'ios, android, and web fields has to be present.'})
        response.status_code=400
        return response

    if(not('slug' in request.json)):
        slug = generateSlug()
    else: slug = request.json['slug']

    shortlink = Shortlink(
        slug=slug,
        ios= request.json['ios'],
        android=request.json['android'],
        web=request.json['web']
    )

    linkWithSameSlug = Shortlink.one(Q.slug==slug)

    if(linkWithSameSlug):
        response= jsonify({'status':'failed','message':'slug is already in use'})
        response.status_code=400
        return response

    shortlink.insert()

    response= jsonify({'status':'successful','slug':slug,'message':'created successfuly'})
    response.status_code=201
    return response;

@app.route('/shortlinks/<slug>',methods=['PUT'])
@validateHeader
def put(slug):

    shortlink = Shortlink.one(Q.slug==slug,projection={'ios': {'$sub': Ios},'android': {'$sub': Android}})
    if(not shortlink):
        response= jsonify({'status':'failed','message':'There is no link with this slug.'})
        response.status_code=400
        return response


    shortlink.web = request.json['web'] if 'web' in request.json else shortlink.web
    shortlink.ios.fallback= request.json['ios']['fallback'] if 'ios' in request.json and 'fallback' in request.json['ios'] else shortlink.ios.fallback
    shortlink.ios.primary= request.json['ios']['primary'] if 'ios' in request.json and 'primary' in request.json['ios'] else shortlink.ios.primary
    shortlink.android.fallback = request.json['android']['fallback'] if 'android' in request.json and 'fallback' in request.json['android'] else shortink.android.fallback
    shortlink.android.primary= request.json['android']['primary'] if 'android' in request.json and 'primary' in request.json['android'] else shortink.android.primary

    shortlink.update()

    response= jsonify({'status':'successful','message':'updated successfuly'})
    response.status_code=201
    return response
