#!/usr/bin/python3
# TODO: Qt WebChannel checken!
'''
Base file of mdTeXerPad:
A pad-like browser app to live-render Markdown with TeX-formulas

This starts a Webserver and a WebSocketServer at the same time on different ports.
'''

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import asyncio
from contextvars import ContextVar
import websockets
import json
from multiprocessing import Process
# convertions to html:
from modules import mdTeX2html

# global settings:

webServerPort = 8081
wsServerPort = 8082
onlyLocal = False

# WebServer stuff:

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    ''' HTTPRequestHandler class '''
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        if self.path.startswith('/static/'):
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True
            elif self.path.endswith('.woff2'):
                mimetype = 'application/font-woff2'
                sendReply = True
            if sendReply == True:
                #Open the static file requested and send it
                fipath = (str(os.getcwd())+self.path)
                f = open(fipath, 'rb')
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            else:
                self.send_error(501,'unsupported file type on path %s' % self.path)
            return
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send message back to client
        with open('static/page.html') as f:
            page = f.read()
        # Write content as utf-8 data
        self.wfile.write(bytes(page, "utf8"))
        return

# WebSocketServer-stuff:

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

async def register(websocket):
    USERS.add(websocket)
    print('user added, ' + str(len(USERS))+ ' user(s) online')
    html = mdTeX2html.convert(mdtex.value)
    replyd = {'mdtex': mdtex.value, 'html': html}
    replyj = json.dumps(replyd)
    await asyncio.wait([user.send(replyj) for user in USERS])

async def unregister(websocket):
    USERS.remove(websocket)
    print('user removed, ' + str(len(USERS))+ ' user(s) online')

async def wsHandler(websocket, path):
    # Register.
    await register(websocket)
    try:
        async for message in websocket:
            mdtex.value = message
            html = mdTeX2html.convert(message)
            replyd = {'mdtex': message, 'html': html}
            replyj = json.dumps(replyd)
            if USERS:  # asyncio.wait doesn't accept an empty list
                await asyncio.wait([user.send(replyj) for user in USERS])
    except:
        pass
    finally:
        await unregister(websocket)

# get it started:

def runWebServer():
    ''' start the webserver '''
    print('starting webserver')
    if onlyLocal: addr='127.0.0.1'
    else: addr='0.0.0.0'
    server_address = (addr, webServerPort)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('webserver is running on port '+str(webServerPort))
    httpd.serve_forever()

def runWsServer():
    ''' start the websocket-server '''
    print('starting websocketserver')
    if onlyLocal: addr='127.0.0.1'
    else: addr='0.0.0.0'
    start_server = websockets.serve(wsHandler, addr, wsServerPort)
    ws = asyncio.get_event_loop()
    ws.run_until_complete(start_server)
    print('websocketserver is running on port '+str(wsServerPort))
    ws.run_forever()

wsServer = Process(target=runWsServer, args=())
wsServer.start()
webServer = Process(target=runWebServer, args=())
webServer.start()
