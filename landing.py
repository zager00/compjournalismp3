from flask import Flask, url_for, redirect
from flask import request
from flask import render_template

from alchemyapi import AlchemyAPI
import json

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/', methods=['POST'])
def my_form_post():
    try:
        url = request.form['url']
        alchemyapi = AlchemyAPI()
        response = alchemyapi.sentiment('url', url)
        result = 0.0
        if response['status'] == 'OK':
            result =  str(response['docSentiment']['score'])
        print 'Result: ', result
        return result
    except Exception as e:
        print e
        return str(0.0)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
