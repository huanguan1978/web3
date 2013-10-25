#!/usr/bin/env python3
'''update js workframe
'''
import os
import sys
import shutil
import zipfile
import urllib.request

js = {'underscore-min.js':'http://underscorejs.org/underscore-min.js',
      'backbone-min.js':'http://backbonejs.org/backbone-min.js',
      'require.js':'http://requirejs.org/docs/release/2.1.8/minified/require.js',

      'jquery-1.10.2.min.js':'http://code.jquery.com/jquery-1.10.2.min.js',
      'jquery-1.10.2.min.map':'http://code.jquery.com/jquery-1.10.2.min.map',

      'jquery.mobile-1.3.2.js':'http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.js',
      'jquery.mobile-1.3.2.min.css':'http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.css',
      
      'jquery-ui-1.10.3.zip':'http://jqueryui.com/resources/download/jquery-ui-1.10.3.zip',
      # 'jquery.mobile-1.4.0-beta.1.zip':'http://jquerymobile.com/resources/download/jquery.mobile-1.4.0-beta.1.zip',
          }


jsz = {'jquery-ui-1.10.3.zip':('jquery-ui-1.10.3/ui/minified/', 'jquery-ui-1.10.3/themes/base/minified/'),
       # 'jquery.mobile-1.4.0-beta.1.zip':('images/', 'jquery.mobile.theme-1.3.2.min.css', 'jquery.mobile.structure-1.3.2.min.css', 'jquery.mobile-1.3.2.min.css', 'jquery.mobile-1.3.2.min.js', 'jquery.mobile-1.3.2.min.map'),
    }

jscp = {'jquery-1.10.2.min.js':'jquery.min.js',
        'jquery-1.10.2.min.map':'jquery.min.map',
        'jquery.mobile-1.3.2.js':'jquery.mobile.min.js',
        'jquery.mobile-1.3.2.min.css':'jquery.mobile.min.css',
}

def rejsname(path:str=None, jscopy:dict=None):
    jscopy = jscopy if jscopy else jscp

    if os.path.exists(path):
        for filename, copyname in jscopy.items():
            copyname = os.path.join(path, copyname)
            if not os.path.exists(copyname) or not os.path.getsize(copyname):
                shutil.copy(os.path.join(path, filename), copyname)

def rejszip(path:str=None, jszip:dict=None):
    jszip = jszip if jszip else jsz

    if os.path.exists(path):
        for zipfilename, nodes in jszip.items():
            zfile = os.path.join(path, zipfilename)
            if os.path.exists(zfile) and zipfile.is_zipfile(zfile):
                zf = zipfile.ZipFile(os.path.join(path, zipfilename))
                files = []
                for name in zf.namelist():
                    for node in nodes:
                        if name.startswith(node):
                            files.append(name)
                            break
                if files:
                    zf.extractall(path, files)
                zf.close()


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else: # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))



def rejslib(path:str=None, jslib:dict=None):
    jslib = jslib if jslib else js

    if os.path.exists(path):
        for filename, url in jslib.items():
            pathfile = os.path.join(path, filename)
            if not os.path.exists(pathfile) or not os.path.getsize(pathfile): # not exists or empty file
                sys.stderr.write("GET %s => %s.\n" %(url, filename))
                filename = os.path.join(path, filename)
                urllib.request.urlretrieve(url, filename, reporthook)
            else:
                sys.stderr.write("GET %s => %s, found, skip.\n" %(url, filename))




if __name__ == '__main__':
    print('rejslib: recreate commonjs libs, usage:rejslib [path]')
    path =  sys.argv[1] if len(sys.argv)>1 else None
    if not path:
        path = os.getcwd()
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path)

    rejslib(path)
    rejszip(path)
    rejsname(path)
