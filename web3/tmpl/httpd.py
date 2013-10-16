#!/bin/env python3

import os
import sys
import site
import sqlite3
import configparser

def dbinit_sqlite(dbh):
    dbh.isolation_level = None
    dbh.row_factory = sqlite3.Row
    dbh.execute('PRAGMA foreign_keys = ON')


def setenvif(environ:dict) -> dict:
    environ['wsgi.debug'] = True
    return environ

def app(confile:str)->object:
    c = configparser.SafeConfigParser()
    c.read(os.path.expanduser(confile))

    site_web3 = c.get('DEFAULT', 'web3_root')
    if site_web3:
        site_web3 = os.path.expanduser(site_web3)
        site.addsitedir(site_web3)

    site_app = c.get('DEFAULT', 'application_root')
    if site_app:
        site_app = os.path.expanduser(site_app)
        site.addsitedir(site_app)


    from web3.lib.node import Node
    from web3.middleware.middleware import T12, application
    from web3.middleware.static import Static
    from web3.middleware.tmpl import Tmpl
    from web3.middleware.route import Route
    from web3.middleware.dbi import DB
    from web3.middleware.env import Env
    from web3.middleware.zip import Zip
    from web3.middleware.session import Cookie, Session, Sqlite

    from url import urls

    link = dict()
    for k, v in c.items('link'):
        link[k] = v

    sess_db = "{}_{}_{}.sqlite".format('web3sess', c.get('web3', 'host'), c.get('web3', 'port') )

    app = application
    app = Static(app, c.get('static', 'path'), c.get('static', 'path_info'))
    app = Route(app, urls, authenticate=True)
    app = Zip(app)
    app = Tmpl(app, c.get('template', 'path'), watch=True)

    app = Cookie(app)
    app = Session(app, Sqlite(os.path.join(site_app, 'db', sess_db)))
    app = DB(app, link, dbinit_sqlite)
    app = Env(app, setenvif)

    app = T12(app)

    return app

if __name__ == '__main__':

    import argparse
    from wsgiref import simple_server

    parser = argparse.ArgumentParser(description='wsgi2ref web3', add_help=False)
    parser.add_argument('-h', '--host', default='localhost', help='server listener host or ip, default:localhost')
    parser.add_argument('-p', '--port', type=int, default=8080, help='server listener port, default:8080')
    parser.add_argument('node', nargs='?', default='~/public_html', help='project startup node, default:~/public_html')
    parser.print_help();print()
    ns = parser.parse_args()

    confile = '{}.conf'.format(ns.node.split(os.sep)[-1])
    confile = os.path.join(ns.node, 'etc', confile)
    print("confile:{}".format(confile))
    application = app(confile)

    c = configparser.SafeConfigParser()
    c.read(confile)

    host = c.get('web3', 'host')
    port = c.getint('web3', 'port')
    debug = c.getboolean('web3', 'debug')


    httpd = simple_server.WSGIServer((ns.host, ns.port), simple_server.WSGIRequestHandler)
    httpd.set_app(application)
    
    print("Serving HTTP on {}:{} ...".format(ns.host, ns.port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        print('keyboard interrupt, exiting.')
    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        sys.exit(0)
