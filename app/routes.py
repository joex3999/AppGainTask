from app import app
from flask import render_template,request,jsonify
import pymongo
import string
import random
from pymongo import MongoClient
from functools import wraps
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
    shortlinks = db.shortlinks
    output = []
    for link in  shortlinks.find():
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

    shortlinks = db.shortlinks
    ios = request.json['ios']
    android=request.json['android']
    web=request.json['web']
    linkWithSameSlug = shortlinks.find_one({'slug':slug})

    if(linkWithSameSlug):
        response= jsonify({'status':'failed','message':'slug is already in use'})
        response.status_code=400
        return response
    id_ = shortlinks.insert({'slug':slug,'ios':ios,'android':android,'web':web})
    response= jsonify({'status':'successful','slug':slug,'message':'created successfuly'})
    response.status_code=201
    return response;

@app.route('/shortlinks/<slug>',methods=['PUT'])
@validateHeader
def put(slug):

    shortlinks = db.shortlinks
    linkWithSameSlug = shortlinks.find_one({'slug':slug})
    if(not linkWithSameSlug):
        response= jsonify({'status':'failed','message':'There is no link with this slug.'})
        response.status_code=400
        return response
    ios = linkWithSameSlug['ios']
    android=linkWithSameSlug['android']

    web = request.json['web'] if 'web' in request.json else linkWithSameSlug['web']
    ios['fallback'] = request.json['ios']['fallback'] if 'ios' in request.json and 'fallback' in request.json['ios'] else ios['fallback']
    ios['primary'] = request.json['ios']['primary'] if 'ios' in request.json and 'primary' in request.json['ios'] else ios['primary']
    android['fallback'] = request.json['android']['fallback'] if 'android' in request.json and 'fallback' in request.json['android'] else android ['fallback']
    android['primary'] = request.json['android']['primary'] if 'android' in request.json and 'primary' in request.json['android'] else android['primary']

    shortlinks.update_one(
      { "slug" : slug },
      { "$set": {"web" : web, "ios" : ios,    "android":android } }
   );

    response= jsonify({'status':'successful','message':'updated successfuly'})
    response.status_code=201
    return response
