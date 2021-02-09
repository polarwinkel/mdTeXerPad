#!/usr/bin/python3
# TODO: Qt WebChannel checken!
'''
Flask wsgi-interface for mdTeXerPad
Base file of mdTeXerPad:
A pad-like browser app to live-render Markdown with TeX-formulas

This starts a Webserver and a WebSocketServer for the mdTeXerPad.
'''

import os
from contextvars import ContextVar
from flask import Flask, render_template, request, send_from_directory, make_response, jsonify
from flask_sockets import Sockets # TODO: Not running on Ubuntu 20.04 due to an old version of gevent, switch to this some day to use only one port
import json
# convertions to html:
from modules import mdTeX2html

# global settings:

app = Flask(__name__)
debug = True

sockets = Sockets(app)

host='0.0.0.0'

# WebServer stuff:

@app.route('/<path:path>', methods=['GET'])
def index(path):
    return render_template('page.html')

@app.route('/static/<path:path>', methods=['GET'])
def sendStatic(path):
    return send_from_directory('', path)

# WebSocketServer-stuff:

USERS = set()
mdtex = type('', (), {})() # empty object, so that it is available in all async functions
mdtex.value = '''
## Example-Title
#
#TeX-Formula: $\sqrt2=x^2 \Rightarrow x=\sqrt{\sqrt{2}}$
#
#- This
#- is
#    - a List
#
#Delete this and write your own `mdTeX`!
#'''

#async def register(websocket):
#    USERS.add(websocket)
#    print('user added, ' + str(len(USERS))+ ' user(s) online')
#    html = mdTeX2html.convert(mdtex.value)
#    replyd = {'mdtex': mdtex.value, 'html': html}
#    replyj = json.dumps(replyd)
#    await asyncio.wait([user.send(replyj) for user in USERS])
#
#async def unregister(websocket):
#    USERS.remove(websocket)
#    print('user removed, ' + str(len(USERS))+ ' user(s) online')
#
#async def wsHandler(websocket, path):
#    # Register.
#    await register(websocket)
#    try:
#        async for message in websocket:
#            mdtex.value = message
#            html = mdTeX2html.convert(message)
#            replyd = {'mdtex': message, 'html': html}
#            replyj = json.dumps(replyd)
#            if USERS:  # asyncio.wait doesn't accept an empty list
#                await asyncio.wait([user.send(replyj) for user in USERS])
#    except:
#        pass
#    finally:
#        await unregister(websocket)

@sockets.route('/ws')
def mdtex_socket(ws):
#    while True:
#    while not ws.closed:
    #if not USERS:
    if ws not in USERS:
        USERS.add(ws)
    if ws.closed:
        USERS.remove(ws)
    while (USERS != False):
        #USERS.add(ws)
        message = ws.receive()
        #mdtex.value = message
        html = mdTeX2html.convert(message)
        replyd = {'mdtex': message, 'html': html, 'users': str(len(USERS))}
        replyj = json.dumps(replyd)
        for user in USERS:
            try:
                user.send(replyj)
            except:
                USERS.remove(ws)
        #ws.send(replyj)

# run it:

if __name__ == '__main__':
    app.run(host=host, debug=debug)
