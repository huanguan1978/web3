class Helper:

    def remote_user2id(self, email:str) ->int:
        '''query id where email '''
        link = self._env['wsgi.database']['_rw']
        
        params = (email,)
        sql = 'SELECT id FROM `user` WHERE email=?'
        record = link.execute(sql, params).fetchone()
        if record:
            return record[0]

    def remote_user2info(self, email:str) ->list:
        '''query id where email '''
        link = self._env['wsgi.database']['_rw']
        
        params = (email,)
        sql = 'SELECT * FROM `user` WHERE email=?'
        return link.execute(sql, params).fetchone()
