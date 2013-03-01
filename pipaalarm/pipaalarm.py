#!/usr/bin/python
"""A web.py application powered by gevent"""

import sys
import os
import re
import web
import base64
import logging

import gevent

from gevent import monkey; monkey.patch_all()
import threading; threading._DummyThread._Thread__stop = lambda x: 42

from web import form
from signal import SIGTERM, SIGQUIT, SIGINT
from gevent import signal
from gevent.pywsgi import WSGIServer

from config import dispatcher, arping, config

from arping import device

urls = ("/", "index",
        "/register/([0-9a-f]{2}([-:][0-9a-f]{2}){5})$", "register",
        "/unregister/([a-zA-Z0-9]+)", "unregister",
        "/login", "login",
        "/(js|css|img)/(.*)", "static")

### Templates
t_globals = {
    'datestr': web.datestr
}
dot = os.path.split(os.path.realpath(__file__))[0]
render = web.template.render(os.path.join(dot, "templates"), base='base', globals=t_globals)

class login:
    def GET(self):
        allowed = ( (config.getUsername(), config.getPassword()), )
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ','',auth)
            username,password = base64.decodestring(auth).split(':')
            if (username.strip(),password.strip()) in allowed:
                raise web.seeother('/')
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate','Basic realm="Auth example"')
            web.ctx.status = '401 Unauthorized'
            return

class index(object):
    def GET(self):
        active_devices = arping.get_active_devices()
        return render.index(active_devices, config.getClients())

class register(object):
    form = form.Form(
        form.Textbox('name',
            form.regexp("[a-zA-Z0-9]+", "Name incorrect"),
            size=30, description="Name of device:"),
        form.Button('Add device'),
    )

    def GET(self, mac, x):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        if mac in [client[1] for client in config.getClients()]:
            raise web.seeother()

        form = self.form()
        return render.register(form, mac)

    def POST(self, mac, x):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        form = self.form()
        if not form.validates():
            return render.register(form)

        config.addClient(form.d.name, mac)
        arping.monitored_devices.add(
            device("", mac))
        raise web.seeother('/')

class unregister(object):
    def GET(self, name):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
            raise web.seeother('/login')

        config.removeClient(name)
        raise web.seeother('/')

class static:
    def GET(self, media, file):
        try:
            f = open(os.path.join(dot, "static", media ,file), 'r')
            return f.read()
        except:
            return '' # you can send an 404 error here if you want

def exit(arping, server):
    server.kill()
    arping.stop()
    sys.exit(0)

def main():
    loglevel = 'INFO'

    datefmt = '%b %d %H:%M:%S'
    logformat = '%(asctime)s %(levelname)s pysms: %(message)s'

    logging.basicConfig(level=loglevel,
                        stream=sys.stdout,
                        format=logformat,
                        datefmt=datefmt)

    application = web.application(urls, globals()).wsgifunc()
    server = WSGIServer(('', 8088), application)

    signal(SIGTERM, exit, arping, server=server)
    signal(SIGQUIT, exit, arping, server=server)
    signal(SIGINT, exit, arping, server=server)

    print "Starting message dispatcher"
    dispatcher.start()
    print "Starting arping monitor"
    arping.start()
    print 'Serving on 8088...'
    server.start()

    while True:
        try:
            gevent.sleep(0)
        except KeyboardInterrupt:
            # Switch to main thread, to quit gracefully
            gevent.hub.get_hub().switch()
            exit(arping, server)

if __name__ == "__main__":
    main()
