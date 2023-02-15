from flask import Flask, render_template, request, jsonify, request, session, flash, redirect, url_for
import mysql.connector
from functools import wraps

username = 'root'
password = 'aarush55'
host = 'localhost'
database = 'student_db'

cnx = mysql.connector.connect(
    user=username,
    password=password,
    host=host,
    database=database
)




def clean_id(id):
    id = str(id)
    id = id.replace('[', '')
    id = id.replace(']', '')
    id = id.replace('(', '')
    id = id.replace(')', '')
    id = id.replace(',', '')
    if id == '':
        id = 0
    id = int(id)
    return id

cursor = cnx.cursor()

#Get the login table and print the results
cursor.execute("SELECT * FROM login")
result = cursor.fetchall()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'aarush55'

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

"""
This code defines a function decorator is_logged_in, which can be used to wrap around other functions to check if a user is logged in before executing the wrapped function.

The decorator takes a function f as an argument and defines a new function wrap which will be used to wrap around f. 
wrap takes an arbitrary number of positional arguments *args and keyword arguments **kwargs and checks if the key 'logged_in' is present in a session object. 
If it is present, the decorator allows the wrapped function f to be executed with the provided arguments *args and **kwargs. 
If the key is not present, the decorator flashes a message to the user indicating that they are not authorized to access the wrapped function and redirects them to the 'index' page.
"""

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not authroized, please login', 'danger')
            return redirect(url_for('index'))
    return wrap


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clear')
def clear():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/register')
def login():
    return render_template('register.html')

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/endpoint', methods=['GET','POST','PUT','DELETE'])
def api():
    if(request.method == 'GET'):
        cursor.execute("SELECT * FROM student_info")
        result = cursor.fetchall()
        serialized = []
        for row in result:
            serialized.append({
                'id': row[0],
                'name': row[1],
                'class': row[2],
                'age': row[3],
                'contact': row[4],
                'email': row[5]
            })
        return jsonify(serialized)
    if(request.method == 'POST'):
        cursor.execute("SELECT id FROM student_info ORDER BY id DESC LIMIT 1")
        lastID = cursor.fetchall()
        lastID= clean_id(lastID)
        lastID = lastID + 1
        name = request.get_json()['name']
        grade = request.get_json()['grade']
        age = request.get_json()['age']
        contact = request.get_json()['contact']
        email = request.get_json()['email']

        cursor.execute("INSERT INTO student_info (id, name, class, age, contact, email) VALUES (%s, %s, %s, %s, %s, %s)", (lastID, name, grade, age, contact, email))
        cnx.commit()
        return jsonify({'status': 'success'})

    if(request.method == 'PUT'):
        id = request.get_json()['id']
        name = request.get_json()['name']
        grade = request.get_json()['grade']
        age = request.get_json()['age']
        contact = request.get_json()['contact']
        email = request.get_json()['email']

        cursor.execute("UPDATE student_info SET name = %s, class = %s, age = %s, contact = %s, email = %s WHERE id = %s", (name, grade, age, contact, email, id))
        cnx.commit()
        return jsonify({'status': 'success'})

    if(request.method == 'DELETE'):
        id = request.get_json()['id']
        cursor.execute("DELETE FROM student_info WHERE id = %s", (id,))
        cursor.execute("SELECT id FROM student_info WHERE id > %s", (id,))
        result = cursor.fetchall()
        for row in result:
            cursor.execute("UPDATE student_info SET id = %s WHERE id = %s", (row[0]-1, row[0]))
        cnx.commit()
        return jsonify({'status': 'success'})
    return 'Welcome to the StudentDB API'

@app.route('/api/example')
def api_example():
    return 'Hello World!'


@app.route('/student_data', methods=['GET'])
def student_data():
    #Get the student_info table
    cursor.execute("SELECT * FROM student_info")
    result = cursor.fetchall()
    serialized = []
    for row in result:
        serialized.append({
            'id': row[0],
            'name': row[1],
            'class': row[2],
            'age': row[3],
            'contact': row[4],
            'email': row[5]
        })

    return jsonify(serialized)

@app.route('/route', methods=['POST'])
def route():
    method = request.get_json()['method']
    
    #Check if the username and password are in the database
    
    #If the username and password are in the database
    if method == 'login':
        password = request.get_json()['password']
        username = request.get_json()['username']
        cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchall()
        if result:
            session['logged_in'] = True
            return {'login_success': True}

        return {'login_success': False}

    if method == 'register':
        password = request.get_json()['password']
        username = request.get_json()['username']
        #Get the last id from the login table and print the results
        cursor.execute("SELECT id FROM login ORDER BY id DESC LIMIT 1")
        lastID = cursor.fetchall()
        lastID= clean_id(lastID)
        lastID = lastID + 1
        #Check if the username is in the database
        cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
        result = cursor.fetchall()
        #If the username is in the database
        if result:
            return {'register_success': False}
        else:
            cursor.execute("INSERT INTO login (id, username, password) VALUES (%s, %s, %s)", (lastID, username, password))
            cnx.commit()
            return {'register_success': True}

    if method == 'add_data':
        cursor.execute("SELECT id FROM student_info ORDER BY id DESC LIMIT 1")
        lastID = cursor.fetchall()
        lastID= clean_id(lastID)
        lastID = lastID + 1
        name = request.get_json()['name']
        grade = request.get_json()['grade']
        age = request.get_json()['age']
        contact = request.get_json()['contact']
        email = request.get_json()['email']

        cursor.execute("INSERT INTO student_info (id, name, class, age, contact, email) VALUES (%s, %s, %s, %s, %s, %s)", (lastID, name, grade, age, contact, email))
        cnx.commit()

        return {'add_data': True}

    if method == 'delete_data':
        value = request.get_json()['id']
        cursor.execute("DELETE FROM student_info WHERE id = %s", (value,))
        #Make it so that all the id's above the deleted id are decremented by 1
        cursor.execute("SELECT id FROM student_info WHERE id > %s", (value,))
        result = cursor.fetchall()
        for row in result:
            cursor.execute("UPDATE student_info SET id = %s WHERE id = %s", (row[0]-1, row[0]))
        cnx.commit()
        return {'delete_data': True}

    if method == 'update':
        value = request.get_json()['id']
        name = request.get_json()['name']
        grade = request.get_json()['grade']
        age = int(request.get_json()['age'])
        contact = request.get_json()['contact']
        email = request.get_json()['email']
        print(request.get_json())
        cursor.execute("UPDATE student_info SET name = %s, class = %s, age = %s, contact = %s, email = %s WHERE id = %s", (name, grade, age, contact, email, value))
        cnx.commit()
        return {'update': True}

