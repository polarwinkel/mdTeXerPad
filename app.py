#!/usr/bin/python3
'''
Flask wsgi-interface for mdTeXerPad
Base file of mdTeXerPad:
A pad-like browser app to live-render Markdown with TeX-formulas

This starts a Webserver and a WebSocketServer for the mdTeXerPad.
'''

import os
import logging
from contextvars import ContextVar
from flask import Flask, render_template, request, send_from_directory, make_response, jsonify
from flask_sockets import Sockets # Not working on Ubuntu 20.04 due to an old version of gevent
import asyncio
import json
from modules import mdTeX2html

# global settings:

app = Flask(__name__)
debug = True

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

sockets = Sockets(app)

host='0.0.0.0'

# WebServer stuff:

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def index(path):
    app.logger.info('http connection: '+str(request.remote_addr))
    return render_template('page.html', path=path)

@app.route('/static/<path:path>', methods=['GET'])
def sendStatic(path):
    return send_from_directory('', path)

# WebSocketServer-stuff:

# Only 1 gunicorn-worker is supported since the connections are stored 
# in variables that the other workers can't access!
USERS = set()
mdtex = type('', (), {})() # empty object, so that it is available in all async functions
mdtex.value = '''
# Example-Title

TeX-Formula: $\sqrt2=x^2 \Rightarrow x=\sqrt{\sqrt{2}}$

- This
- is
    - a List

Delete this and write your own `mdTeX`!
'''

@sockets.route('/ws')
def mdtex_socket(ws):
    if ws not in USERS:
        USERS.add(ws)
        app.logger.info('ws connected: '+str(request.remote_addr)+', '+str(len(USERS))+' users online now')
    html = mdTeX2html.convert(mdtex.value)
    replyd = {'mdtex': mdtex.value, 'html': html, 'users': str(len(USERS))}
    replyj = json.dumps(replyd)
    ws.send(replyj)
    message = None
    while True:
        if message != None:
            mdtex.value = str(message)
        html = mdTeX2html.convert(mdtex.value)
        replyd = {'mdtex': mdtex.value, 'html': html, 'users': str(len(USERS))}
        replyj = json.dumps(replyd)
        if message != None:
            asyncio.run(sendUpdate())
        try:
            message = ws.receive()
        except:
            # close connection on error, client may reconnect
            break

async def sendUpdate():
    html = mdTeX2html.convert(mdtex.value)
    replyd = {'mdtex': mdtex.value, 'html': html, 'users': str(len(USERS))}
    replyj = json.dumps(replyd)
    for ws in USERS.copy():
        try:
            ws.send(replyj)
        except:
            try:
                USERS.remove(ws)
            except WebSocketError:
                pass
                # garbage collector will remove dead object
            app.logger.info('One ws-client was dropped, '+str(len(USERS))+' users remain')

# run it:

if __name__ == '__main__':
    app.run(host=host, debug=debug)
