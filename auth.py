#Routes that Handle Authentication
#Divided for the sake of organizing project

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app import mysql
from routes import auto, mysql_connection

import secrets
import string
from datetime import datetime


auth = Blueprint('auth', __name__)



#to generate unique device id for visitors
def generate_id(S, len):

    secure = 'start'

    while secure in S:
        secure = ''.join((secrets.choice(string.ascii_letters + string.digits) for i in range(len)))

    S.add(secure)
    return secure


@auth.route('/visitor/<int:pid>', methods=['GET', 'POST'])
@auto.doc()
def visitor_page(pid):
    '''

    This is the route a visitor goes after scanning a qrcode.
    Allows visitor to register and then enter into the place.
    
    Device_id is unique i.e. a user cannot have 2 different IDs and one device_id belongs to ONLY one user.
    '''
    if request.method == 'POST':
        name1 = request.form.get('first_name')
        name2 = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        addr = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zip')

        name = name1+ " "+name2
        address = addr + ", " + zipcode + " " + city + ", " + state
        
        cur = mysql_connection()

        #set of all registered device_id to ensure uniqueness when calling generate_id function
        devices = set()
        devices.add('start')

        cur.execute('SELECT device_id FROM visitors')
        ans = cur.fetchall()

        for row in ans:
            devices.add(row['device_id'])

        cur.execute('SELECT vid FROM visitors WHERE v_name = %s AND v_address = %s', (name, address))
        result = cur.fetchone()

        if not result:
            device = generate_id(devices, 64)
            if email and phone:
                cur.execute('INSERT INTO visitors(v_name, v_address, phone_number, v_email, device_id) VALUES(%s, %s, %s, %s, %s)',
                (name, address, phone, email, device))
                mysql.connection.commit()
            elif email:
                cur.execute('INSERT INTO visitors(v_name, v_address, v_email, device_id) VALUES(%s, %s, %s, %s)', (name, address, email, device))
                mysql.connection.commit()
            elif phone:
                cur.execute('INSERT INTO visitors(v_name, v_address, phone_number, device_id) VALUES(%s, %s, %s, %s)', (name, address, phone, device))
                mysql.connection.commit()
            else:
                cur.execute('INSERT INTO visitors(v_name, v_address, device_id) VALUES(%s, %s, %s)', (name, address, device))
                mysql.connection.commit()
            cur.close()    
        else:
            cur.execute('SELECT device_id FROM visitors WHERE vid = %s', (result['vid'], ))
            device = cur.fetchone()['device_id']

        #add to visit table as well
        start_date = datetime.now().date()
        start_time = datetime.now().time()

        cursor = mysql_connection()
        cursor.execute('INSERT INTO visit(place_id, device, entry_date, entry_time) VALUES(%s, %s, %s, %s)', (pid, device, start_date, start_time))
        id = cursor.lastrowid

        mysql.connection.commit()
        cursor.close()
        
        session['user'] = name
        session['visitor'] = id

        flash('Registration successful', 'success')

        return redirect(url_for('routes.enter', id=id))
    else:
        return redirect(url_for('auth.register', user=1, pid=pid))




#FOR AUTHENTICATION 

@auth.route('/register/<int:user>', methods=['GET', 'POST'])
@auto.doc()
def register(user): 
    '''

    Route to register vistors, hospitals and places.
    Agents don't have to register, just log in.
    (Also, after hospitals verification is done, they can log in as well)

    A different registration form is shown depending on which user it is.

    After establishment register, they are redirected to a page where they can download 
    their QR-Code.
    '''
    if request.method == "POST":
        #vistor = 1, hospital = 3, establishment = 4

        if user == 3:
            name = request.form.get('name')
            email = request.form.get('email')
            
            cur3 = mysql_connection()

            cur3.execute('INSERT INTO hospitals(h_name, h_email) VALUES(%s, %s)', (name, email))
            mysql.connection.commit()
            cur3.close()

            flash('Registration done! Once accepted, you will receive login details', 'success')
            return redirect(url_for('routes.home'))

        if user == 4:
            name2 = request.form.get('name')
            addr2 = request.form.get('address')
            city2 = request.form.get('city')
            state2 = request.form.get('state')
            zipcode2 = request.form.get('zip')

            ENV = 'prod'
            if ENV == 'dev':
                data = "http://127.0.0.1:5000/visitor/"
            else:
                data = "https://corona-archive.herokuapp.com/visitor/"

            address2 = addr2 + ", " + zipcode2 + " " + city2 + ", " + state2
            #data = (f

            cur = mysql_connection()

            cur.execute('INSERT INTO places(p_name, p_address, QRcode) VALUES(%s, %s, %s)', (name2, address2, data)) 
            id = cur.lastrowid

            data += str(id)

            cur.execute('UPDATE places SET QRcode=%s WHERE p_name = %s', (data, name2)) 
            mysql.connection.commit()
            cur.close()

            flash('Registration successful', 'success')
            return render_template('qrcode.html', data=data)

    else:
        return render_template('register.html', user=user)




#FOR AUTHENTICATION 
@auth.route('/login', methods=['POST', 'GET'])
@auto.doc()
def login():
    '''
    Login for Agents and Hospitals. Different redirection depending on which user 
    '''
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        cur = mysql_connection()
        cur.execute('SELECT * FROM agents WHERE a_username = %s AND a_password = %s', (username, password))

        agent = cur.fetchone()

        if agent is None:
            cur2 = mysql_connection()
            cur2.execute('SELECT * FROM hospitals WHERE h_username = %s AND h_password = %s', (username, password))

            hospital = cur2.fetchone()

            if hospital is None and agent is None:
                flash('User does not exist', 'error')
                return render_template("login.html")
            elif hospital:
                session['user'] = username
                session['hospital'] = True
                flash('Logged In successfully', 'success')
                return redirect(url_for('routes.dashboard_h')) #dashboard for hospitals...
        else:
            session['user'] = username
            session['admin'] = True
            flash('Logged In successfully', 'success')
            return redirect(url_for('routes.dashboard_a')) #dashboard for agents...            
    else:
        return render_template("login.html")





#Logout route
@auth.route('/logout')
@auto.doc()
def logout():
    if 'user' in session:
        if 'visitor' in session:
            end_date = datetime.now().date()
            end_time = datetime.now().time()

            cursor = mysql_connection()
            id = session['visitor']

            cursor.execute('UPDATE visit SET exit_date = %s, exit_time = %s WHERE visit_id = %s', (end_date, end_time, id))
            mysql.connection.commit()
            cursor.close()
            session.pop('visitor', None)

        if 'admin' in session:
            session.pop('admin', None)

        if 'hospital' in session:
            session.pop('hospital', None)
        
        session.pop('user', None)

        return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))