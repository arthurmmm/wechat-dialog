#!/usr/bin/env python

import os
import time
import json
import logging
import hashlib

from flask import Flask, render_template, request, make_response, jsonify, session, escape, redirect, url_for

import wechat.bot
import demo_dialog

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.debug = True

# 公众号token
TOKEN = 'amwatcher'
        
@app.route('/', methods=['GET'])
def wechat_get():
    ''' Token validation logic 
    '''
    timestamp = request.args.get('timestamp', '')
    if not timestamp:
        return 'This page is used for wechat validation'
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    token = TOKEN
    
    list = [token, timestamp, nonce]
    list.sort()
    list = ''.join(list).encode('utf-8')
    logger.debug(list)
    hashcode = hashlib.sha1(list).hexdigest()
    logger.info('handle/GET func: hashcode %s, signature %s' % (hashcode, signature))
    if hashcode == signature:
        return echostr
    else:
        return ''
        
@app.route('/', methods=['POST'])
def wechat_post():
    ''' WeChat reply bot
    '''
    data = request.get_data()
    logger.info('Receiving data: %s' % data)
    return wechat.bot.answer(data, demo_dialog).format()
            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)