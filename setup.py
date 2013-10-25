import os
import sys
import codecs

from distutils.core import setup

def readme(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname), 'r', 'utf-8').read()


'''
ref:http://www.scotttorborg.com/python-packaging/index.html
'''

PACKAGE = 'web3'
NAME = 'web3'
DESCRIPTION = 'web3 is a microframework for Python3 based on WSGI2'
AUTHOR = 'crown.hg'
AUTHOR_EMAIL = 'crown.hg@gmail.com'
URL = 'http://github.com/huanguan1978/web3'
DOWNLOAD_URL = 'http://github.com/huanguan1978/web3/archive/master.zip'
VERSION = __import__(PACKAGE).__version__
KEYWORDS = ['wsgi', 'wsgi2']

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,

    description=DESCRIPTION,
    long_description=readme('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Web3",
        "Natural Language :: English",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: Chinese (Traditional)",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    download_url = DOWNLOAD_URL,
    keywords = KEYWORDS,
    license='BSD',

    packages = ['web3', 'web3.lib', 'web3.middleware'],
    package_dir={'web3':'web3', 'web3.lib':'web3/lib', 'web3.middleware':'web3/middleware'},
    package_data = {'web3':['tmpl/*', 'test/middleware/*.py', 'test/*.py']},
    scripts = ['scripts/web3rejslib.py', 'scripts/web3tree.py'],
    include_package_data=True,
    zip_safe=False
)
