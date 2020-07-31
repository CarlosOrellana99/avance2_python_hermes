from flask import Flask, render_template
from database.Logics import adminAdministrador, adminClientes, adminTrabajadores, adminOpciones,adminCategorias,adminCitas

app = Flask(__name__) 
app.secret_key = "Latrenge3456"

@app.route("/")
def index(): 
    admin = adminAdministrador()
    images = admin.getImages()

    return render_template('index.html', imagenes = images)

if __name__=='__main__':
    app.run(debug=True)