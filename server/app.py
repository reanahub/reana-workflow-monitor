# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

import os
import socketio
import zmq.green as zmq
from flask import Flask, render_template
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

ctx = zmq.Context()
sio = socketio.Server(logger=True, async_mode='gevent')
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'


def background_thread():
    """Example of how to send server generated events to clients."""
    socket = ctx.socket(zmq.SUB)
    socket.connect(os.environ['ZMQ_PROXY_CONNECT'])
    socket.setsockopt_string(zmq.SUBSCRIBE, u'')
    while True:
        msg = socket.recv_json()
        if 'yadage_ctrl' in msg:
            sio.emit('yadage_ctrl', {'data': msg['yadage_ctrl']},
                     room=msg['identifier'], namespace='/test')
        elif 'yadage_obj' in msg:
            sio.emit('yadage_state', {'data': msg['yadage_obj']},
                     room=msg['identifier'], namespace='/test')


@app.route('/<identifier>')
def index(identifier):
    return render_template('index.html', room=identifier)


@sio.on('connect', namespace='/test')
def connect(sid, environ):
    print('Client connected')


@sio.on('join', namespace='/test')
def enter(sid, data):
    print('data', data)
    print('Adding Client {} to room {}'.format(sid, data['room']))
    sio.enter_room(sid, data['room'], namespace='/test')


@sio.on('roomit', namespace='/test')
def roomit(sid, data):
    print('Emitting to Room: {}'.format(data['room']))
    sio.emit('join_ack', {'data':
                          'Welcome to the room {}'.format(data['room'])},
             room=data['room'], namespace='/test')


@sio.on('disconnect', namespace='/test')
def disconnect(sid):
    print('Client disconnected')


if __name__ == '__main__':
    sio.start_background_task(background_thread)
    pywsgi.WSGIServer(('0.0.0.0', 5000), app,
                      handler_class=WebSocketHandler).serve_forever()
