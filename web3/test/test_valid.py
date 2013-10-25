import os
import sys
import unittest

sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../')))

from web3.lib.valid import REH5, VE, VF

data = {
        'date':{'1':('20120208', '2012-02-08', ), '0':('120208',)}, # 1, '2012-2-8'
        'time':{'1':('14:02', '14:02:30', '14:02:30.2354', '14:02:30.234Z', '14:02:30.234+08:00', '1402', '140230', '140230.235', '140230.235Z', '140230.235+05:00'), 
                '0':('24', '24:00', '23:60')}, # '25:00:00'
        'datetime':{'1':('2012-02-08 14:02:30', '2012-02-08T14:02:30', '2012-02-08T14:02:30.252', '2012-02-08T14:02:30.252Z', '2012-02-08T14:02:30.252+08:00'),
                    '0':('MON 2012-02-08#1402:30', )
            },
        'week':{'1':('2012W06', '2012w0603', '2012-W16', '2012-w16-03', '201206W',  '2012-06W'), '0':('201206',)}, # '2012-W6',
        'month':{'1':('201202', '2012-02'), '0':('1202', '12-2', '2012-2')},
        'email':{'1':('name@subdomail.com', 'l-f@name.com', 'l.f@name.com'), '0':('abc@', 'abc@abc')},
        'url':{'1':('http://abc.com', 'https://abc.com/def', 'http://abc.com/a.php'), '0':('ftp://', )}
        }


class TestREH5(unittest.TestCase):

    def setUp(self):
        self._data = data
        self._regex = REH5

    def tearDown(self):
        pass
    
    def test_reh5(self):
        for k, vs in self._data.items():
            re = self._regex.get(k, None)
            if re:
                for v in vs['1']:
                    self.assertTrue(re.search(v), 'pass re key:{} test:{}'.format(k, v))
                for v in vs['0']:
                    self.assertFalse(re.search(v), 'pass re key:{} test:{}'.format(k, v))

class TestVF(unittest.TestCase):
    def setUp(self):
        self._attr = {
            'email':{'type':'email', 'required':'', 'multiple':''},
            'website':{'type':'url'},
            'comment':{'type':'text', 'maxlength':4096},
            }

        self._values = {
            'email':['huanguan1978@163.com', 'crown.hg@gmail.com'],
            'website':['http://blog.xscripter.com'],
            'comment':['123456789'*10]
            }

    def tearDonw(self):
        pass

    def test_valid(self):
        vf = VF(self._attr, self._values)
        self.assertTrue(vf.valid, 'valid')

    def test_customError(self):
        attr = self._attr.copy()
        attr['website']['customError'] = "th's customError"        
        vf = VF(attr, self._values)
        self.assertFalse(vf.valid, 'valid')
        self.assertTrue(vf.message, 'exists message')

        def myfn(values:list):
            return 'my fn'
        
        attr = self._attr.copy()
        attr['website']['customError'] = myfn
        vf = VF(attr, self._values)
        self.assertFalse(vf.valid, 'valid')
        self.assertTrue(vf.message, 'exists message')

        attr = self._attr.copy()
        attr['website']['customError'] = self.ifn
        vf = VF(attr, self._values)
        self.assertFalse(vf.valid, 'valid')
        self.assertTrue(vf.message, 'exists message')


    def ifn(self, values:list):
        return repr(self._attr)

    def test_invalid(self):
        values = self._values.copy()
        values['website']=['1234567890']
        
        vf = VF(self._attr, values)
        self.assertFalse(vf.valid, 'invalid')
        self.assertTrue(vf.message, 'exists message')
        
        

class TestVE(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_valueMissing(self):
        ve = VE('email', [], 'required')
        self.assertTrue(ve.valueMissing, 'valueMissing')
        self.assertTrue(ve.validationMessage, 'Exists validationMessage')
        self.assertFalse(ve.valid, 'invalid')

    def test_typeMismatch(self):
        
        for k, vs in data.items():
            for v in vs['1']:
                ve = VE(k, [v], 'required')
                self.assertFalse(ve.typeMismatch, '1 mismatch type:{}, val:{}'.format(k, repr(v)))
                # self.assertTrue(ve.valid, 'valid')

            for v in vs['0']:
                ve = VE(k, [v], 'required')
                self.assertTrue(ve.typeMismatch, '0 match type:{}, val:{}'.format(k, repr(v)))
                # self.assertFalse(ve.valid, 'invalid')


    def test_patternMismatch(self):
        ve = VE('text', ['2012211'], 'required', pattern='\d{8}')
        self.assertFalse(ve.valid, 'invalid')
        self.assertTrue(ve.patternMismatch, 'patternMismatch')

    def test_tooLong(self):
        ve = VE('text', ['1234567890'*1000], 'required', maxLength=255)
        self.assertFalse(ve.valid, 'invalid')
        self.assertTrue(ve.tooLong, 'tooLong')

    def test_rangeUnderflow(self):
        ve = VE('number', ['0.2'], 'required', min=1)
        self.assertFalse(ve.valid, 'invalid')
        self.assertTrue(ve.rangeUnderflow, 'rangeUnderflow')

    def test_rangeOverflow(self):
        ve = VE('number', ['1.5'], 'required', max=1)
        self.assertFalse(ve.valid, 'invalid')
        self.assertTrue(ve.rangeOverflow, 'rangeOverflow')

    # def test_stepMismatch(self):
    #     ve = VE('number', ['A'], 'required', max=10, min=1, step=11)
    #     self.assertFalse(ve.valid, 'invalid')
    #     self.assertTrue(ve.stepMismatch, 'stepMismatch')

    def test_customError(self):
        ve = VE('number', ['1.5'], 'required')
        ve.setCustomValidity('set_custom_validity')
        self.assertFalse(ve.valid, 'invalid')
        self.assertTrue(ve.customError, 'customError')


    def test_not_required(self):
        ve = VE('email', ['crown.hg@gmail.com'])
        self.assertTrue(ve.valid, 'valid')


if '__main__' == __name__:
    unittest.main()
