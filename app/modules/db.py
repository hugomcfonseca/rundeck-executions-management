#!/usr/bin/python3

from mysql.connector import errorcode, connect, Error


class DatabaseConn(object):
    '''
    Class to initialize and manage all operations in
    Rundeck database.
    '''

    _connection = None
    _session = None

    def __init__(self, dbname, user, password, host='127.0.0.1', port=3306):
        '''Initialization of global variables'''
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port

        self.open()

    def open(self):
        '''Open a new connection session to database'''
        try:
            self._connection = connect(user=self._user, password=self._password,
                                       database=self._dbname, host=self._host, port=self._port)
            self._session = self._connection.cursor()
        except Error as err:
            self._connection = False
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self._session = 'Something is wrong with your user name or password'
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self._session = 'Database does not exist'
            else:
                self._session = err

    def close(self):
        '''Close both session and connection to database'''
        self._session.close()
        self._connection.close()

    def query(self, query):
        '''Return results from a given query'''
        if not self._connection.is_connected or not self._session:
            self.open()

        self._session.execute(query)

        return self._session

    def apply(self):
        '''Commit changes in database'''
        self._connection.commit()
