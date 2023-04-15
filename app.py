import os
from flask import Flask, json, render_template, request, jsonify, session
from flask_session import Session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "C:\session"

Session(app)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mudar123'
app.config['MYSQL_DATABASE_DB'] = 'tcc'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app) 

# Navegação da paginas #
@app.route('/')
def main():
     # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html", msg1 = "Recuperar minha senha.")
    else:     
       return render_template('home.html')
    
@app.route('/logout')
def logout():
    session["name"] = None
    return render_template("login.html", msg1 = "Recuperar minha senha.")

@app.route('/reset')
def reset():
    return render_template("reset.html")

@app.route('/emailsenha', methods=['POST','GET'])
def emailsenha():
    return render_template('login.html', msg1 ='Senha enviada para o e-mail de cadastro !!!')

@app.route('/cadastrar', methods=['POST','GET'])
def cadastrar():
      # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")    
    else:     
        return render_template('cadastro.html')
  
@app.route('/home', methods=['POST','GET'])
def home():
     # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")
    else:     
        return render_template('home.html')

@app.route('/menu', methods=['POST','GET'])
def menu():
           # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")
    else:     
        return render_template('menu.html')

@app.route('/usuario', methods=['POST','GET'])
def usuario():
        # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")
    else:  
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user')
        data = cursor.fetchmany(size=10)
        conn.commit()
        return render_template('usuario.html', lista = data)
  
@app.route('/cadusuario', methods=['POST','GET'])
def cadusuario():
        # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")
    else:  
        return render_template('usuario_novo.html')

# Autenticação na aplicação #
@app.route('/logar', methods=['POST','GET'])
def logar():
  user = request.form['user']
  _password = request.form['password']

  try:
     conn = mysql.connect()
     cursor = conn.cursor()
     cursor.execute('select user_password from tbl_user where user_username = (%s)', 
                (user))
     data = cursor.fetchone()
     conn.commit()
     _hash_password = data[0]

     if check_password_hash(_hash_password, _password):
      session["name"] = request.form['user']
      return render_template('home.html')
     else:
      return render_template('login.html', msg1 = 'Credenciais inválidas.', msg2 = 'Recuperar a senha?')  
  except Exception as e:
     return render_template('login.html', msg1 = 'Credenciais inválidas.', msg2 = 'Recuperar a senha?')  
  finally:
     cursor.close()
     conn.close()
   
# Inserção de usuários na base #
@app.route('/gravar', methods=['POST','GET'])
def gravar():
  nome = request.form['nome']
  username = request.form['user']
  _hashed_password = generate_password_hash(request.form['senha'], method='sha256')
  email = request.form['email']
  cpf = request.form['cpf']
  telefone = request.form['telefone']
 
  if nome and username and _hashed_password and email and cpf and telefone:
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('insert into tbl_user (user_name, user_username, user_password, user_email, user_cpf, user_telefone) VALUES (%s, %s, %s, %s, %s, %s)', 
                   (nome, username, _hashed_password, email, cpf, telefone))
    conn.commit()
    return render_template('usuario_novo.html', msg='Usuário inserido com sucesso')
  else:
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user')
    data = cursor.fetchmany(size=10)
    conn.commit()
    return render_template('usuario.html', lista = data)

# Inserção de usuários na base #
@app.route('/atualizar', methods=['POST','GET'])
def atualizar():
  id = request.form['id']
  nome = request.form['nome']
  username = request.form['user']
  senha = request.form['senha']
  senha = senha.split('$')
  email = request.form['email']
  cpf = request.form['cpf']
  telefone = request.form['telefone']
 
  if senha[0] == 'sha256':
    _hashed_password = request.form['senha']
  else:
    _hashed_password = generate_password_hash(request.form['senha'], method='sha256')
    

  if nome and username and _hashed_password and email and cpf and telefone:
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'update tbl_user set user_name = "%s", user_username = "%s", user_password = "%s", user_email = "%s"' % (nome, username, _hashed_password, email)
    query = query + ', user_cpf = "%s", user_telefone ="%s" where user_id = %s'% (cpf, telefone, id)
    cursor.execute(query)
    conn.commit()
    cursor.execute('select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user')
    data = cursor.fetchmany(size=10)
    conn.commit()
    return render_template('usuario.html', lista = data, msg = 'Usuário atualizado')
  else:
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user')
    data = cursor.fetchmany(size=10)
    conn.commit()
    return render_template('usuario.html', lista = data)


@app.route('/listar', methods=['POST','GET'])
def listar():
        # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")
    else:  
        nome = request.form['nome']
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user where user_name like '%%%s%%'" % (nome)
        query = query + "union all select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user where user_cpf like '%%%s%%'" % (nome)
        query = query + "union all select user_id, user_username, user_email, user_CPF, user_telefone from tbl_user where user_telefone like '%%%s%%'" % (nome)
        cursor.execute(query)
        data = cursor.fetchmany(size=10)
        conn.commit()
        return render_template('usuario.html', lista = data)

@app.route('/usuario/<int:id_consulta>', methods=['POST','GET'])
def exibe_por_id(id_consulta):
        # check if the users exist or not
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return render_template("login.html")
    else:  
        user_id = id_consulta
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('select * from tbl_user where user_id = (%s)', 
                        (user_id))
        data = cursor.fetchone()
        conn.commit()
        return render_template('usuario_edicao.html', datas=data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    app.run(host='0.0.0.0', port=port)

