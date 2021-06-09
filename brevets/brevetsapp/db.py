import flask
#from flask import request, abort, render_template, jsonify
import os
#import arrow  # Replacement for datetime, based on moment.js
#import acp_times  # Brevet time calculations
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetsdb


def db_find():
    vals = list(db.vals.find())
    if len(vals) == 0:
        return False, False
    return True, vals

def db_insert(vals):
    ret = False
    if vals:
        db.vals.drop()
        for row in vals:
            db.vals.insert_one(row)
        ret = True
    return ret
