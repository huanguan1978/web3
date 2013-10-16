from web3.lib.helper import Helper as WHelper # Web framework lib

from .w3.helper import Helper as W3Helper
from .ws.helper import Helper as WSHelper

class Helper(W3Helper, WSHelper, WHelper):
    pass
