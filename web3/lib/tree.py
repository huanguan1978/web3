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
| |_db
| |_etc
| |_public
| | |_js
| | | |_global.js
| | |_css
| | |_image
| | |_upload
| | |_index.html
| | |_favicon.ico
| | |_favicon.png
| | |_tl
| | | |_private
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
| | |_w3
| | | |_ __init__.py
| | | |_private
| | | | |_ __init__.py
| | |_ws
| | | |_ __init__.py 
'''

import os

app_global_js = \
'''
//Disable jQM routing and component creation events. ref:https://github.com/ccoenraets/backbone-jquerymobile
$(document).bind("mobileinit", function(){     

   $.mobile.hashListeningEnabled = false;    // disable hash-routing
   $.mobile.linkBindingEnabled = false;    // disable anchor-control
   $.mobile.ajaxEnabled = false;    // can cause calling object creation twice and back button issues are solved
   $.mobile.autoInitializePage = false;    // Otherwise after mobileinit, it tries to load a landing page
   $.mobile.page.prototype.options.domCache = false;   // we want to handle caching and cleaning the DOM ourselves

   // consider due to compatibility issues
   $.mobile.pushStateEnabled = false;    // not supported by all browsers
   $.mobile.phonegapNavigationEnabled = true;    // Solves phonegap issues with the back-button
   $.mobile.page.prototype.options.degradeInputs.date = true;    //no native datepicker will conflict with the jQM component
});
'''

app_index_html = \
'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="format-detection" content="telephone=no" />
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1, target-densitydpi=device-dpi" />

    <title>default</title>
    <link rel="shortcut icon" type="image/vnd.microsoft.icon" href="favicon.ico" />
    <link rel="icon" type="image/png" href="favicon.png" />
    <link rel="stylesheet" href="javascript/framework/jquery.mobile.min.css" />
    <script src="javascript/framework/jquery.min.js"></script>
    <script src="javascript/global.js"></script>
    <script src="javascript/framework/jquery.mobile.min.js"></script>
    <script src="javascript/framework/underscore-min.js"></script>
    <script src="javascript/framework/backbone-min.js"></script>
    <script src="cordova.js"></script>
  </head>
  <body>
    <p>Hello world</p>
  </body>
  <script src="javascript/app.js" defer="defer"></script>
</html>
'''
index_html = \
'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>index</title>
    <link rel="shortcut icon" type="image/vnd.microsoft.icon" href="favicon.ico" />
    <link rel="icon" type="image/png" href="favicon.png" />
    <!--<link rel="stylesheet" href="js/jquery-ui/themes/base/minified/jquery-ui.min.css" />-->
    <script src="app/www/javascript/framework/underscore-min.js"></script>
    <script src="app/www/javascript/framework/backbone-min.js"></script>
    <script src="app/www/javascript/framework/jquery.min.js"></script>
    <!--<script src="js/jquery-ui/ui/minified/jquery-ui.min.js"></script>-->
  </head>
  <body>
    <p>Hello world</p>
  </body>
  <script src="js/global.js" defer="defer"></script>
</html>
'''

def touch(node:str, content=None)->bool:
    '''some linux command touch, create empty file'''
    f = open(node, 'w')
    if content:
        f.write(content)
    f.close()

def mktree(root:str)->bool:
    '''make directory tree'''
    root = os.path.normpath(os.path.expanduser(os.path.expandvars(root)))
    project = root.split(os.sep)[-1]
    if not os.path.exists(root):
        os.makedirs(os.path.join(root, 'docs'))
        os.makedirs(os.path.join(root, 'tests'))

        touch(os.path.join(root, 'README.txt'))
        touch(os.path.join(root, 'COPYING.txt'))
        touch(os.path.join(root, 'setup.py'))
        touch(os.path.join(root,  '__init__.py'))


        os.makedirs(os.path.join(root, project, 'public/tl'))
        os.makedirs(os.path.join(root, project, 'public/js'))
        os.makedirs(os.path.join(root, project, 'public/css'))
        os.makedirs(os.path.join(root, project, 'public/image'))
        os.makedirs(os.path.join(root, project, 'public/upload'))
        touch(os.path.join(root, project, 'public/js/global.js'))
        touch(os.path.join(root, project, 'public/index.html'), index_html)
        touch(os.path.join(root, project, 'public/favicon.ico'))
        touch(os.path.join(root, project, 'public/favicon.png'))
        
        os.makedirs(os.path.join(root, project, 'db'))
        os.makedirs(os.path.join(root, project, 'etc'))

        os.makedirs(os.path.join(root, project, 'lib/ws'))
        os.makedirs(os.path.join(root, project, 'lib/w3'))
        os.makedirs(os.path.join(root, project, 'lib/w3/private'))
        
        touch(os.path.join(root, project, 'lib/__init__.py'))
        touch(os.path.join(root, project, 'lib/ws/__init__.py'))
        touch(os.path.join(root, project, 'lib/w3/private/__init__.py'))

        # mkdir jquerymobile and phonegap tree
        if not os.path.exists(os.path.join(root, project, 'public/app/www')):
            os.makedirs(os.path.join(root, project, 'public/app/www'))

        os.makedirs(os.path.join(root, project, 'public/app/www/image'))
        os.makedirs(os.path.join(root, project, 'public/app/www/stylesheet'))
        os.makedirs(os.path.join(root, project, 'public/app/www/javascript/framework'))

        touch(os.path.join(root, project, 'public/app/www/default.html'), app_index_html)
        touch(os.path.join(root, project, 'public/app/www/favicon.ico'))
        touch(os.path.join(root, project, 'public/app/www/favicon.png'))
        touch(os.path.join(root, project, 'public/app/www/javascript/global.js'), app_global_js)
        touch(os.path.join(root, project, 'public/app/www/javascript/app.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/underscore-min.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/backbone-min.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/jquery.min.js'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/jquery.mobile.min.css'))
        touch(os.path.join(root, project, 'public/app/www/javascript/framework/jquery.mobile.min.js'))
        # touch(os.path.join(root, project, 'public/app/www/javascript/framework/cordova.js'))
        

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
    if ns.tree:
        mktree(ns.node)

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
    
