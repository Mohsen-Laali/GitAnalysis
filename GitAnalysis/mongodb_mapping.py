from mongoengine import connect, disconnect


class EngineUtilities:

    DEFAULT_CONNECTION_NAME = 'default'

    def __init__(self, db_name, alias=None, host='None', port='None'):

        if alias is None:
            alias = self.DEFAULT_CONNECTION_NAME
        self.alias = alias
        self.db_name = db_name
        self.host = host
        self.port = port
        self.connect_db(db_name=db_name, alias=alias, host=host, port=port)

    def disconnect_db(self, alias=None):
        if alias is None:
            disconnect(alias=self.alias)

    def connect_db(self, db_name, alias=None, host='None', port='None'):
        if alias is None:
            alias = self.alias
        if host is None and port is None:
            connect(db=db_name, alias=alias)
        else:
            connect(db=db_name, alias=alias, host=host, port=port)



