#!/usr/bin/env python
'''ascii art
'''
import sys
import time
import random
import unittest
import abc

class AFEoverflow(Exception):
    def __init__(self, message):
        self.__msg = message
    def __str__(self):
        return self.__msg
    def __repr__(self):
        return repr(self.__msg)

class AF(metaclass=abc.ABCMeta):
    _limit = 2
    _offset = 8

    _asciis = tuple(chr(x) for x in range(33, 127))
    _sets = set(_asciis)
    _fonts = _asciis
    _font = dict(zip(_asciis, _fonts))

    @abc.abstractproperty
    def limit(self):
        return self._limit
    @limit.setter
    def limit(self, limit:int):
        self._limit = limit
        return self._limit

    @abc.abstractproperty
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset:int):
        self._offset = offset
        return self._offset

    @abc.abstractproperty
    def asciis(self):
        return self._asciis

    @abc.abstractproperty
    def sets(self):
        return self._sets

    @abc.abstractproperty
    def fonts(self):
        return self._fonts

    @abc.abstractproperty
    def font(self):
        return self._font

    @abc.abstractmethod
    def randstr(self) ->str:
        random.seed(time.time())

        l = []
        i = random.randint(self.limit, self.offset)
        while i:
            l.append(random.choice(self.asciis))
            i -= 1

        return ''.join(l)

    @abc.abstractmethod
    def diff(self, string:str) -> set:
        _inputs = set(string)
        _diffs = _inputs - self.sets

        if _diffs:
            msg = "overflow:diff {}, string {}, not subset {}".format(_diffs, string, self.asciis)
            raise AFoverflow(msg)

        return _diffs

    @abc.abstractmethod
    def output(self, string:str=None) -> tuple:
        if string is None:
            string = self.randstr()

        diffs = self.diff(string)
        if not diffs:
            return [self.font[af] for af in string]


class Alnum(AF):
    _limit = 2
    _offset = 8

    _asciis = tuple(chr(x) for x in range(33, 127))
    _sets = set(_asciis)
    _fonts = _asciis
    _font = dict(zip(_asciis, _fonts))

    @property
    def limit(self):
        return self._limit
    @limit.setter
    def limit(self, limit:int):
        self._limit = limit
        return self._limit

    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset:int):
        self._offset = offset
        return self._offset

    @property
    def asciis(self):
        return super().asciis

    @property
    def sets(self):
        return super().sets

    @property
    def fonts(self):
        return self._fonts

    @property
    def font(self):
        return super().font

    def randstr(self) ->str:
        return super().randstr()

    def diff(self, string:str) -> set:
        return super().diff(string)

    def output(self, string:str=None) -> tuple:
        if string is None:
            string = self.randstr()
            return string

        diffs = self.diff(string)
        if not diffs:
            return [self.font[af] for af in string]

        return super().output(string)

class Clock(AF):
    _limit = 2
    _offset = 8

    _asciis = tuple(set(range(10)) | set(chr(x) for x in  range(ord('a'), ord('f')+1)) | set(chr(x) for x in  range(ord('A'), ord('F')+1)))
    _sets = set(_asciis)
    _fonts = _asciis
    _font = dict(zip(_asciis, _fonts))

    @property
    def limit(self):
        return self._limit
    @limit.setter
    def limit(self, limit:int):
        self._limit = limit
        return self._limit

    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, offset:int):
        self._offset = offset
        return self._offset

    @property
    def asciis(self):
        return super().asciis

    @property
    def sets(self):
        return super().sets

    @property
    def fonts(self):
        return self._fonts

    @property
    def font(self):
        return super().font

    def randstr(self) ->str:
        return super().randstr()

    def diff(self, string:str) -> set:
        return super().diff(string)

    def output(self, string:str=None) -> tuple:
        if string is None:
            string = self.randstr()
            return string

        diffs = self.diff(string)
        if not diffs:
            return [self.font[af] for af in string]

        return super().output(string)


class AA:
    '''AsciiArt'''

    def __init__(self, limit:int=2, offset:int=8):
        self._mode = mode
        self._limit = limit
        self._offset = offset
        self._modules = ('alnum', 'clock', 'upper3row')
        self._hexs = tuple(set(range(10)) | set(chr(x) for x in  range(ord('a'), ord('f')+1)) | set(chr(x) for x in  range(ord('A'), ord('F')+1)))
        self._alnum = tuple(chr(x) for x in range(33, 127))
        self._upper_ascs = tuple(range('A', ord('Z')+1))
        self._upper_3rows = [' /\\\n/--\\', ' _\n|_)\n|_)', ' _\n|\n|_', ' _\n| \\\n|_/', ' _\n|_\n|_', ' _\n|_\n|', ' _\n| _\n|_|', '\n|_|\n| |', '_ _\n |\n_|_', '_ _\n |\n_|', '|_/\n| \\', '|\n|_', '|\\/|\n|  |', '|\\ |\n| \\|', ' _\n| |\n|_|', ' _\n|_)\n|', ' _\n| |\n|_\\', ' _\n|_)\n| \\', ' _\n|_\n _|', '_ _\n |\n |', '| |\n|_|', '\\  /\n \\/', '\\    /\n \\/\\/', '\\_/\n/ \\', '\\ /\n |', '_\n /\n/_']
        self._upper_font_3row = dict(zip(self._upper_ascs, self._upper_3row))

    def randstr(self):
        random.seed(time.time())

        s = self._alnum

        l = []
        i = random.randint(self._limit, self._offset)
        while i:
            l.append(random.choice(s))
            i -= 1
        
        return ''.join(l)


    def _ascii(self, string:str=None):
        if not string:
            string = self.randstr()
        return string

    def _clock(self, string:str=None):
        if not string:
            string = self.randstr()
        return [''.join('     | _  _||  | ||_ |_|'[(7&(d>>l))*3:][:3]for d in[255&0xb4b61fa637bdbbbf89b7b3399b9e09af>>int(x,16)*8 for x in string]) for l in[6,3,0]]


class TestAA(unittest.TestCase):
    def setUp(self):
        self._limit = 2
        self._offset = 8
        self._mode = None
        self._aa = AA(self._mode, self._limit, self._offset)

    def tearDown(self):
        del self._aa

    def test_randstr(self):
        result = self._aa.randstr()
        length = len(result)
        self.assertGreaterEqual(length, self._limit, 'len(result) >= limit')
        self.assertLessEqual(length, self._offset, 'len(result) <= limit')

    def test_ascii(self):
        data = 'crown.hg@gmail.com'
        result = self._aa._ascii(data)
        self.assertEqual(result, data, 'ascii input and output match')

    def test_clock(self):
        data = 'abcd'
        result = [' _     _    ', '|_||_ |   _|', '| ||_||_ |_|']
        self.assertListEqual(self._aa._clock(data), result, 'clock input and output match')
        


def test():
    # unittest.main()
    pass

def main():
#    test()
    # aa = AA('clock')
    # result = aa._clock('abcd')
    # print('\n'.join(result))
    # print('-------------------')
    # fonts = aa._font_3row
    # print(repr(fonts))
    # print('\n'.join(fonts))
    # print()
    # del aa
    alnum = Alnum()
    alnum.limit = 4
    print(alnum.randstr())
    print('output', repr(alnum.output()))
    del alnum
    return 0

if '__main__' == __name__:
    status = main()
    sys.exit(status)
