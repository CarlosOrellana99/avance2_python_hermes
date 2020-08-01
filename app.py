from flask import Flask, render_template, redirect, request
from database.Logics import adminAdministrador, adminClientes, adminTrabajadores, adminOpciones,adminCategorias,adminCitas

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
    images = admin.getImages()

    if lugar == "administradores":
        administradores = admin.getAllAdmins()
        return render_template('administradores.html', imagenes = images, administradores = administradores)
    elif lugar == "clientes":
        adminC = adminClientes()
        clientes = adminC.getAllClientes()
        return render_template('clientes.html', imagenes = images, clientes = clientes)
    elif lugar == "trabajadores":
        return render_template('trabajadores.html', imagenes = images)
    elif lugar == "tarjetas":
        return render_template('tarjetas.html', imagenes = images)
    elif lugar == "membresias":
        return render_template('membresias.html', imagenes = images)
    elif lugar == "citas":
        citas = administradorCitas.getAllCitas()
        return render_template('citas.html', allcitas=citas , imagenes = images)

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

if __name__=='__main__':
    app.run(debug=True)