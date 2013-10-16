#!/usr/bin/env python3
'''web3 makedirs

integrate phonegap 3, 

1. cd projectname/projectname/public
2. cordova -d create app

projectname
|_README.txt
|_COPYING.txt
|_setup.py
|_docs
|_tests
|_projectname
| |_ __init__.py
| |_httpd.py
| |_url.py
| |_db
| |_etc
| |_public
| | |_js
| | | |_global.js
| | |_css
| | | |_basic.css
| | | |_layout.css
| | | |_color.css
| | | |_typography.css
| | |_image
| | |_upload
| | |_index.html
| | |_favicon.ico
| | |_favicon.png
| | |_tl
| | | |_private
| | | |_test
| | | | |_test.html
| | |_app
| | | |_www
| | | | |_default.html
| | | | |_favicon.ico
| | | | |_favicon.png
| | | | |_image
| | | | |_stylesheet
| | | | |_javascript
| | | | | |_ global.js
| | | | | |_framework
| | | | | | |_ cordova.js
| | | | | | |_ jquery.min.js
| | | | | | |_ jquery.mobile.min.js
| | | | | | |_ jquery.mobile.min.css
| | | | | | |_ underscore-min.js
| | | | | | |_ backbone-min.js
| |_lib
| | |_ __init__.py
| | |_node.py
| | |_helper.py
| | |_test.py
| | |_w3
| | | |_ __init__.py
| | | |_helper.py
| | | |_tmpl.py
| | | |_test.py
| | | |_private
| | | | |_ __init__.py
| | |_ws
| | | |_ __init__.py 
'''

import os
import sys
import configparser

def touch(node:str, content=None, isfile:bool=False)->bool:
    '''some linux command touch, create empty file'''
    f = open(node, 'w')
    if content:
        if isfile and os.path.exists(content):
            f2 = open(content, 'r')
            content = f2.read()
            f2.close()
        f.write(content)
    f.close()

def confile(confile:str, conf:dict=None):
    if os.path.exists(confile):
        c = configparser.SafeConfigParser()
        c.read(os.path.expanduser(confile))
        if 'DEFAULT' in conf:
            if 'application_root' in conf['DEFAULT']:
                c['DEFAULT']['application_root'] = conf['DEFAULT']['application_root']
            if 'document_root' in conf['DEFAULT']:
                c['DEFAULT']['document_root'] = conf['DEFAULT']['document_root']
            if 'web3_root' in conf['DEFAULT']:
                c['DEFAULT']['web3_root'] = conf['DEFAULT']['web3_root']

        if 'loggers' in conf:
            if 'keys' in conf['loggers']:
                c['loggers']['keys'] = conf['loggers']['keys']

                project = c['loggers']['keys'].split(',')[-1]
                project = project.strip()
                section = "logger_{}".format(project)
                if section in conf:
                    c.remove_section(section)
                c[section] = {}
                c[section]['level']='DEBUG';
                c[section]['qualname']=project
                c[section]['handlers']=''

        with open(confile, 'w') as f:
            c.write(f)


def mktree(root:str, path:str)->bool:
    '''make directory tree'''
    root = os.path.normpath(os.path.expanduser(os.path.expandvars(root)))
    project = root.split(os.sep)[-1]
    if not os.path.exists(root):
        os.makedirs(os.path.join(root, 'docs'))
        os.makedirs(os.path.join(root, 'tests'))
        os.makedirs(os.path.join(root, project))

        touch(os.path.join(root, 'README.txt'))
        touch(os.path.join(root, 'COPYING.txt'))
        touch(os.path.join(root, 'setup.py'))
        touch(os.path.join(root,  '__init__.py'))
        touch(os.path.join(root, project, 'url.py'), os.path.join(path, 'url.py'), True)
        touch(os.path.join(root, project, 'httpd.py'), os.path.join(path, 'httpd.py'), True)

        os.makedirs(os.path.join(root, project, 'public/tl'))
        os.makedirs(os.path.join(root, project, 'public/js'))
        os.makedirs(os.path.join(root, project, 'public/css'))
        os.makedirs(os.path.join(root, project, 'public/image'))
        os.makedirs(os.path.join(root, project, 'public/upload'))
        touch(os.path.join(root, project, 'public/js/global.js'))
        touch(os.path.join(root, project, 'public/index.html'), os.path.join(path, 'index.html'), True)
        touch(os.path.join(root, project, 'public/favicon.ico'))
        touch(os.path.join(root, project, 'public/favicon.png'))
        touch(os.path.join(root, project, 'public/css/basic.css'), os.path.join(path, 'basic.css'), True)
        touch(os.path.join(root, project, 'public/css/layout.css'))
        touch(os.path.join(root, project, 'public/css/color.css'))
        touch(os.path.join(root, project, 'public/css/typography.css'))
        os.makedirs(os.path.join(root, project, 'public/tl/test'))
        touch(os.path.join(root, project, 'public/tl/test/test.html'), os.path.join(path, 'tl_test_test.html'), True)
        
        os.makedirs(os.path.join(root, project, 'db'))
        os.makedirs(os.path.join(root, project, 'lib/ws'))
        os.makedirs(os.path.join(root, project, 'lib/w3'))
        os.makedirs(os.path.join(root, project, 'lib/w3/private'))
        
        touch(os.path.join(root, project, 'lib/__init__.py'))
        touch(os.path.join(root, project, 'lib/ws/__init__.py'))
        touch(os.path.join(root, project, 'lib/w3/private/__init__.py'))
        touch(os.path.join(root, project, 'lib/node.py'), os.path.join(path, 'lib_node.py'), True)
        touch(os.path.join(root, project, 'lib/helper.py'), os.path.join(path, 'lib_helper.py'), True)
        touch(os.path.join(root, project, 'lib/test.py'), os.path.join(path, 'lib_test.py'), True)
        touch(os.path.join(root, project, 'lib/w3/tmpl.py'), os.path.join(path, 'w3_tmpl.py'), True)
        touch(os.path.join(root, project, 'lib/w3/helper.py'), os.path.join(path, 'w3_helper.py'), True)
        touch(os.path.join(root, project, 'lib/w3/test.py'), os.path.join(path, 'w3_test.py'), True)
        touch(os.path.join(root, project, 'lib/ws/helper.py'), os.path.join(path, 'ws_helper.py'), True)
        touch(os.path.join(root, project, 'lib/ws/test.py'), os.path.join(path, 'ws_test.py'), True)


        # mkdir jquerymobile and phonegap tree
        if not os.path.exists(os.path.join(root, project, 'public/app/www')):
            os.makedirs(os.path.join(root, project, 'public/app/www'))

        os.makedirs(os.path.join(root, project, 'public/app/www/image'))
        os.makedirs(os.path.join(root, project, 'public/app/www/stylesheet'))
        os.makedirs(os.path.join(root, project, 'public/app/www/javascript/framework'))

        touch(os.path.join(root, project, 'public/app/www/default.html'), os.path.join(path, 'app_index.html'), True)
        touch(os.path.join(root, project, 'public/app/www/favicon.ico'))
        touch(os.path.join(root, project, 'public/app/www/favicon.png'))
        touch(os.path.join(root, project, 'public/app/www/javascript/global.js'), os.path.join(path, 'app_global.js'), True)
        touch(os.path.join(root, project, 'public/app/www/javascript/app.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/underscore-min.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/backbone-min.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/jquery.min.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/jquery.mobile.min.css'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/jquery.mobile.min.js'))
        # touch(os.path.join(root, project, 'public/app/www/javascript/framework/cordova.js'))


        os.makedirs(os.path.join(root, project, 'etc'))
        confilename = os.path.join(root, project, 'etc', "{}.conf".format(project))
        touch(confilename, os.path.join(path, 'project.conf'), True)
        confdict = dict(
            DEFAULT = dict(
                application_root = os.path.join(root, project),
                document_root = os.path.join(root, project, 'public'),
                web3_root = os.path.normpath(os.path.join(path, os.path.pardir, os.path.pardir))
                ),
            loggers = dict(
                keys = "root, {}".format(project)
                )
            )
        confile(confilename, confdict)

        

if __name__ == '__main__':
    import os
    import sys
    import site
    import argparse
    import wsgiref.simple_server

    parser = argparse.ArgumentParser(description='wsgi2 server', add_help=False)
    parser.add_argument('-h', '--host', default='localhost', help='server listener host or ip, default localhost')
    parser.add_argument('-p', '--port', type=int, default='8080', help='server listener port, default:8080')
    parser.add_argument('-t', '--tree', type=bool, default=False, help='project files tree touch, default:False')
    parser.add_argument('--lib', help='web3 lib directory')
    parser.add_argument('node', nargs='?', default='~/public_html', help='project startup node, default:current directory') # positional argument
    parser.print_help()
    ns = parser.parse_args()

    if ns.lib:
        site.addsitedir(os.path.expanduser(ns.lib))
        print('site.addsitedir {}'.format(ns.lib))

    from web3.lib.node import Node
    from web3.middleware.middleware import T12, application
    from web3.middleware.static import Static

    app = application
    app = Static(application, ns.node, '/')
    app = T12(app)

    # httpd = wsgiref.simple_server.make_server(ns.host, ns.port, wsgiref.simple_server.demo_app)
    # httpd = wsgiref.simple_server.make_server(ns.host, ns.port, app)
    httpd = wsgiref.simple_server.WSGIServer((ns.host, ns.port), wsgiref.simple_server.WSGIRequestHandler)
    httpd.set_app(app)

    if ns.tree:
        libpath = os.path.dirname(sys.modules[Node.__module__].__file__)
        tmpl_path = os.path.normpath(os.path.join(os.path.join(libpath, os.path.pardir, 'tmpl')))
        mktree(ns.node, tmpl_path)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        print('keyboard interrupt, exiting.')
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        parser.print_help()
        print("Serving HTTP on {}:{} ...".format(ns.host, ns.port))
    finally:
        sys.exit(0)
    
