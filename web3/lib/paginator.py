class Paginator:
    '''
paginator=Paginator(url='/?p=',start=1, stop=10, step=5)
attrs = paginator.theme()
attrs['first']['class']='class="first"'
attrs['last']['class']='class="last"'
attrs['current']['wrap']={'element':'span', 'id':'', 'class':'', 'style':''}
print(paginator.paginator(attrs))
print(paginator.theme())



url parser:
        limit = [10, ];offset=[0,]
        if query_string:
            qs = parse_qs(query_string)
            limit = qs.get('limit', limit)
            offset = qs.get('offset', offset)
        
        limit = int(limit[0]);offset=start=int(offset[0]); offset=(offset-1)*limit if offset else 0

    '''

    def __init__(self, url, start, stop, step):
        self.__url = url        # 
        self.__start = start    # current page
        self.__stop = stop      # total rowcount
        self.__step = step      # page size
        self.__pages = []
        self.__count, self.__tail = divmod(self.__stop, self.__step)
        if self.__tail:self.__count+=1
        self.__opt = {
            'first':{'text':'first',     'id':'', 'class':'', 'style':''},
            'prev':{'text':'prev',       'id':'', 'class':'', 'style':''},
            'next':{'text':'next',       'id':'', 'class':'', 'style':''},
            'last':{'text':'last',       'id':'', 'class':'', 'style':''},
            'item':{'text':'item',       'id':'', 'class':'', 'style':'', 'wrap':{'element':'', 'id':'', 'class':'', 'style':''}},
            'current':{'text':'',        'id':'', 'class':'', 'style':'', 'wrap':{'element':'', 'id':'', 'class':'', 'style':''},  'href':'javascript:void(0);' },
            }


    def theme(self, theme=None):
        if theme:
            self.__opt = theme

        return self.__opt

    def paginator(self, theme=None):
        if self.__start < 1:
            self.__start = 1
        if self.__start == 1:
            if self.__stop <=self.__start * self.__step:
                return ''            
        if self.__start != self.__count:
            if self.__stop <=self.__start * self.__step:
                return ''

        theme = self.theme(theme)
        tf = theme['first'];tp = theme['prev'];tn = theme['next'];tl=theme['last'];tc = theme['current'];ti=theme['item']        

        if self.__start > -1:
            np = self.__start -1
            if np <1:
                np = 1 # np some number prev
            self.__pages.append('<a {} {} {} href="{}{}">{}</a>'.format(tf['id'], tf['class'], tf['style'], self.__url, 1, tf['text']))
            self.__pages.append('<a {} {} {} href="{}{}">{}</a>'.format(tp['id'], tp['class'], tp['style'], self.__url, np , tp['text']))

        limit_s = 1 if self.__start <=5 else self.__start-4

        if self.__count >= self.__start+5:
            limit_e = self.__start+5
        else:
            limit_e = self.__count
            if self.__start>=10:
                limit_s = self.__start -9
        
        for i in range(limit_s, limit_e+1):
            if self.__start == i:
                ss = i
                wc = tc.get('wrap', None)             # wrap current
                if wc and wc.get('element', None):
                    ss = '<{} {} {} {}>{}</{}>'.format(wc['element'], wc['id'], wc['class'], wc['style'], i, wc['element'])

                wc_href = tc.get('href', None)
                if not wc_href:
                    wc_href='{}{}'.format(self.__url, i)
                s = '<a {} {} {} href="{}">{}</a>'.format(tc['id'], tc['class'], tc['style'], wc_href, ss)

                self.__pages.append(s)
            else:
                self.__pages.append('<a {} {} {} href="{}{}">{}</a>'.format(ti['id'], ti['class'], ti['style'], self.__url, i, i))

        if self.__start <= self.__count:
            nl = i+1;
            if nl> self.__count:
                nl=i # nl some number next
            self.__pages.append('<a {} {} {} href="{}{}">{}</a>'.format(tn['id'], tn['class'], tn['style'], self.__url, nl, tn['text']))
            self.__pages.append('<a {} {} {} href="{}{}">{}</a>'.format(tl['id'], tl['class'], tl['style'], self.__url, self.__count, tl['text']))

        wi = ti.get('wrap', None)                     # wrap item
        if wi and wi.get('element', None):
            self.__pages = map(lambda x:"<{} {} {} {}>{}</{}>".format(wi['element'], wi['id'], wi['class'], wi['style'], x, wi['element']), self.__pages)

        return "".join(self.__pages)


# paginator=Paginator(url='/?p=',start=1, stop=10, step=5)
# attrs = paginator.theme()
# attrs['first']['class']='class="first"'
# attrs['last']['class']='class="last"'
# attrs['current']['wrap']={'element':'span', 'id':'', 'class':'', 'style':''}
# print(paginator.paginator(attrs))
# print(paginator.theme())
