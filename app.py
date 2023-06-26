import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory # obtener info de la imagen

# session es para que se guarde una session en el navegador y quede abierta
# es decir, cuando se loguee el usuario, mantenemos los valores de usuario y password
# mientras q el usuario navegue por la pagina o cierre navegador

app=Flask(__name__)
app.secret_key="webconpython"
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='site'
mysql.init_app(app)

@app.route('/')
def inicio():
    return render_template('site/index.html')

@app.route('/img/<image>')
def images(image):
    print(image)
    return send_from_directory(os.path.join('templates/site/img'), image)

@app.route('/books')
def books():

    conection=mysql.connect()
    cursor=conection.cursor()
    cursor.execute("SELECT * FROM `books`")
    books=cursor.fetchall()
    conection.commit()

    return render_template('site/books.html', books=books)

@app.route('/us')
def us():
    return render_template('site/us.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect("/admin/login")
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario == "admin" and _password == "123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template("admin/login.html", mensaje="Acceso denegado")

@app.route('/admin/close')
def admin_login_close():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/books')
def admin_books():

    if not 'login' in session:
        return redirect("/admin/login")
    
    conection=mysql.connect()
    cursor=conection.cursor() # este cursor es para poder ejecutar la instruccion sql
    cursor.execute("SELECT * FROM `books`")
    books=cursor.fetchall() #recuperamos todos los libros y los almacenamos en la variable books
    conection.commit()
    print(books)
    return render_template('admin/books.html', books=books)

@app.route('/admin/books/save', methods=['POST'])
def admin_books_save():

    if not 'login' in session:
        return redirect("/admin/login")
    
    _name=request.form['txtNombre']
    _url=request.form['txtURL']
    _file=request.files['txtImagen']

    time=datetime.now()
    currentTime=time.strftime('%Y%H%M%S')

    if _file.filename!="":
        newName=currentTime+"_"+_file.filename
        _file.save("templates/site/img/"+newName)

    sql="INSERT INTO `books` (`id`, `name`, `image`, `url`) VALUES (NULL,%s,%s,%s);" # se ejecuta la instruccion sql
    data=(_name, newName, _url)
    conection=mysql.connect() # se abre la coneccion
    cursor=conection.cursor() #se genera un cursor
    cursor.execute(sql, data) #ese cursor ejecuta la instruccion sql
    conection.commit() #se lleva a cabo la instruccion con commit

    print(_name)
    print(_url)
    print(_file)
    return redirect('/admin/books')

@app.route('/admin/books/delete', methods=['POST'])
def admin_books_delete():

    if not 'login' in session:
        return redirect("/admin/login")
    
    _id=request.form['txtID']
    print(_id)

    conection=mysql.connect()
    cursor=conection.cursor() # este cursor es para poder ejecutar la instruccion sql
    cursor.execute("SELECT image FROM `books` WHERE id=%s", (_id))
    book=cursor.fetchall() #recuperamos todos los libros y los almacenamos en la variable books
    conection.commit()
    print(book)

    # si existe la imagen la borra
    if (os.path.exists("templates/site/img/"+str(book[0][0]))):
        os.unlink("templates/site/img/"+str(book[0][0]))

    conection=mysql.connect()
    cursor=conection.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (_id))
    conection.commit()

    return redirect('/admin/books')

## Esta es una forma de acceder a un archivo css
# @app.route("/css/<archivocss>")
# def css_link(archivocss):
#     return send_from_directory(os.path.join('templates/site/css'), archivocss)

if __name__ == '__main__':
    app.run(debug=True)


#Para correr la aplicacion: python app.py en consola