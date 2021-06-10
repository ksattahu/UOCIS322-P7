# UOCIS322 - Project 7 #

Brevet time calculator with MongoDB and RESTful api, with login functionality!

## Author: Kale Satta-Hutton, ksattahu@uoregon.edu ##

## Overview

Implementation of the RUSA ACP controle time calculator with Flask and AJAX,
Flask-WTForms, Flask-Login, and flak_RESTful with python MongoDB database manipulation.

### ACP controle times

The algorithm for calculating controle times is described here [https://rusa.org/pages/acp-brevet-control-times-calculator](https://rusa.org/pages/acp-brevet-control-times-calculator). Additional background information is given here [https://rusa.org/pages/rulesForRiders](https://rusa.org/pages/rulesForRiders).

The algorithm does not account past 20% of each brevet, uses the French
calculation for KM 0-60, each brevet has the same open and close time up to 20%
past. Each specific brevet has a unique max, these are :(in hours and minutes, HH:MM)
3:30 for 200 KM, 20:00 for 300 KM, 27:00 for 400 KM, 40:00 for 600 KM, and 75:00 for 1000 KM
Each starting time is relative to the previous starting times, similar to the closing times.

acp_times.py provided by UOCIS322S21 resources, and project 3 implementation.

Program now accepts valid inputs into a database. If the user attempts to submit an invalid
value nothing will be added to the data base, and a message will be put on the index page.
If the user displays from an empty database an error will be raised.

This program also has a RESTful api service which allows the user to dictate what data
will be returned back to them via a webpage.

docker-compose.yml file runs 3 separate containers and the MongoDB database.

If the top "k" value is out of range of the top times it displays all of the times.
This includes negative and positive values. If k = 0 it displays nothing for all
api access's.

- POST **/register**

Registers a new user. On success a status code 201 is returned. The body of the response contains a JSON object with the newly added user. On failure status code 400 (bad request) is returned. Note: The password is hashed before it is stored in the database. Once hashed, the original password is discarded. Your database should have three fields: id (unique index), username and password for storing the credentials.

- GET **/token**

Returns a token. This request must be authenticated using a HTTP Basic Authentication. On success a JSON object is returned with a field `token` set to the authentication token for the user and a field `duration` set to the (approximate) number of seconds the token is valid. On failure status code 401 (unauthorized) is returned.

- GET **/RESOURCE**

Return a protected <resource>. This request is authenticated by using token-based authentication only. On success a JSON object with data for the authenticated user is returned. On failure status code 401 (unauthorized) is returned.

There is a maximum of 600 seconds for the user to be remembered by the session until it logs out and redirects the user to the index.

#

## Credits

Michal Young, Ram Durairajan, Steven Walton, Joe Istas.
