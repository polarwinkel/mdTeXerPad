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
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send message back to client
        message = '''
                <!doctype html><html>
                <head>
                    <title>mdTeXerPad</title><meta charset="utf-8" />
                </head>
                <body style="background-color:#040;">
                <h1>mdTeXerPad</h1>
                <div id="notConnected" style="width:100%;background-color:#faa;display:none;">
                    <p style="text-align:center;">Not connected to WebSocketServer!<!--<button onclick="connect()">Try Reconnect</button>--></p>
                </div>
                <textarea id="mdtex" oninput="sendMdTeX()" style="width:49%; height:200px; float:left;" disabled></textarea>
                <div id="htmlOut" style="border:1px solid black; width:49%; float:right; background-color:#fff;"></div>
                <button id="editMode" onclick="window.location.assign(window.location.href.concat('edit'))">Edit this!</button></p>
                <script>
                function connect() {
                    var mdtex = document.querySelector('#mdtex');
                    try { 
                        var ws = new WebSocket("ws://".concat(window.location.hostname, ":8082/"));
                    } catch(e) {
                        document.getElementById('notConnected').style.display='block';
                    }
                    mdtex.oninput = function (event) {
                        if (window.location.pathname.endsWith('edit')) {
                            try {
                                ws.send(mdtex.value);
                            } catch(e) {
                                document.getElementById('notConnected').style.display='block';
                            }
                        } else {
                            mdtex.disabled = true;
                            alert('TODO: Besser machen!');
                        }
                    }
                    ws.onmessage = function (event) {
                        data = JSON.parse(event.data);
                        out = document.getElementById('htmlOut');
                        out.innerHTML = data.html;
                        mdtex.value = data.mdtex;
                        /*out.innerHTML = event.data;*/
                    };
                    ws.onopen = function (e) {
                        document.getElementById('notConnected').style.display='none';
                    };
                    ws.onclose = function(e) {
                        console.log('Socket is closed. Reconnect will be attempted in 3 seconds.', e.reason);
                        setTimeout(function() {
                            if (ws.readyState != 1) {
                                document.getElementById('notConnected').style.display='block';
                            }
                            connect();
                        }, 3000);
                    }
                    ws.onerror = function(err) {
                        console.error('Socket encountered error: ', err.message, 'Closing socket');
                        ws.close();
                    };
                }
                connect();
                if (window.location.pathname.endsWith('edit')) {
                    mdtex.disabled = false;
                    document.getElementById('editMode').style.display='none';
                }
document.onkeydown = function(e){
    if(e.ctrlKey && e.which === 83){ // Check for the Ctrl key being pressed, and if the key = [S] (83)
        alert('ERROR 501: TODO: speichern implementieren');
        e.preventDefault();
        return false;
    }
}
                </script>
                '''
        message += '\n</body>\n</html>'
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

# WebSocketServer-stuff:

#async def socketMdTeX2html(websocket, path):
#    '''Websocket-Server single-user-mode'''
#    while True:
#        try:
#            mdtex = await websocket.recv()
#            html = mdTeX2html.convert(mdtex)
#            await websocket.send(html)
#        except:
#            pass

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
    print('webserver is running')
    httpd.serve_forever()

def runWsServer():
    ''' start the websocket-server '''
    print('starting websocketserver')
    if onlyLocal: addr='127.0.0.1'
    else: addr='0.0.0.0'
    start_server = websockets.serve(wsHandler, addr, wsServerPort)
    ws = asyncio.get_event_loop()
    ws.run_until_complete(start_server)
    print('websocketserver is running')
    ws.run_forever()

wsServer = Process(target=runWsServer, args=())
wsServer.start()
webServer = Process(target=runWebServer, args=())
webServer.start()
