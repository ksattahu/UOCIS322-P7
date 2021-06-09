"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request, abort, render_template, jsonify, redirect, url_for
import os
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
from pymongo import MongoClient
import logging
from db import db_insert, db_find
from json import loads
###
# Globals
###

app = flask.Flask(__name__)
CONFIG = config.configuration()

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


@app.errorhandler(400)
def submit_error(error):
    app.logger.debug("Bad Request")
    return flask.render_template('400.html'), 400

@app.errorhandler(503)
def display_error(error):
    app.logger.debug("Service Unavailable")
    return flask.render_template('503.html'), 503

@app.route("/_display")
def display():
    app.logger.debug("Display.html")
    found, vals = db_find()
    if found:
        return flask.render_template('display.html', vals=vals)
    else:
        return flask.render_template('400.html')

@app.route("/_submit", methods=['POST'])
def insert():
    vals = loads(request.form.get("vals", type=str))
    app.logger.debug(vals)
    ret = "Fill out table properly to submit into database."
    if(db_insert(vals)):
        ret = "Entries submitted into database."
    out = {
            "ret": ret
          }
    return flask.jsonify(out)

###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', 999, type=int)
    begin_date = request.args.get('begin_date', type=str)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    begin_date = arrow.get(begin_date, "YYYY-MM-DDTHH:mm").shift(hours=8)
    # FIXME!
    # Right now, only the current time is passed as the start time
    # and control distance is fixed to 200
    # You should get these from the webpage!
    open_time = acp_times.open_time(km, brevet_dist_km, begin_date) #arrow.now().isoformat).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet_dist_km, begin_date) #arrow.now().isoformat).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time.isoformat().format('YYYY-MM-DDTHH:mm'), "close": close_time.isoformat().format('YYYY-MM-DDTHH:mm')}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
