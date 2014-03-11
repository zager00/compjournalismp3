from flask import Flask, url_for, redirect
from flask import request
from flask import render_template

from alchemyapi import AlchemyAPI
import json

import urllib

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

from werkzeug.contrib.cache import SimpleCache

CACHE_TIMEOUT = 60 * 10

cache = SimpleCache()

class cached(object):

    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.args.get('url'))
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.args.get('url'), response, self.timeout)
            return response
        return decorator


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/sentimenturl', methods=['GET'])
@crossdomain(origin="*")
@cached()
def my_form_post():
    try:
        url = request.args.get('url')
        alchemyapi = AlchemyAPI()
        response = alchemyapi.sentiment('url', url)
        result = str(0.0)
        if response['status'] == 'OK':
            result =  str(response['docSentiment']['score'])
        print 'Result: ', str(response)
        return result
    except Exception as e:
        print e
        return str(0.0)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
