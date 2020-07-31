from flask import Flask, render_template
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
    images = admin.getImages()

    if lugar == "administradores":
        administradores = admin.getAllAdmins()
        return render_template('administradores.html', imagenes = images, administradores = administradores)
    elif lugar == "clientes":
        return render_template('clientes.html', imagenes = images)
    elif lugar == "trabajadores":
        return render_template('trabajadores.html', imagenes = images)
    elif lugar == "tarjetas":
        return render_template('tarjetas.html', imagenes = images)
    elif lugar == "membresias":
        return render_template('membresias.html', imagenes = images)
    elif lugar == "citas":
        return render_template('citas.html', imagenes = images)

# Edits
@app.route("/edit/administrador/<correo>")
def edit(correo):
    admin = adminAdministrador()
    images = admin.getImages()
    administrador = admin.getAdminByCorreo("correo")
    return render_template('editAdmin.html', imagenes = images, administrador = administrador)
    
@app.route("/servlet/admin/")
def editAdmin():
    pass


if __name__=='__main__':
    app.run(debug=True)