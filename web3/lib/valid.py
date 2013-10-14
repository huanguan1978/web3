#!/usr/bin/env python
'''valid html5 from
'''

import re
import datetime

from collections import defaultdict

REH5 = {
    'date':re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])$'),
    'time':re.compile('([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?([zZ]|([\+-])([01]\d|2[0-3])\D?([0-5]\d)?)?$'),
    'datetime':re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])(\D?([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?([zZ]|([\+-])([01]\d|2[0-3])\D?([0-5]\d)?)?)?$'),
    'month':re.compile('^(\d{4})\D?(0[1-9]|1[0-2])'),
    'week':re.compile('^(\d{4})\D?([W|w]([0-4][0-9]|5[0-2]))|(([0-4][0-9]|5[0-2])[W|w])'),
    'float':re.compile('^[-+]?[0-9]+[.]?[0-9]*([eE][-+]?[0-9]+)?$'), # eg:Matches 123 | -123.35 | -123.35e-2
    'color':re.compile('^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})'), # eg:#FFFFFF
    'email':re.compile('[\w-]+@([\w-]+\.)+[\w-]+'),            # eg:f-l@d.com | f.l@d.com
    'url':re.compile('^http[s]?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$'),
}

class VF:
    '''Validity Form
    ref:http://standardista.com/interlabs/#slide1
    html5:XMLSubmission,enctype = application/x-www-form+xml
    eg:
    formData = {'tel':'+86 020 110', 'email':'crown.hg@gmail.com,huanguan1978@163.com', 'url':'http://xscripter.com/blog/'}
    kwargs = {'tel': {'type':'tel'}, 'email':{'type':'email', 'required':'', 'multiple':''}, 'url':{'type':'url'}},
    # 'mychkbox':{'type':'checkbox', 'checked':'', 'value':'value'},
    # 'myradio':{'type':'radio', 'checked':'val', value:{'val':'name', 'val':'name', 'val':'name'}}
    # 'myselect':{'type':'select', , 'size':'', 'multiple':'', 'selected':[],
    #              'option':[{'val':'name', 'val':'name', 'val':'name', 'optgroup':'label'},
    #                        {'val':'name', 'val':'name', 'val':'name' }],
    }
    '''

    
    def __init__(self, attr:dict, data:dict):
        self.__attr = attr
        self.__data = data
        self.__vs = dict()

    @property
    def valid(self):
        for name, attr in self.__attr.items():
            values = self.__data.get(name, None)
            if values:
                ve = VE(attr['type'], values, kwargs=attr)

                customError = attr.get('customError', None)
                if customError:
                    if callable(customError): # hasattr(customError, '__call__')
                        customError = customError(values)
                    if customError:
                        ve.setCustomValidity(repr(customError))

                self.__vs[name] = dict(valid=ve.valid, msg=ve.validationMessage, obj=ve)

        if all([v for v in [ve['valid'] for n, ve in self.__vs.items()]]):
            return True

    @property
    def message(self):
        return {n:ve['msg'] for n, ve in self.__vs.items() if not ve['valid']}

    @property
    def invalid(self):
        if not self.valid:
            return self.message


class VE:
    '''Validity Element'''

    def __init__(self, type_:str, values:list, *args, **kwargs):
        self.__customError = None
        self.__validationMessage = defaultdict(list)

        self.__type = type_
        self.__values = values
        self.__args = args
        self.__kwargs = kwargs

        self.__valid = None     # cache status

        self.__t4 = ('text', 'password', 'hidden', 'file', 'checkbox', 'radio', 'submit', 'reset', 'button', 'image')
        self.__t5_txt = ('email', 'url', 'tel', 'search', 'color')
        self.__t5_obj = ('number', 'range',  'datetime',  'datetime-local', 'date', 'time', 'month', 'week')
        self.__t5 = self.__t5_txt + self.__t5_obj

    # def __call__(self):
    #     return self.valid()


    def checkValidity(self):
        if self.__valid:
            return self.__valid

        if self.willValidate:
            if not self.valueMissing and not self.typeMismatch and not self.patternMismatch and not self.tooLong and not self.stepMismatch and not self.rangeUnderflow and not self.rangeOverflow and not self.customError:
                self.__valid = True
                return True

    @property
    def validity(self) -> object:
        return self

    @property
    def valid(self) -> object:
        if self.__valid:
            return self.__valid
        return self.checkValidity()

    @property
    def willValidate(self) ->bool:
        if self.__valid:
            return False

        _args = {'required', }
        _kwargs = {'pattern', 'min', 'max', 'setp', 'required'}
        # _kwargs = {'pattern', 'min', 'max', 'setp', } ^ args
        if self.__args and (set(self.__args) & _args):
            return True
        if self.__kwargs and (set(self.__kwargs) & _kwargs):
            return True
        if self.__values:
            return True

    @property
    def valueMissing(self) ->bool:
        if self.willValidate:
            if ('required' in self.__args) or self.__kwargs.get('required',None):
                if not self.__values:
                    k = 'valueMissage'
                    if not self.__validationMessage[k]: self.__validationMessage[k].append('Please fill out this field')
                    return True

    @property
    def typeMismatch(self) ->bool:
        '''typeMismatch
        html4:(text, password, hidden, file, checkbox, radio, submit, reset, button, image)
        html5:(email, url, tel, search, number, range, color, datetime,  datetime-local, date, time, month, week)
        html5-attrs multiple(email, file), comma-separated list, eg:a@abc.com,b@abc.com
        html5-attrs max,min,step(number, range, datetime, datetime-local, date, time, month, week)
        html5-attrs checked (checkbox, radio)
        '''
        k = 'typeMismatch'
        if self.__type in self.__t4:
            if self.__type == 'file':
                pass
            elif self.__type == 'checkbox':
                pass
            elif self.__type == 'radio':
                pass
            else:
                pass
                # if not all([v.isalnum() for v in self.__values]):
                #     self.__validationMessage[k].append('Please enter an alnum.')
                #     return True
            return

        if self.__type in self.__t5:
            if self.__type == 'tel':
                if not all([self.__valid_tel(v) for v in self.__values]):
                    self.__validationMessage[k].append('Please enter a valid tel.')
                    return True

            elif self.__type == 'email':
                if not all([self.__valid_email(v) for v in self.__values]):
                    self.__validationMessage[k].append('Please enter an email address.')
                    return True

            elif self.__type == 'url':
                if not all([self.__valid_url(v) for v in self.__values]):
                    self.__validationMessage[k].append('Please enter a URL.')
                    return True
            elif self.__type == 'color':  # valid lowercase simple color
                if not all([self.__valid_color(v) for v in self.__values]):
                    self.__validationMessage[k].append('Please enter a color value.')
                    return True

            # http://wufoo.com/html5/types/4-date.html
            elif self.__type in self.__t5_obj:
                if not self.__valid_types(self.__type):
                    return True
            else:
                pass
                # if not all([v.isalnum() for v in self.__values]):
                #     self.__validationMessage[k].append('Please enter an alnum.')
                #     return True

            return

        # unknow input type
        # if not all([v.isalnum() for v in self.__values]):
        #     self.__validationMessage[k].append('unknow type,Please enter an alnum.')
        #     return True


    @property
    def patternMismatch(self) ->bool:
        if self.willValidate:
            pattern = self.__kwargs.get('pattern', None)
            if pattern:
                if not all([re.search(pattern, value) for value in self.__values]):
                    msg = self.__kwargs.get('title', None)
                    if not msg: msg = 'Please match the requested format'
                    k = 'patternMismatch'
                    if not self.__validationMessage[k]: self.__validationMessage[k].append(msg)
                    return True

    @property
    def tooLong(self) ->bool:
        if self.willValidate:
            maxLength = self.__kwargs.get('maxLength', None)
            if maxLength:
                if len(self.__values[0]) > maxLength:
                    k = 'tooLong'
                    if not self.__validationMessage[k]: self.__validationMessage[k].append(k)
                    return True

    @property
    def rangeUnderflow(self) ->bool:
        if self.willValidate:
            min_ = self.__kwargs.get('min', None)
            if min_:
                val = self.__values[0]
                if val < min_:
                    k = 'rangeUnderflow'
                    if not self.__validationMessage[k]: self.__validationMessage[k].append(k)
                    return True

    @property
    def rangeOverflow(self) ->bool:
        if self.willValidate:
            max_ = self.__kwargs.get('max', None)
            if max_:
                val = self.__values[0]
                if val > max_:
                    k = 'rangeOverflow'
                    if not self.__validationMessage[k]: self.__validationMessage[k].append(k)
                    return True

    @property
    def stepMismatch(self) ->bool:
        if self.willValidate:
            step = self.__kwargs.get('step', None)
            if step and self.__valid_float(setp):
                k = 'stepMismatch'
                if not self.__validationMessage[k]: self.__validationMessage[k].append(k)
                return True

    @property
    def customError(self) ->bool:
        return self.__customError
    @customError.setter
    def customError(self, customError) ->bool:
        self.__customError = customError
        return self.__customError

    def setCustomValidity(self, message:str):
        k = 'customError'
        if not self.__validationMessage[k]: self.__validationMessage[k].append(message)
        self.customError = True

    @property
    def validationMessage(self):
        return self.__validationMessage


    def __valid_tel(self, tel:str) -> bool:
        # tel char include digit or ' ' or '-', eg:123456, 020-123345, 020 1234 5678, 020-1234567-1234, 1234567#123
        v = tel.replace(' ', '').replace('(','').replace(')', '').replace('+', '').replace('#', '')
        if v.isdigit():
            return tel

    def __valid_color(self, color:str) -> bool:
        colors = {'A', 'B', 'C', 'D', 'E', 'F', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
        v = color.upper()
        if v.starts('#'):
            v = set(v[1:])
            length = len(v)
            if (length== 3) or (lenght==6):
                if v < colors:
                    return color

    def __valid_email(self, email:str) -> bool:
        vs = email.replace(' ', '').split('@')
        if len(vs)== 2:
            name, domain = vs
            if domain.find('.')>0:
                return email

    def __valid_url(self, url:str) -> bool:
        # ^http[s]?//\w*?\.\w*?/.*
        if url.replace(' ', '').startswith('http'):
            vs = url.split('//')
            if len(vs) ==2:
                v = vs[-1]
                ps = v.split('/') # parts
                if len(ps):
                    host = ps[0]
                    if host.find('.')>1:
                        return url
                
    def __valid_float(self, float_:str) -> float:
        try:
            float_ = float(float_)
        except ValueError as e:
            pass
        else:
            return float_

    def __valid_datetime(self, dt:str) -> object: # datetime
        # fmt:yyyy-mm-dd HH:MM or yyyy-mm-ddTHH:MM
        v = dt.upper()
        dts = v.split('T') if v.count('T') else v.split()
        if len(dts) == 2:
            d = self.__valid_date(dts[0])
            t = self.__valid_time(dts[1])
            if d and t:
                return datetime.datetime.combine(d, t)

    def __valid_month(self, month:str) -> object: # date
        # fmt:yyyy-mm, yyyymm
        month = month.replace('-', '')
        length = len(month)
        # y = month[:4]
        # if length == 5: month = y + '0' + month[4:]
        # if length == 7: month = y +  month[4:6] + '0' + month[6:]
        if length == 6: month += '01'
        try:
            month = datetime.datetime.strptime(month, '%Y%m%d').date()
        except ValueError as e:
            pass
        else:
            return month

    def __valid_week(self, week:str) -> object: # date 
        # fmt:yyyyWmm, yyyy-Wmm, yyyy-Wmm-d, yyyyWmmd, yyyymmW, yyyy-mmW, yyyymmWdd, yyyy-mmW-dd
        week = week.upper().replace('-', '')
        length = len(week)
        if week.count('W') and (length>=6):
            week = week.replace('W','')
            if week.isdigit():
                y,w = week[:4], week[4:6]
                d = week[6:]; w = int(w)
                d = int(d) if d else 0
                if (0<w<53) and (0<=d<8):
                    d = d+1+(w-1)*7  #total days
                    dt = datetime.timedelta(days=d) + datetime.date(int(y), 1, 1)
                    return dt
        
    def __valid_date(self, date:str) -> object:
        # fmt:yyyy-mm-dd
        d = date.replace('-', '')
        try:
            d = datetime.datetime.strptime(d, '%Y%m%d').date()
        except ValueError as e:
            pass
        else:
            return d

    def __valid_time(self, time:str) -> object:
        # fmt:HH:MM
        fmt = '%H%M%S'
        ms = tz = mstz = None
        time = time.upper().replace(':', '')
        if time.endswith('Z'):  # utc
            time = time[:-1]
        if time.count('.'):
            time, mstz = time.split('.')
        time += '0'*(6-len(time))
        if mstz:
            fmt += '%f'
            if mstz.count('-') or mstz.count('+'):
                fmt += '%z'

        try:
            time = datetime.datetime.strptime(time, '%H%M%S').time()
        except ValueError as e:
            pass
        else:
            return time

    def __valid_types(self, type_:str) -> bool:

        if type_ in self.__t5_obj:
            k = 'typeMismatch'
            step = self.__kwargs.get('step', None)
            if step:
                if not self.__valid_float(step):
                    self.__validationMessage[k].append('step(num)')
                    return False

            min_, max_ = self.__kwargs.get('max', None), self.__kwargs.get('max', None)
            if type_ in ('number', 'range'):
                values = [self.__valid_float(value) for value in self.__values]
                if not all(values):
                    self.__validationMessage[k].append('val(num)')
                    return False
                self.__values = values

                if max_:
                    max_ = self.__valid_float(max_)
                    if not max_:
                        self.__validationMessage[k].append('max(num)')
                        return False
                    self.__kwargs['max'] = max_
                if min_:
                    min_ = self.__valid_float(min_)
                    if not min_:
                        self.__validationMessage[k].append('min(num)')
                        return False
                    self.__kwargs['min'] = min_
                return True

            if type_.startswith('datetime'):
                values = [self.__valid_datetime(value) for value in self.__values]
                if not all(values):
                    self.__validationMessage[k].append('val(datetime)')
                    return False
                self.__values = values
                
                if max_:
                    max_ = self.__valid_datetime(max_)
                    if not max_:
                        self.__validationMessage[k].append('max(datetime)')
                        return False
                    self.__kwargs['max'] = max_
                if min_:
                    min_ = self.__valid_datetime(min_)
                    if not min_:
                        self.__validationMessage[k].append('min(datetime)')
                        return False
                    self.__kwargs['min'] = min_
                return True

            if type_ == 'time':
                values = [self.__valid_time(value) for value in self.__values]
                if not all(values):
                    self.__validationMessage[k].append('val(time)')
                    return False
                self.__values = values

                if max_:
                    max_ = self.__valid_time(max_)
                    if not max_:
                        self.__validationMessage[k].append('max(time)')
                        return False
                    self.__kwargs['max'] = max_
                if min_:
                    min_ = self.__valid_time(min_)
                    if not min_:
                        self.__validationMessage[k].append('min(time)')
                        return False
                    self.__kwargs['min'] = min_
                return True

            if type_ == 'date':
                values = [self.__valid_date(value) for value in self.__values]
                if not all(values):
                    self.__validationMessage[k].append('val(date)')
                    return False
                self.__values = values
                
                if max_:
                    max_ = self.__valid_date(max_)
                    if not max_:
                        self.__validationMessage[k].append('max(date)')
                        return False
                    self.__kwargs['max'] = max_
                if min_:
                    min_ = self.__valid_date(min_)
                    if not min_:
                        self.__validationMessage[k].append('min(date)')
                        return False
                    self.__kwargs['min'] = min_
                return True

            if type_ == 'month':
                values = [self.__valid_month(value) for value in self.__values]
                if not all(values):
                    self.__validationMessage[k].append('val(month)')
                    return False
                self.__values = values

                if max_:
                    max_ = self.__valid_month(max_)
                    if not max_:
                        self.__validationMessage[k].append('max(month)')
                        return False
                    self.__kwargs['max'] = max_
                if min_:
                    min_ = self.__valid_month(min_)
                    if not min_:
                        self.__validationMessage[k].append('min(month)')
                        return False
                    self.__kwargs['min'] = min_
                return True

            if type_ == 'week':
                values = [self.__valid_week(value) for value in self.__values]
                if not all(values):
                    self.__validationMessage[k].append('val(week)')
                    return False
                self.__values = values
                
                if max_:
                    max_ = self.__valid_week(max_)
                    if not max_:
                        self.__validationMessage[k].append('max(week)')
                        return False
                    self.__kwargs['max'] = max_

                if min_:
                    min_ = self.__valid_week(min_)
                    if not min_:
                        self.__validationMessage[k].append('min(week)')
                        return False
                    self.__kwargs['min'] = min_
                return True
