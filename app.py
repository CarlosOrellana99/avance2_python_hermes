from flask import Flask, render_template, redirect, request
from database.Logics import adminAdministrador, adminClientes, adminTrabajadores, adminOpciones,adminCategorias,adminCitas, adminMembresia, adminTarjetas

app = Flask(__name__) 
app.secret_key = "Latrenge3456"

@app.route("/")
def index(): 
    admin = adminAdministrador()
    images = admin.getImages()

    return render_template('index.html', imagenes = images)

@app.route("/tablas/<lugar>")
def tablas(lugar): 
    admin = adminAdministrador()
    administradorCitas= adminCitas()
    adminMembresias = adminMembresia()
    images = admin.getImages()
    traba= adminTrabajadores()

    if lugar == "administradores":
        administradores = admin.getAllAdmins()
        return render_template('administradores.html', imagenes = images, administradores = administradores)
    elif lugar == "clientes":
        adminC = adminClientes()
        clientes = adminC.getAllClientes()
        adminO = adminOpciones()
        municipios = adminO.getMunicipios()
        departamentos = adminO.getDepartamentos()
        return render_template('clientes.html', imagenes = images, clientes = clientes, municipios = municipios, departamentos = departamentos)
    elif lugar == "trabajadores":
        trabajadores = traba.getAllTrabajadores()
        return render_template('trabajadores.html', imagenes = images, trabajadores = trabajadores)
    elif lugar == "tarjetas":
        adminCard = adminTarjetas()
        allCards = adminCard.getAllCards()
        idWorkerForCard = adminCard.getIdWorkerForCards()
        return render_template('tarjetas.html', imagenes = images, cards = allCards, idWorker = idWorkerForCard)
    elif lugar == "membresias":
        membresias = adminMembresias.getAllMembresias()
        return render_template('membresias.html', imagenes = images, membresias = membresias)
    elif lugar == "citas":
        citas = administradorCitas.getAllCitas()
        idTrabajadores,idClientes = administradorCitas.getidTrabajadoresClientesExistentes()
        return render_template('citas.html', allcitas=citas , imagenes = images , idClientes = idClientes, idTrabajadores= idTrabajadores)

# Edits
@app.route("/servlet/admin/<tipo>", methods=['POST', 'GET'])
def editAdmin(tipo):
    admin = adminAdministrador()
    if tipo == "register":
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        contra = request.form.get('password')
        imagen = request.files['imagen']
        foto = imagen.read()
        admin.insertAdmin(nombre, apellido, correo, contra, foto)
        return redirect("/tablas/administradores")
    elif tipo == "delete":
        idDel = request.args.get('id')
        print(idDel)
        admin.deleteAdmin(idDel)
        return redirect("/tablas/administradores")
    elif tipo == "update":
        idUp = request.args.get('id')
        administrador = admin.getAdminById(idUp)
        imagenes = admin.getImages()
        return render_template("editAdmin.html", administrador = administrador, imagenes = imagenes)
    elif tipo == "updateWD":
        idup = request.form.get('id')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        contra = request.form.get('password')
        admin.updateAdmin(idup, nombre, apellido, correo, contra)
        return redirect("/tablas/administradores")
    elif tipo == "updateWP":
        idup = request.form.get('id')
        picture = request.files['imagen']
        foto = picture.read()
        admin.updateAdminPicture(idup, foto)
        return redirect("/tablas/administradores")
    else:
        return redirect("/")

@app.route("/servlet/clientes/<tipo>", methods=['POST', 'GET'])
def editClientes(tipo):
    adminC = adminClientes()
    if tipo == "register":
        idUp = request.form.get('id')
        dui = request.form.get('dui')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        celular = request.form.get('celular')
        direccion = request.form.get('direccion')
        correo = request.form.get('correo')
        contra = request.form.get('password')
        imagen = request.files['imagen']
        foto = imagen.read()
        departamento = int(request.form.get('departamento'))
        municipio = int(request.form.get('municipio'))
        genero = request.form.get('genero')
        adminC.insert(dui, nombre, apellido, celular, direccion, correo, contra, departamento, municipio, genero, foto)
        return redirect("/tablas/clientes")
    elif tipo == "delete":
        idDel = request.args.get('id')
        print(idDel)
        valor = adminC.deleteCliente(idDel)
        if valor:
            return redirect("/tablas/clientes")
        else:
            admin = adminAdministrador()
            images = admin.getImages()
            error = "El cliente tiene tiene una cita, así que no puedes borrar su registro. Intenta borrar la cita primero."
            return render_template("error.html", error = error, imagenes = images)
    elif tipo == "update":
        idUp = request.args.get('id')
        cliente = adminC.getClienteById(idUp)
        imagenes = adminC.getImages()
        return render_template("editClientes.html", cliente = cliente, imagenes = imagenes)
    elif tipo == "updateWD":
        idUp = request.form.get('id')
        dui = request.form.get('dui')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        celular = request.form.get('celular')
        direccion = request.form.get('direccion')
        correo = request.form.get('correo')
        contra = request.form.get('password')
        departamento = int(request.form.get('departamento'))
        municipio = int(request.form.get('municipio'))
        genero = request.form.get('genero')
        adminC.updateCliente(idUp, dui, nombre, apellido, celular, direccion, correo, contra, departamento, municipio, genero)
        return redirect("/tablas/clientes")
    elif tipo == "updateWP":
        idUp = request.form.get('id')
        picture = request.files['imagen']
        foto = picture.read()
        adminC.updateClientePicture(idUp, foto)
        return redirect("/tablas/administradores")

    else:
        return redirect("/")

#Tabla de trabajadores



@app.route("/servlet/citas/<tipo>", methods=['POST', 'GET'])
def editCitas(tipo):
    administrarCitas = adminCitas()
    admin = adminAdministrador()
    images = admin.getImages()

    if tipo == "register":
        data = {
            "Fecha": request.form.get('Fecha'),
            "Hora": request.form.get('Hora'),
            "Trabajador": int(request.form.get('IdTrabajador')),
            "Cliente": int(request.form.get('IdCliente')),
            "Hora": request.form.get('Hora'),
            "DescripcionTrabajo": request.form.get('DescripcionTrabajo'),
            "Confirmacion": request.form.get('Confirmacion'),
            "Finalizada": request.form.get('Finalizada')
            }
        administrarCitas.insertCita(data)
        return redirect("/tablas/citas")

    elif tipo == "delete":
        idDel = int(request.args.get('id'))
        administrarCitas.deleteCita(idDel)
        return redirect("/tablas/citas")
    
    elif tipo == "update":
        idUpdt = int(request.args.get('id'))
        citaRegistro = administrarCitas.getCitaById(idUpdt)
        idTrabajadores,idClientes = administrarCitas.getidTrabajadoresClientesExistentes()
        print(citaRegistro)
        return render_template("editCitas.html", lacita = citaRegistro, imagenes = images , idClientes = idClientes, idTrabajadores= idTrabajadores)
    
    elif tipo=="updater":
        data = {
            "idCitas":request.form.get('id'),
            "Fecha": request.form.get('Fecha'),
            "Hora": request.form.get('Hora'),
            "Trabajador": int(request.form.get('IdTrabajador')),
            "Cliente": int(request.form.get('IdCliente')),
            "Hora": request.form.get('Hora'),
            "DescripcionTrabajo": request.form.get('DescripcionTrabajo'),
            "Confirmacion": request.form.get('Confirmacion'),
            "Finalizada": request.form.get('Finalizada')
            }
        update = administrarCitas.updateCitas(data)
        return redirect("/tablas/citas")

@app.route("/servlet/membresias/<tipo>", methods=['POST', 'GET'])
def editMembresia(tipo):
    administrarMembresias = adminMembresia()

    if tipo == "register":
        data = {
            "Membresia": request.form.get('Membresia'),
            "Vigencia": request.form.get('Vigencia'),
            "UltimoPago": request.form.get('UltimoPago')
            }
        success = administrarMembresias.insertMembresia(data)
        return redirect("/tablas/Membresias")

    elif tipo == "delete":
        idDel = int(request.args.get('idMembresias'))
        delete = administrarMembresias.deleteMembresia(idDel)
        return redirect("/tablas/membresias")
    
    elif tipo=="update":
        data = {
            "idMembresias":request.form.get('idMembresias'),
            "Membresia": request.form.get('Membresia'),
            "Vigencia": request.form.get('Vigencia'),
            "UltimoPago": request.form.get('UltimoPago')
            }
        update = administrarMembresias.updateMembresia(data)
        return redirect("/tablas/membresias")

@app.route("/servlet/tarjetas/<tipo>", methods=['POST', 'GET'])
def editCards(tipo):
    adminCards = adminTarjetas()
    admin = adminAdministrador()
    images = admin.getImages()

    if tipo == "register":
        data = {
            "Trabajador": request.form.get('Trabajador'),
            "Numero": request.form.get('Numero'),
            "DiaVencimiento": int(request.form.get('DiaVencimiento')),
            "MesVencimiento": int(request.form.get('MesVencimiento')),
            "CVV": request.form.get('CVV'),
            "Tipo": request.form.get('Tipo'),
            "Titular": request.form.get('Titular'),
            }
        adminCards.insertCard(data)
        return redirect("/tablas/tarjetas")

    elif tipo == "delete":
        idDel = int(request.args.get('id'))
        adminCards.deleteCard(idDel)
        return redirect("/tablas/tarjetas")

    elif tipo == "update":
        idUp = int(request.args.get('id'))
        registro = adminCards.getCardById(idUp)
        idWorker= adminCards.getIdWorkerForCards()
        return render_template("editCards.html", registro = registro , idUp = idUp, idWorker= idWorker, imagenes = images)
    
    elif tipo=="updateCard":
        
        data = {
            "idTarjetas":request.form.get('id'),
            "Trabajador": request.form.get('Trabajador'),
            "Numero": request.form.get('Numero'),
            "DiaVencimiento": request.form.get('DiaVencimiento'),
            "MesVencimiento": request.form.get('MesVencimiento'),
            "CVV": request.form.get('CVV'),
            "Tipo": request.form.get('Tipo'),
            "Titular": request.form.get('Titular'),
            }
        update = adminCards.updateCards(data)
        return redirect("/tablas/tarjetas")

if __name__=='__main__':
    app.run(debug=True)