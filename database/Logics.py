from database.DatabaseZ import DatabaseZ
from base64 import b64encode
from datetime import date
from decimal import Decimal

class adminAdministrador(DatabaseZ):
    """Administrador de la cuenta Administrador
    -----
    Tiene acceso a todas las cuentas y al la de Administrador
    """

    def __init__(self):
        self.database = DatabaseZ()
        self.adminClientes = adminClientes()
        self.adminTrabajadores = adminTrabajadores()

    def verify(self, correo, contra, picture = False):
        """Verifica si el par Correo-Contraseña pertenece a algún usuario de cualquier clase
        ----
        Devuelve un diccionario que que contiene :
        {"encontrado": encontrado, "permitido": contraseña_coincide, "user": diccionario_datos_usuario, "tipo": string_tipo_usuario}
        """

        encontrado = False
        permitido = False
        tipo = None
        lista = self.adminClientes.getUserbyCorreo(correo, picture)
        if len(lista) == 0:
            lista = self.adminTrabajadores.getWorkerbyCorreo(correo, picture)
            if len(lista) == 0:
                lista = self.getAdminByCorreo(correo, picture)
                if not len(lista) == 0:
                    encontrado = True
                    tipo = "admin"
            else:
                encontrado = True
                tipo = "worker"

        else:
            encontrado = True
            tipo = "user"

        if encontrado:
            permitido = self.checkContra(contra, lista)

        encontrado = len(lista) > 0
        permitido = encontrado and permitido

        conclusion = {
            "encontrado": encontrado,
            "permitido": permitido,
            "user": lista,
            "tipo": tipo,
        }
        return conclusion

    def insertAdmin(self, nombre, apellido, correo, contra, foto):
        sql = """INSERT INTO `hermes`.`administradoes` (`Nombre`, `Apellido`, `Correo`, `Contrasena`, `foto`) VALUES (%s, %s, %s, %s, %s);"""
        val = (nombre, apellido, correo, contra, foto)
        database = self.database
        success = database.executeMany(sql, val)
        return success

    def updateAdmin(self, idup, nombre, apellido, correo, contra):
        sql = f"""UPDATE `hermes`.`administradoes` SET `Nombre` = %s, `Apellido` = %s, `Correo` = %s, `Contrasena` = %s WHERE (`idAdministradoes` = '{idup}');"""
        val = (nombre, apellido, correo, contra)
        database = self.database
        success = database.executeMany(sql, val)
        return success

    def updateAdminPicture(self, idup, foto):
        sql = f"""UPDATE `hermes`.`administradoes` SET `foto` = %s WHERE (`idAdministradoes` = '{idup}');"""
        
        database = self.database
        success = database.executeMany(sql, foto)
        return success

    def deleteAdmin(self, idDel):
        sql = f"DELETE FROM `hermes`.`administradoes` WHERE (`idAdministradoes` = '{idDel}');"
        database = self.database
        success = database.executeNonQueryBool(sql)
        return success

    def getAdminByCorreo(self, correo, picture = True):
        """Debuele una lista con los datos del usuario con ese correo"""
        database = self.database
        sql = f"SELECT * FROM hermes.administradoes where administradoes.Correo = '{correo}' limit 1;"
        data = database.executeQuery(sql)
        lista = {}
        if len(data) > 0:
            lista = self.convertTuplaToList(data[0], picture)
        return lista
    
    def getAdminById(self, idAdmin, picture = True):
        """Debuele una lista con los datos del usuario con ese correo"""
        database = self.database
        sql = f"SELECT * FROM hermes.administradoes where administradoes.idAdministradoes = '{idAdmin}' limit 1;"
        data = database.executeQuery(sql)
        lista = {}
        if len(data) > 0:
            lista = self.convertTuplaToList(data[0], picture)
        return lista

    def getAllAdmins(self):
        """Debuele una lista de diccionarios con todos los administradores"""
        database = self.database
        sql = f"SELECT * FROM hermes.administradoes;"
        data = database.executeQuery(sql)
        lista = {}
        final = []
        if len(data) > 0:
            for x in data:
                lista = self.convertTuplaToList(x, True)
                final.append(lista)
        return final

    def checkContra(self, contra, lista):
        valor = contra == lista["contra"]
        return valor

    def convertTuplaToList(self, tupla, picture = True):
        lista = {}
        if picture:
            foto= b64encode(tupla[5]).decode("utf-8")
        else:
            foto= None

        if tupla is not None:
            lista = {
                "id": tupla[0],
                "nombre": tupla[1],
                "apellido": tupla[2],
                "correo": tupla[3],
                "contra": tupla[4],
                "foto": foto
            }
        return lista

    def searchWorker(self, word, limit = "20"):
        """
        Devuelve una lista con todos los trabajadores relacionados a una palabra
        ---
        La palabra se bueca en el dui, el nomre, el apellido, el celular, la dirección, el correo, la descripción o la categoría
        "limit" ajusta el número de trabajadores devueltos
        """
        admin = self.adminTrabajadores
        lista = admin.fetchAllWorkersByWord(word, limit)

    def revocarLicenciaDeudores(self):
        sql = "update hermes.membresias set membresias.Vigencia = 0 where datediff(now(), UltimoPago) > 31 and membresias.vigencia = 1;"
        exito = self.database.executeNonQueryBool(sql)
        return exito
    
    def getTopN(self, n = 5):
        adminT = self.adminTrabajadores
        sql = f"""SELECT citas.Trabajador, count(distinct(citas.idCitas)) as sumCitas 
                from citas  
                where datediff(now(), citas.Fecha) < 31 and citas.finalizada = 'True'
                group by citas.Trabajador 
                order by sumCitas desc limit {n};"""
        data = self.database.executeQuery(sql)
        top5trabajadores = []
        for x in data:
            trabajador = adminT.fetchAllWorkersByWord(str(x[0]), limit = 1, kind = ['trabajadores.idTrabajadores'] , aprox = False, cat = False)
            conclusion = trabajador[0]
            conclusion["cantidadCitas"]  = x[1]
            
            top5trabajadores.append(conclusion)

        return top5trabajadores

    def getStats(self):
        dicc = {"TrabajadoresMora": self.getNumeroTrabajadoresMora(),
                "TrabajadoresNoAcceso": self.getNumeroTrabajadoresNoAcceso(),
                "IngresosMes": self.ingresosMes()}
        return dicc

    def getNumeroTrabajadoresMora(self):
        sql = """SELECT count(distinct(membresias.idMembresias)) as morosos FROM hermes.trabajadores 
                inner join membresias on membresias.idMembresias = trabajadores.Membresia
                where datediff(now(), membresias.UltimoPago) > 31 and membresias.vigencia = 1;"""
        data = self.database.executeQuery(sql)
        valor = int(data[0][0])
        return valor
    
    def getNumeroTrabajadoresNoAcceso(self):
        sql = """SELECT count(distinct(membresias.idMembresias)) as morosos FROM hermes.trabajadores 
                inner join membresias on membresias.idMembresias = trabajadores.Membresia
                where membresias.Membresia = "AAAA-0000-0000";"""
            
        data = self.database.executeQuery(sql)
        valor = int(data[0][0])
        return valor

    def ingresosMes(self):
        sql = """SELECT sum(monto) as total FROM hermes.pagos
                where month(Fecha) = month(now());"""
        data = self.database.executeQuery(sql)
        valor = Decimal(data[0][0])
        return valor

    def getTrabajadoresSinAcceso(self, limit = "30"):
        admin = self.adminTrabajadores
        trabajadores = admin.fetchAllWorkersByWord("0", limit, ['trabajadores.aceptado'], mode = "asc", aprox = False, cat = False)
        return trabajadores

    def getTrabajadoresConAcceso(self, limit = "30", modo = "asc"):
        admin = self.adminTrabajadores
        trabajadores = admin.fetchAllWorkersByWord("1", limit, ['trabajadores.aceptado'], mode = modo, aprox = False, cat = False)
        return trabajadores
    
    def getImages(self):
        sql = "SELECT * FROM hermes.imagenes;"
        data = self.database.executeQuery(sql)
        dicc = {
            "logo": b64encode(data[0][1]).decode("utf-8"),
            "pared": b64encode(data[1][1]).decode("utf-8"),
            "icono": b64encode(data[2][1]).decode("utf-8"),
            "logoYnombre": b64encode(data[3][1]).decode("utf-8")
        }
        return dicc

    

class adminClientes(DatabaseZ):
    """Aministración de los clientes en la base de datos
    ----
    """

    def __init__(self):
        self.database = DatabaseZ()

    def insert(self, dui, nombre, apellido, celular, direccion, correo, contrasena, departamento, municipio, genero, foto=None ):
        """ Inserta los componentes de un cliente en la base de datos
        -------
        Devuelve True si se ejecutó con éxito y false si no se hicieron cambios"""
        success = False
        if  foto == "":
            sql = """INSERT INTO hermes.clientes 
            (`DUI`, `Nombre`, `Apellido`, `Celular`, `Direccion`, `Correo`, `Contrasena`, `Departamento`, `Municipio`, `Genero` )  
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            val = (dui, nombre, apellido, celular, direccion, correo, contrasena, departamento, municipio, genero)
        else:
            sql = """INSERT INTO hermes.clientes 
            (`DUI`, `Nombre`, `Apellido`, `Celular`, `Direccion`, `Correo`, `Contrasena`, `Departamento`, `Municipio`, `Foto`, `Genero` ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

            val = ( dui, nombre, apellido, celular, direccion, correo, contrasena, departamento, municipio, foto, genero)

        database = self.database
        success = database.executeMany(sql, val)
        return success

    def getUserbyCorreo(self, correo, picture = True):
        """Debuele una lista con los datos del usuario con ese correo"""
        database = self.database
        sql = f"""SELECT clientes.*, departamentos.Nombre as dep, municipios.Nombre as mun FROM hermes.clientes 
                    inner join hermes.departamentos on departamentos.idDepartamento = clientes.Departamento
                    inner join hermes.municipios on municipios.idMunicipio = clientes.Municipio
                    where clientes.Correo = '{correo}' limit 1;"""
        data = database.executeQuery(sql)
        lista = {}
        if len(data) > 0:
            lista = self.convertTuplaToList(data[0],picture)
        return lista

    def deleteCliente(self, idDel):
        sql = f"DELETE FROM `hermes`.`clientes` WHERE (`idClientes` = '{idDel}');"
        database = self.database
        success = database.executeNonQueryBool(sql)
        return success

    def getAllClientes(self):
            """Debuele una lista de diccionarios con todos los clientes"""
            database = self.database
            sql = f"SELECT * FROM hermes.clientes;"
            data = database.executeQuery(sql)
            lista = {}
            final = []
            if len(data) > 0:
                for x in data:
                    lista = self.convertTuplaToDicc(x, True)
                    final.append(lista)
            return final

    def convertTuplaToDicc(self, tupla, picture = True):
        if picture:
            foto = b64encode(tupla[8]).decode("utf-8")
        else:
            foto = None

        if tupla is not None:
            lista = {
                "id": tupla[0],
                "dui": tupla[1],
                "nombre": tupla[2],
                "apellido": tupla[3],
                "celular": tupla[4],
                "direccion": tupla[5],
                "correo": tupla[6],
                "contrasena": tupla[7],
                "foto": foto,
                "genero": tupla[11],
                "departamento": tupla[9],
                "municipio": tupla[10],
            }
        return lista

    def updateClientePicture(self, idcliente, picture):
        sql = f"""UPDATE `hermes`.`clientes` SET `foto` = %s WHERE (`idClientes` = '{idcliente}');"""
        
        database = self.database
        success = database.executeMany(sql, picture)
        return success

    def convertTuplaToList(self, tupla, picture = True):
        if picture:
            foto = b64encode(tupla[8]).decode("utf-8")
        else:
            foto = None

        if tupla is not None:
            lista = {
                "id": tupla[0],
                "dui": tupla[1],
                "nombre": tupla[2],
                "apellido": tupla[3],
                "telefono": tupla[4],
                "direccion": tupla[5],
                "correo": tupla[6],
                "contra": tupla[7],
                "foto": foto,
                "genero": tupla[11],
                "departamento": tupla[12],
                "municipio": tupla[13],
            }
        return lista

    def getImages(self):
        sql = "SELECT * FROM hermes.imagenes;"
        data = self.database.executeQuery(sql)
        dicc = {
            "logo": b64encode(data[0][1]).decode("utf-8"),
            "pared": b64encode(data[1][1]).decode("utf-8"),
            "icono": b64encode(data[2][1]).decode("utf-8"),
            "logoYnombre": b64encode(data[3][1]).decode("utf-8")
        }
        return dicc

    def getClienteById(self, idClientes, picture = True):
        """Debuele una lista con los datos del usuario con ese correo"""
        database = self.database
        sql = f"SELECT * FROM hermes.clientes where clientes.idClientes = '{idClientes}' limit 1;"
        data = database.executeQuery(sql)
        lista = {}
        if len(data) > 0:
            lista = self.convertTuplaToDicc(data[0], picture)
        return lista

    def updateCliente(self, idUp, dui, nombre, apellido, celular, direccion, correo, contra, departamento, municipio, genero):  
        sql = f"""UPDATE `hermes`.`clientes` SET `DUI` = %s, `Nombre` = %s, `Apellido` = %s, `Celular`=%s, `Direccion`=%s, `Correo`=%s ,
            `Contrasena`=%s , `Departamento`=%s , `Municipio`=%s, `Genero`=%s WHERE (`idClientes` = '{idUp}');"""
        val = (dui, nombre, apellido, celular, direccion, correo, contra, departamento, municipio, genero)
        database = self.database
        success = database.executeMany(sql, val)
        return success

    def updateusuario(self, datanueva):
        """ actualiza los campos de la cuenta de un usuario recibiendo un diccionario con los nuevos campos y el id"""
        database = self.database
        sql = """UPDATE hermes.clientes SET
            DUI=%s , Nombre=%s, Apellido=%s, Celular=%s, Direccion=%s, Correo=%s ,
            Contrasena=%s , Departamento=%s , Municipio=%s, Genero=%s WHERE idClientes=%s;"""
        val = (
            datanueva['dui'],
            datanueva['nombre'],
            datanueva['apellido'],
            datanueva['telefono'],
            datanueva['direccion'],
            datanueva['correo'],
            datanueva['contra'],
            datanueva['departamento'],
            datanueva['municipio'],
            datanueva['genero'],
            datanueva['id']
            )
            
        success = database.executeMany(sql,val)
        return success

    def getDepartamentoMunicipioCliente(self,idCliente):
        """ Obtiene el nombre del Departamento y Municipio de un cliente"""
        database = self.database
        sql=f"""SELECT clientes.idClientes,departamentos.Nombre,municipios.Nombre FROM hermes.clientes 
                left join hermes.departamentos on clientes.Departamento= departamentos.idDepartamento 
                left join hermes.municipios on clientes.Municipio=municipios.idMunicipio 
                WHERE clientes.idClientes='{idCliente}';"""
        data = database.executeQuery(sql)
        for x in data:
            Departamento = x[1]
            Municipio=x[2]
            
        return Departamento,Municipio

class adminTrabajadores(DatabaseZ):
    """
    Aministración de los trabajadores en la base de datos
    ----
    """

    def __init__(self):
        self.database = DatabaseZ()

    def insert( self, dui, nombre, apellido, celular, direccion, correo, contrasena, descripcion, departamento, municipio, genero, aceptado, membresia="AAAA-0000-0000", foto=None,):
        """ Inserta los componentes de un cliente en la base de datos
        -------
        Devuelve True si se ejecutó con éxito y false si no se hicieron cambios"""
        success = False
        fecha = date.today()
        fechaF = fecha.strftime("%d-%m-%Y")
        if foto == "":
            sql = """INSERT INTO `hermes`.`trabajadores` 
            (`DUI`, `Nombre`, `Apellido`, `Celular`, `Direccion`, `Correo`, `Contrasena`, `Descripcion`, `Departamento`, `Municipio`, `Genero`, `Aceptado`, `Membresia`, `fechaDeEntrada`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            val = ( dui, nombre, apellido, celular, direccion, correo, contrasena, descripcion, departamento, municipio, genero, aceptado, membresia, fechaF)
        else:
            sql = """INSERT INTO `hermes`.`trabajadores` 
            (`DUI`, `Nombre`, `Apellido`, `Celular`, `Direccion`, `Correo`, `Contrasena`, `Descripcion`, `Departamento`, `Municipio`, `Genero`, `Aceptado`, `Membresia`, `Foto`, `fechaDeEntrada`) 
            VALUES (%s, s, %s, %s, %s, s, %s, %s, %s, %s, %s, %s, %s, %s );"""
            val = (
                dui,
                nombre,
                apellido,
                celular,
                direccion,
                correo,
                contrasena,
                descripcion,
                departamento,
                municipio,
                genero,
                aceptado,
                membresia,
                foto,
                fechaF
            )

        database = self.database
        success = database.executeMany(sql, val)
        return success

    def getWorkerbyCorreo(self, correo, picture = True):

        """Debuele una lista con los datos del usuario con ese correo"""
        database = self.database
        sql = f"""
                SELECT trabajadores.*, departamentos.Nombre as dep, municipios.Nombre as mun FROM hermes.trabajadores 
                inner join hermes.departamentos on departamentos.idDepartamento = trabajadores.Departamento
                inner join hermes.municipios on municipios.idMunicipio = trabajadores.Municipio
                where trabajadores.Correo = '{correo}' limit 1;"""
        data = database.executeQuery(sql)
        lista = {}
        if len(data) > 0:
            lista = self.convertTuplaToDicc(data[0], picture)
        return lista

    def fetchAllWorkersByWord(self, word, limit = str(20), kind = [], order = "fechaDeEntrada", mode = "desc", aprox=True, cat = True):

        """"Lista de {limit} trabajadores con características que parescan a {word}
        ----
        {Kind} es la lista de lugares en que se buscará 
        Kind puede ser: ['trabajadores.DUI', 'trabajadores.Nombre', 'trabajadores.Apellido', 'trabajadores.Celular', 'trabajadores.Direccion', 'trabajadores.Descripcion', 'membresias.Membresia', 'municipios.nombre', 'departamentos.nombre']
        Si desea que la busqueda no incluya a categoria escriba cat = False en los argumentos
        Para buscar a un trabajador por su id escriba 'trabajadores.idTrabajadores' en kind
        La búsqueda se ordena con la fecha de entrada descendente. Para ajustar, el campo {order} es el campo de ordenamiento y {mode} es el modo de ordenamiento
        Si desea una búsqueda exacta ingrese False en aprox
        """
        database = self.database 
        if aprox:
            like = f"like  '{word.upper()}%'"
        else:
            like = f"= '{word.upper()}'"
        final = []

        if len(kind) == 0:
            lista = ['trabajadores.DUI', 'trabajadores.Nombre', 'trabajadores.Apellido', 'trabajadores.Celular', 'trabajadores.Direccion', 'trabajadores.Descripcion', 'membresias.Membresia', 'municipios.nombre', 'departamentos.nombre', 'categoria.nombre']
        else:
            lista = kind

        select = "trabajadores.idTrabajadores, trabajadores.DUI, trabajadores.Nombre, trabajadores.Apellido, trabajadores.Celular, trabajadores.Direccion, trabajadores.Correo, trabajadores.Contrasena, trabajadores.Descripcion, trabajadores.Genero, trabajadores.Foto, trabajadores.Aceptado,  membresias.Membresia, departamentos.nombre as depa, municipios.nombre as mun, trabajadores.trabajos"
        # Búsquedas generales
        for x in lista:

            sql = f"""  SELECT distinct {select}
                    FROM categorias 
                    right join trabajadores on trabajadores.idTrabajadores = categorias.Trabajador
                    left join categoria on categoria.idCategoria = categorias.Categoria
                    inner join hermes.departamentos on departamentos.idDepartamento = trabajadores.Departamento
                    inner join hermes.municipios on municipios.idMunicipio = trabajadores.Municipio
                    inner join hermes.membresias on membresias.idMembresias = trabajadores.Membresia
                    where {x} {like}
                    order by {order} {mode} limit {limit};"""
            # print(sql)
            
            data = database.executeQuery(sql)
            temporal = self.convertDataToList(data)
            final += temporal
            
        return final
    
    def convertDataToList(self, data):
        """De los datos devueltos de un select de trabajadores, devuelve una lista de diccionarios"""
        lista = []
        value = None
        numero = 0
        if len(data) > 0:
            for x in data:
                value = self.convertTuplaToDicc(x, numero = numero)
                lista.append(value)
                numero += 1
        return lista

    def convertTuplaToDicc(self, tupla, picture = True, numero = 0):
        """Converts a tuple to a dictionary"""
        if picture:
            foto = b64encode(tupla[10]).decode("utf-8")
        else:
            foto = None
        if tupla is not None:
            lista = {
                "id": tupla[0],
                "dui": tupla[1],
                "nombre": tupla[2],
                "apellido": tupla[3],
                "telefono": tupla[4],
                "direccion": tupla[5],
                "correo": tupla[6],
                "contra": tupla[7],
                "descripcion": tupla[8],  
                "genero": tupla[9],
                "foto":  foto,
                "aceptado": tupla[11],
                "membresia": tupla[12],
                "departamento": tupla[13],
                "municipio": tupla[14],
                "trabajos": tupla[15],
                "Categoría": self.getCategoriasById(tupla[0]),
                "numero": numero
            }
        return lista

    def convertTuplaToList(self, tupla, picture = True):
        lista = {}
        if picture:
            foto= b64encode(tupla[12]).decode("utf-8")
        else:
            foto= None

        if tupla is not None:
            lista = {
                "id": tupla[0],
                "dui": tupla[1],
                "nombre": tupla[2],
                "apellido": tupla[3],
                "telefono": tupla[4],
                "direccion": tupla[5],
                "correo": tupla[6], 
                "contra": tupla[7],
                "descripcion": tupla[8],
                "departamento": tupla[9],
                "municipio": tupla[10],  
                "genero": tupla[11],
                "foto":  foto,
                "aceptado": tupla[13],
                "membresia": tupla[14], 
                "trabajos": tupla[15],
                "fechaI":tupla[16]
            }
        return lista

    def getCategoriasById(self, idTrabajador):
        """Retorna la lista de categorias a las que pertenece el trabajador con el id especificado"""
        sql = f"""SELECT categoria.nombre FROM hermes.categorias
            left join categoria on categoria.idCategoria = categorias.categoria
            where categorias.Trabajador = '{idTrabajador}';"""
        
        data = self.database.executeQuery(sql)
        lista = []
        texto = ""
        for x in data:
            lista.append(x[0])
            texto += str(x[0])
        return lista
    
    def generarMembresiaEnTrabajador(self, idW):
        trabajador = self.fetchAllWorkersByWord(str(idW), limit='1', kind= ['trabajadores.idTrabajadores'], order='trabajadores.idTrabajadores', aprox=False, cat=False)
        membActual, exito = trabajador[0]['membresia'], False
        last = self.getLastMembresia()
        if membActual == "AAAA-0000-0000": # Esto significa que aún no se le ha asignado ninguna membresía
            new = self.createMembresia(last)
            sql = f"""  UPDATE hermes.membresias inner join hermes.trabajadores on trabajadores.Membresia = membresias.idMembresias
                        set membresias.Membresia = '{new}'
                        where trabajadores.idTrabajadores = '{idW}';"""
            exito = self.database.executeNonQueryBool(sql)
        return exito

    def createMembresia(self, last):
        # last = self.getLastMembresia()
        numeros_ok = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
        abecedario = {"A": "B", "B": "C", "C": "D", "D": "E", "E": "F", "F": "A"}
        letras = ['A', 'B', 'C', 'D', 'E', 'F']
        nueva, value, added, num="", "", False, 0
        for x in reversed(last):
            print(x)
            if x in numeros_ok:
                value = int(x)
                value += 1
                added = True
            elif x == '9':
                value = "0"
            elif x in letras:
                value = abecedario[x]
                num += 1
                added = not (value == "A") or (num > 3)
            else:
                value = '-'
            nueva += str(value)
            if added:
                break
        final = last[0:(14-len(nueva))] + nueva[::-1]
        return final
        
    def getLastMembresia(self):
        """Devuelve el valor de la última membresía ingresada"""
        database = self.database
        sql = """   SELECT membresias.Membresia FROM hermes.trabajadores 
                    inner join hermes.membresias on membresias.idMembresias = trabajadores.Membresia
                    order by membresias.Membresia desc limit 1;"""
        data = database.executeQuery(sql)
        membresia = data[0][0]
        return membresia

    def fragmentarMembersia(self, membresia):
        """Devuelve un diccionario con lo siguiente:
            {'membresia': '00-0000-0000', 'primeraParte': '00', 'segundaParte': '0000', 'terceraParte': '0000'}
        """
        dicc = {
        "membresia": membresia,
        "primeraParte": membresia[0:2],
        "segundaParte": membresia[3:7],
        "terceraParte": membresia[8:12] 
        }
        return dicc

    def getAllTrabajadores(self):
        """Devuelve una lista de diccionarios con todos los trabajadores"""
        database = self.database
        sql = f"SELECT * FROM hermes.trabajadores;"
        data = database.executeQuery(sql)
        lista = {}
        final = []
        if len(data) > 0:
            for x in data:
                lista = self.convertTuplaToList(x, True)
                final.append(lista)
        return final

    def getTrabajadorById(self, idTrabajador, picture = True):
        """Debuele una lista con los datos del usuario con ese correo"""
        database = self.database
        sql = f"SELECT * FROM hermes.trabajadores where trabajadores.idTrabajadores = '{idTrabajador}' limit 1;"
        data = database.executeQuery(sql)
        lista = {}
        if len(data) > 0:
            lista = self.convertTuplaToList(data[0], picture)
        return lista
    
    def getImages(self):
        sql = "SELECT * FROM hermes.imagenes;"
        data = self.database.executeQuery(sql)
        dicc = {
            "logo": b64encode(data[0][1]).decode("utf-8"),
            "pared": b64encode(data[1][1]).decode("utf-8"),
            "icono": b64encode(data[2][1]).decode("utf-8"),
            "logoYnombre": b64encode(data[3][1]).decode("utf-8")
        }
        return dicc

    def deleteTrabajador(self,idDel):
        """Elimina un trabajador"""
        database = self.database
        sql = f"""DELETE FROM `hermes`.`trabajadores` WHERE (`idTrabajadores` = {idDel});"""
        success = database.executeNonQueryBool(sql)
        return success

    def updateTrabajador( self, idup, dui, nombre, apellido, celular, direccion, correo, contra, descripcion, departamento, municipio, genero, aceptado, fechaDeEntrada ):
        sql = f"""UPDATE `hermes`.`trabajadores` SET `DUI` = %s,`Nombre` = %s, `Apellido` = %s, `Celular` = %s, `Direccion` = %s,`Correo` = %s,`Contrasena` = %s,`Descripcion` = %s,`Departamento` = %s,`Municipio` = %s, `Genero` = %s,`Aceptado` = %s,`fechaDeEntrada` = %s WHERE (`idTrabajadores` = '{idup}');"""
        val = (dui, nombre, apellido, celular, direccion, correo, contra, descripcion, departamento, municipio, genero, aceptado, fechaDeEntrada)
        database = self.database
        success = database.executeMany(sql, val)
        return success

    def updateTrabajadorPicture(self, idup, foto):
        sql = f"""UPDATE `hermes`.`Trabajadores` SET `foto` = %s WHERE (`idTrabajadores` = '{idup}');"""
   
        database = self.database
        success = database.executeMany(sql, foto)
        return success


class adminCategorias(DatabaseZ):
    
    def __init__(self):
        self.database = DatabaseZ()
        
    def getCategoriaConFoto(self):
        """Retorna una lista con los datos completos de las categorias (id,nombre,foto)"""
        database = self.database
        sql = "SELECT * FROM hermes.categoria;"
        data = database.executeQuery(sql)
        return data

    def convertirimagenes(self,listacategoria):
        """Retorna una lista con imagenes transformadas de las categorias (id,nombre,foto)"""
        listafinalcategorias=[]
        dicccategoriaactual=[]
        for x in listacategoria:
            image = b64encode(x[2]).decode("utf-8")
            dicccategoriaactual={
                "id":x[0], 
                "nombre":x[1],
                "imagen":image}
            listafinalcategorias.append(dicccategoriaactual)
        return listafinalcategorias
        
class adminOpciones(DatabaseZ):
    def __init__(self):
        self.database = DatabaseZ()

    def getMunicipios(self):
        """Retorna una lista de diccionarios con los datos de los municipios (id, nombre)"""
        database = self.database
        sql = "SELECT idMunicipio, Nombre FROM hermes.municipios;"
        data = database.executeQuery(sql)
        lista = self.listToDicc(data)
        return lista

    def getDepartamentos(self):
        """Retorna una lista de diccionarios con los datos de los municipios (id, nombre)"""
        database = self.database
        sql = "SELECT idDepartamento, Nombre FROM hermes.departamentos;"
        data = database.executeQuery(sql)
        lista = self.listToDicc(data)
        return lista

    def getCategorias(self):
        """Retorna una lista de diccionarios con los datos de las categorias (id, nombre)"""
        database = self.database
        sql = "SELECT idCategoria,Nombre FROM hermes.categoria;"
        data = database.executeQuery(sql)
        lista = self.listToDicc(data)
        return lista

    def listToDicc(self, data):
        """Convierte la lista de tuplas a una lista de diccionarios
        -----
        Advertencia: Solo aplicable a tuplas que contengan id, nombre
        """
        lista = []
        for x in data:
            dicc = {"id": x[0], "nombre": x[1]}
            lista.append(dicc)
        return lista

class adminCitas(DatabaseZ):
    def __init__(self):
        self.database = DatabaseZ()
    
    def getCitasCliente(self, idCliente):
        """Retorna una lista de diccionarios con los datos de las citas y trabajadores"""
        database = self.database
        sql = f"""SELECT idCitas,Fecha,Hora,Finalizada,DescripcionTrabajo,Confirmacion,Cliente,idTrabajadores,
                Nombre,Apellido,Descripcion,Departamento,Municipio,Foto,trabajos,fechaDeEntrada FROM hermes.citas 
                left outer join hermes.trabajadores on trabajador=idTrabajadores WHERE Cliente='{idCliente}';"""
        data = database.executeQuery(sql)
        CitasCliente= self.creardiccsCitasClientes(data)
        CitasClienteTipos = self.clasificarcitasCliente(CitasCliente)
        return CitasClienteTipos
    
    def getidTrabajadoresClientesExistentes(self):
        """Retorna dos listas con los id de los trabajadores y clientes existentes"""
        database = self.database
        sql1 = "SELECT idTrabajadores FROM hermes.trabajadores;"
        idTrabajadoresExistentes = database.executeQuery(sql1)

        sql2 = f"""SELECT idClientes FROM hermes.clientes;"""
        idClientesExistentes = database.executeQuery(sql2)

        return idTrabajadoresExistentes,idClientesExistentes

    def getAllCitas(self):
        """Retorna una lista de diccionarios con los datos de las citas"""
        database = self.database
        sql = "SELECT * FROM hermes.citas;"
        data = database.executeQuery(sql)
        allcitas = self.creardiccsAllCitas(data)
        return allcitas
    
    def getCitaById(self,idCita):
        """Busca una cita por su id y la regersa como diccionario"""
        database = self.database
        sql = f"""SELECT * FROM hermes.citas WHERE idCitas = '{idCita}';"""
        data = database.executeQuery(sql)
        citaBuscada ={}
        for x in data:
            citaBuscada = {
                    "idCitas": x[0],
                    "Fecha": x[1],
                    "Hora": x[2],
                    "Trabajador":x[3],
                    "Cliente":x[4],
                    "Finalizada":x[5],
                    "DescripcionTrabajo":x[6],
                    "Confirmacion":x[7],
                        }
        return citaBuscada
    
    def deleteCita(self,idCita):
        """Elimina una Cita"""
        database = self.database
        sql = f"DELETE FROM `hermes`.`citas` WHERE (`idCitas` = {idCita});"
        success = database.executeNonQueryBool(sql)
        return success

    def insertCita(self, datanueva):
        """Agrega una citas y returna True si se realiza correctamente"""
        database = self.database
        sql = """INSERT INTO hermes.citas (`Fecha`, `Hora`, `Trabajador`, `Cliente`, `Finalizada`,`DescripcionTrabajo`, `Confirmacion`) 
                 VALUES ( %s, %s, %s, %s, %s, %s, %s);"""
        val = (
            datanueva['Fecha'],
            datanueva['Hora'],
            datanueva['Trabajador'],
            datanueva['Cliente'],
            datanueva['Finalizada'],
            datanueva['DescripcionTrabajo'],
            datanueva['Confirmacion']
            )
        success = database.executeMany(sql,val)
        return success

    def updateCitas(self, datanueva):
        """Actualiza la informacion de las citas y returna True si se realiza correctamente"""
        database = self.database
        sql = """UPDATE hermes.citas SET
            Fecha=%s , Hora=%s, Trabajador=%s, Cliente=%s, Finalizada=%s, DescripcionTrabajo=%s ,
            Confirmacion=%s WHERE idCitas=%s;"""
        val = (
            datanueva['Fecha'],
            datanueva['Hora'],
            datanueva['Trabajador'],
            datanueva['Cliente'],
            datanueva['Finalizada'],
            datanueva['DescripcionTrabajo'],
            datanueva['Confirmacion'],
            datanueva['idCitas']
            )
        success = database.executeMany(sql,val)
        return success

    def creardiccsAllCitas(self, lista):
        """Crea una lista de diccionarios de todas las citas"""
        listafinal=[]
        if lista is not None:
            for x in lista:
                dicc = {
                    "idCitas": x[0],
                    "Fecha": x[1],
                    "Hora": x[2],
                    "Trabajador":x[3],
                    "Cliente":x[4],
                    "Finalizada":x[5],
                    "DescripcionTrabajo":x[6],
                    "Confirmacion":x[7],
                }
                listafinal.append(dicc)
        return listafinal

    def creardiccsCitasClientes(self, lista):
        """Crea una lista de diccionarios de las citas del cliente"""
        listafinal=[]
        if lista is not None:
            for x in lista:
                dicc = {
                    "idCitas": x[0],
                    "Fecha": x[1],
                    "Hora": x[2],
                    "Finalizada": x[3],
                    "DescripcionTrabajo": x[4],
                    "Confirmacion": x[5],
                    "Cliente": x[6],
                    "idTrabajadores": x[7],
                    "NombreTrabajador": x[8],  
                    "ApellidoTrabajdor": x[9],
                    "DescripcionTrabajador": x[10],
                    "DepartamentoTrabajador": x[11],
                    "Municipiotrabajador": x[12],
                    "foto":  b64encode(x[13]).decode("utf-8"),
                    "TrabajosRealizados": x[14],
                    "FechadeEntrada": x[15],
                }
                listafinal.append(dicc)
        return listafinal

    def clasificarcitasCliente(self,listacitas):
        citaspendientes=[]
        citasnoconfirmadas=[]
        citaspasadas=[]
        if listacitas is not None:
            for cita in listacitas:
                if cita['Finalizada']=="False" and cita['Confirmacion']=="True":
                    citaspendientes.append(cita)
                elif cita['Confirmacion']=="False":
                    citasnoconfirmadas.append(cita)
                elif cita['Finalizada']=="True":
                    citaspasadas.append(cita)
        return citaspendientes,citasnoconfirmadas,citaspasadas



class adminMembresia(DatabaseZ):
    def __init__(self):
        self.database = DatabaseZ()

    def getAllMembresias(self):
        """Retorna una lista de diccionarios con los datos de las Membresias"""
        database = self.database
        sql = "SELECT * FROM hermes.membresias;"
        data = database.executeQuery(sql)
        lista = {}
        final = []
        if len(data) > 0:
            for x in data:
                lista = self.convertTuplaToList(x)
                final.append(lista)
        return final
    
    def getMembresiaById(self,idMembresias):
        """Busca una Membresia por su id y la regersa como diccionario"""
        database = self.database
        sql = f"""SELECT * FROM hermes.membresias WHERE idMembresias = '{idMembresias}';"""
        data = database.executeQuery(sql)
        membresiaBuscada ={}
        for x in data:
            membresiaBuscada = {
                    "idMembresias": x[0],
                    "Membresia": x[1],
                    "Vigencia": x[2],
                    "UltimoPago":x[3]
            }
        return membresiaBuscada
    
    def deleteMembresia(self,idMembresias):
        """Elimina una Membresia"""
        database = self.database
        sql = f"DELETE FROM `hermes`.`membresias` WHERE (`idMembresias` = {idMembresias});"
        success = database.executeNonQueryBool(sql)
        return success

    def insertMembresia(self, datanueva):
        """Agrega una membresia y returna True si se realiza correctamente"""
        database = self.database
        sql = """INSERT INTO hermes.membresias (`Membresia`, `Vigencia`, `UltimoPago`) 
                 VALUES ( %s, %s, %s);"""
        val = (
            datanueva['Membresia'],
            datanueva['Vigencia'],
            datanueva['UltimoPago']
        )
        success = database.executeMany(sql,val)
        return success  

    def getImages(self):
        sql = "SELECT * FROM hermes.imagenes;"
        data = self.database.executeQuery(sql)
        dicc = {
            "logo": b64encode(data[0][1]).decode("utf-8"),
            "pared": b64encode(data[1][1]).decode("utf-8"),
            "icono": b64encode(data[2][1]).decode("utf-8"),
            "logoYnombre": b64encode(data[3][1]).decode("utf-8")
        }
        return dicc

    def updateMembresia(self, idup, Membresia, Vigencia, UltimoPago):
        sql = f"""UPDATE `hermes`.`membresias` 
        SET `Membresia` = %s,
         `Vigencia` = %s,
          `UltimoPago` = %s
           WHERE (`idMembresias` = '{idup}');"""
        val = (Membresia, Vigencia, UltimoPago)
        database = self.database
        success = database.executeMany(sql, val)
        return success


    def convertTuplaToList(self, tupla):
        lista = {}
        if tupla is not None:
            lista = {
                "idMembresias": tupla[0],
                "Membresia": tupla[1],
                "Vigencia": tupla[2],
                "UltimoPago": tupla[3],
            }
        return lista


class adminTarjetas(DatabaseZ):
    def __init__(self):
        self.database = DatabaseZ()

    def getAllCards(self):
        """Retorna una lista de diccionarios con los datos de las citas"""
        database = self.database
        sql = "SELECT * FROM hermes.tarjetas;"
        data = database.executeQuery(sql)
        allCards = self.diccForCards(data)
        return allCards

    def getCardById(self,idCard):
        """Busca una cita por su id y la regersa como diccionario"""
        database = self.database
        sql = f"""SELECT * FROM hermes.tarjetas WHERE idTarjetas = '{idCard}';"""
        data = database.executeQuery(sql)
        card ={}
        for x in data:
            card = {
                    "idTarjetas": x[0],
                    "Trabajador": x[1],
                    "Numero": x[2],
                    "DiaVencimiento":x[3],
                    "MesVencimiento":x[4],
                    "CVV":x[5],
                    "Tipo":x[6],
                    "Titular":x[7],
                        }
        return card

    def diccForCards(self, lista):
        """Crea una lista de diccionarios de todas las citas"""
        listafinal=[]
        if lista is not None:
            for x in lista:
                dicc = {
                    "idTarjetas": x[0],
                    "Trabajador": x[1],
                    "Numero": x[2],
                    "DiaVencimiento":x[3],
                    "MesVencimiento":x[4],
                    "CVV":x[5],
                    "Tipo":x[6],
                    "Titular":x[7],
                }
                listafinal.append(dicc)
        return listafinal

    
    def getIdWorkerForCards(self):
        database = self.database
        sql = "SELECT idTrabajadores FROM hermes.trabajadores;"
        idWorkerForCards = database.executeQuery(sql)
        return idWorkerForCards

    def deleteCard(self,idTarjetas):
        """Elimina una Cita"""
        database = self.database
        sql = f"DELETE FROM `hermes`.`tarjetas` WHERE (`idTarjetas` = {idTarjetas});"
        success = database.executeNonQueryBool(sql)
        return success

    def insertCard(self, datanueva):
        """Agrega una citas y returna True si se realiza correctamente"""
        database = self.database
        sql = """INSERT INTO hermes.tarjetas (`Trabajador`, `Numero`, `DiaVencimiento`, `MesVencimiento`, `CVV`,`Tipo`, `Titular`) 
                 VALUES ( %s, %s, %s, %s, %s, %s, %s);"""
        val = (
            datanueva['Trabajador'],
            datanueva['Numero'],
            datanueva['DiaVencimiento'],
            datanueva['MesVencimiento'],
            datanueva['CVV'],
            datanueva['Tipo'],
            datanueva['Titular']

            )
        success = database.executeMany(sql,val)
        return success

    def updateMembresia(self, datanueva):
        """Actualiza la informacion de las membresias y returna True si se realiza correctamente"""
        database = self.database
        sql = """UPDATE hermes.membresias SET
            Membresia=%s , Vigencia=%s, UltimoPago=%s;"""
        val = (
            datanueva['Membresia'],
            datanueva['Vigencia'],
            datanueva['UltimoPago'],
            )
        success = database.executeMany(sql,val)
        return success


    def convertTuplaToList(self, tupla):
        lista = {}
        if tupla is not None:
            lista = {
                "idMembresias": tupla[0],
                "Membresia": tupla[1],
                "Vigencia": tupla[2],
                "UltimoPago": tupla[3],
            }
        return lista

    

    def updateCards(self, datanueva):
        """Actualiza la informacion de las citas y returna True si se realiza correctamente"""
        database = self.database
        sql = """UPDATE hermes.tarjetas SET
            Trabajador=%s , Numero=%s, DiaVencimiento=%s, MesVencimiento=%s, CVV=%s, Tipo=%s ,
            Titular=%s WHERE idTarjetas=%s;"""
        val = (
            datanueva['Trabajador'],
            datanueva['Numero'],
            datanueva['DiaVencimiento'],
            datanueva['MesVencimiento'],
            datanueva['CVV'],
            datanueva['Tipo'],
            datanueva['Titular'],
            datanueva['idTarjetas']
            )
        success = database.executeMany(sql,val)
        return success