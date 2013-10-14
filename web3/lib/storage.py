class Psycopg2(Storage):

    def __init__(self, database:str=':memory:', expires:int=3600):
        self.__database = database
        self.__expires = expires
        self.__handler = None
        super().__init__(database, expires)

    def __del__(self):
        super().__del__()

    @property
    def database(self):
        return self.__database

    @property
    def expires(self):
        return self.__expiress
    @expires.setter
    def expires(self, expires):
        self.__expires = expires
        return self.__expires

    @property
    def handler(self):
        if self.__handler:
            return self.__handler

        try:
            self.__handler = Psycopg2.connect(self.database)
        except:
            raise
        else:
            try:
                self.prepare(self.__handler)
            except:
                raise
        finally:
            if hasattr(self.__handler, 'close'):
                self.__handler.close()
        
        return self.__handler

    @handler.setter
    def handler(self, handler:object) -> object:
        handler.autocommit = True
        return super().handler(handler)

    @abc.abstractmethod
    def prepare(self, handler:object):
        sql = 'CREATE TABLE IF NOT EXISTS _sessions (id INT NOT NULL PRIMARY KEY, expires TIMESTAMP NOT NULL, data TEXT);'
        cursor = None
        try:
            cursor = handler.cursor()
        except:
            raise
        else:
            cursor.execute(sql)
        finally:
            if hasattr(cursor, 'close'):
                cursor.close()


    def get(self, id_:str, exists:bool=False) ->tuple:
        return super().get(id_, exists)

    def delete(self, id_:str) -> int:
        return super().delete(id_)
        
    def save(self, id_:str, data:str) -> int:
        row = self.get(id_, True)
        if row:
            sql = 'UPDATE _sessions SET data=? WHERE id=?'
            params = (data, id_)
        else:
            sql = "INSERT INTO _sessions(expires, data, id) VALUES((now() + INTERVAL '{} seconds'), ?, ?)".format(self.expires)
            params = (data, id_)

        cursor = self.handler.cursor()
        cursor.execute(sql, params)
        cursor.close()

        return cursor.rowcount

    def delay(self, id_:str) -> int:
        cursor = self.handler.cursor()

        sql = "DELETE FROM _sessions WHERE expires <= now()"
        cursor.execute(sql)

        sql = "UPDATE _sessions SET expires = expires + ({} - extract('epoch' from (expires - now()))) WHERE =? AND ({} - extract('epoch' from (expires - now()))) <={}".format(self.expires, self.expires)
        cursor.execute(sql, (id_, ))

        cursor.close()

        return cursor.rowcount


