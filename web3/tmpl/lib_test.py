from .w3.test import Test as W3Test
from .ws.test import Test as WSTest

from web3.lib.helper import Helper
from web3.lib.node   import Node

class Test(W3Test, WSTest, Node, Helper):
    pass
