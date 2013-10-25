#!/bin/env python

import os
import sys
import unittest

sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../')))

from web3.lib.node import Node

class N(Node):
    def __init__(self, environ):
        self._env = environ

class TestNode(unittest.TestCase):
    def setUp(self):
        self._env = {}
        self._n = N(self._env)

    def tearDown(self):
        pass


    def test_w3_id(self):
        url = '/order/12345/?a=1&b=2#bookmark1'
        self.assertEqual('12345', self._n._w3_id(url))
        self.assertEqual('12345', self._n._w3_id(url, '\d+'))
        self.assertEqual('12345', self._n._w3_id(url, '\d+', lambda x: True))
        self.assertFalse(self._n._w3_id(url, '\D+'))
        self.assertFalse(self._n._w3_id(url, exist=lambda x: False))
        

if __name__ == '__main__':
    unittest.main()
