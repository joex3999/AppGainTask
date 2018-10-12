import pytest
import json
from flask import Flask
from app import app
from app.models.shortlinks import *
from pymongo import MongoClient
from mongoframes import *
client = MongoClient('mongodb://localhost:27017/testdb')
db = client['testdb']

@pytest.fixture(scope='module')
def test_client():
    app.config.from_pyfile('flask_test.cfg')
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield testing_client  # this is where the testing happens!
    ctx.pop()

@pytest.fixture(scope='module')
def new_shortlink():
    shortlink = Shortlink(
        slug='SggGG2134',
        ios= {"primary":"http://...","fallback":"http://..."},
        android={"primary":"http://..","fallback":"http://..."},
        web='http://...'
    )
    return shortlink



def test_get_shortlinks_unauthenticated(test_client):
    #response = test_client.get('/shortlinks/',headers={'Content-Type':'application/json'})
    response = test_client.get('/shortlinks/')
    assert response.status_code==400
    assert b"Bad Request" in response.data

def test_post_shortlink_unauthenticated(test_client):
        #response = test_client.get('/shortlinks/',headers={'Content-Type':'application/json'})
        response = test_client.post('/shortlinks/')
        assert response.status_code==400
        assert b"Bad Request" in response.data

def test_put_shortlink_unauthenticated(test_client):
    #response = test_client.get('/shortlinks/',headers={'Content-Type':'application/json'})
    response = test_client.put('/shortlinks/anySlug')
    assert response.status_code==400
    assert b"Bad Request" in response.data

def test_get_shortlinks(new_shortlink,test_client):
        new_shortlink.insert()
        response = test_client.get('/shortlinks/',headers={'Content-Type':'application/json'})
        assert response.status_code==200
        assert bytes(new_shortlink.slug, 'utf-8') in response.data
        assert bytes(new_shortlink.ios['primary'], 'utf-8') in response.data
        assert bytes(new_shortlink.android['primary'], 'utf-8') in response.data
        assert bytes(new_shortlink.ios['fallback'], 'utf-8') in response.data
        assert bytes(new_shortlink.android['fallback'], 'utf-8') in response.data
        assert bytes(new_shortlink.web, 'utf-8') in response.data

def test_post_shortlink(new_shortlink,test_client):
        db.Shortlink.delete_many({})
        data={
                "slug":new_shortlink.slug,
                "ios": {
                "primary": new_shortlink.ios['primary'],
                "fallback": new_shortlink.ios['fallback']
                },
                "android": {
                "primary": new_shortlink.android['primary'],
                "fallback": new_shortlink.android['fallback'],
                },
                "web": new_shortlink.web
                }
        response = test_client.post('/shortlinks/',data=json.dumps(data),headers={'Content-Type':'application/json'})
        assert response.status_code==201
        assert "successful" == response.json['status']
        assert "created successfuly" == response.json['message']

        link = Shortlink.one(Q.slug==data['slug'],projection={'ios': {'$sub': Ios},'android': {'$sub': Android}})
        assert link.ios.primary==data['ios']['primary']
        assert link.ios.fallback==data['ios']['fallback']
        assert link.web ==data['web']
        assert link.android.primary==data['android']['primary']
        assert link.android.fallback ==data['android']['fallback']


def test_post_shortlink_used_slug(new_shortlink,test_client):
        db.Shortlink.delete_many({})
        new_shortlink.insert()
        data={
                "slug":new_shortlink.slug,
                "ios": {
                "primary": new_shortlink.ios['primary'],
                "fallback": new_shortlink.ios['fallback']
                },
                "android": {
                "primary": new_shortlink.android['primary'],
                "fallback": new_shortlink.android['fallback'],
                },
                "web": new_shortlink.web
                }
        response = test_client.post('/shortlinks/',data=json.dumps(data),headers={'Content-Type':'application/json'})
        assert response.status_code == 400
        assert 'failed'==response.json['status']
        assert 'slug is already in use'==response.json['message']

def test_put_shortlink(new_shortlink,test_client):
        db.Shortlink.delete_many({})
        new_shortlink.insert()
        data={
                "ios": {
                "fallback": 'http://new'
                },
                "android": {
                "primary": "http://new",
                }
                }
        response = test_client.put('/shortlinks/'+new_shortlink.slug,data=json.dumps(data),headers={'Content-Type':'application/json'})
        assert response.status_code==201
        assert "successful" == response.json['status']
        assert "updated successfuly" == response.json['message']
def test_put_shortlink_nonexistant_slug(new_shortlink,test_client):
        db.Shortlink.delete_many({})
        data={
                "ios": {
                "fallback": 'http://new'
                },
                "android": {
                "primary": "http://new",
                }
                }
        response = test_client.put('/shortlinks/NonExistantSlug',data=json.dumps(data),headers={'Content-Type':'application/json'})
        assert response.status_code==400
        assert "failed" == response.json['status']
        assert "There is no link with this slug." == response.json['message']
