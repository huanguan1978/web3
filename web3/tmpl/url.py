#!/bin/env python

#urls = [(httpsonly?,'http_host regex pattern', 'path_info regex pattern', 'module.classname', {
#        'request-method':(auth role),
#        }),]

import re

from lib.test import Test

urls = [
    (0, re.compile('.*', re.I), re.compile('^/test.*'), Test, {}),
]

path = {
    '/test/':{'pattern':re.compile('^/test/.*'),
               'urls':[
            '/test/1234', '/test/abcd/',
            '/test?a=1&b=2', '/test?s=abcd',
            ]},

    '/register/validate':{'pattern':re.compile('^/register/validate'),
              'urls':[
            '/register/validate?email=crown.hg@gmail.com',
            ]},

}


def test(path:dict):
    for k, v in path.items():
        pattern = v['pattern']
        urls = v['urls']
        for url in urls:
            if isinstance(pattern, str):
                print("{}\t{}".format(pattern, url))
                obj = re.match(pattern, url)
            else:
                print("{}\t{}".format(pattern.pattern, url))
                obj = pattern.match(url)

            assert obj

if __name__ == '__main__':
    test(path)
