import pymysql

class DatabaseZ:
    """ Base de datos MySql
        --------
        Fomato general, crea un módulo de base de datos
    """

    def __init__(self):
        self.params = {
            "host":"localhost",
            "user": "root",
            "passwd": "12345",
            "database": "hermes"
        }
        self.connection = self.createConnection()
        self.cursor = self.createCurosor()
    
    def createConnection(self):
        conn = pymysql.connect(
            host = self.params["host"],
            user = self.params["user"],
            passwd = self.params["passwd"],
            database = self.params["database"]
        )
        return conn
    
    def createCurosor(self):
        cursor = None
        if not self.connection is None:
            cursor = self.connection.cursor()
        return cursor
    
    def executeNonQueryBool(self, sql):
        """ Ejecuta un código que afecta a las columnas
            -----
            Debuelve un boolean si las columnas afectadas son más que cero
        """
        cursor = self.cursor
        success = False
        if cursor is not None:
            cursor.execute(sql)
            self.connection.commit()
            rows = cursor.rowcount
            success = rows > 0
        return success
    
    def executeNonQueryRows(self, sql):
        """ Ejecuta un código que afecta a las columnas
            -----
            Debuelve el número de columnas afectadas
        """
        cursor = self.cursor
        conn = self.connection
        if cursor is not None:
            cursor.execute(sql)
            conn.commit()
        return cursor.rowscount

    def executeQuery(self, sql):
        """ Ejecuta un código que debuelve datos
            -----
            Debuelve una lista de datos
        """
        cursor = self.cursor
        data = {}
        if cursor is not None:
            cursor.execute(sql)
            data = cursor.fetchall()
        return data

    def executeMany(self, sql, val):
        """ Ejecuta un código de tipo insert con %s en vez de valores
            -----
            La variable val requiere de una arreglo de datos ordenados que sustituirán los %s del código insert.
            Devuelve True si la cantidad de columnas afectadas es mayor que cero
        """
        cursor = self.cursor
        conn = self.connection
        succes = False
        if cursor is not None:
            cursor.execute(sql, val)
            conn.commit()
            
            rows = cursor.rowcount
            succes = rows > 0
        return succes