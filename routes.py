from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app import mysql #, mail
#from flask_mail import Message
from flask_selfdoc import Autodoc


routes = Blueprint('routes', __name__)
auto = Autodoc()

def mysql_connection():
    cursor = mysql.connection.cursor()
    return cursor


@routes.route('/')
@auto.doc()
def home():
    """
    This is the landing page.
    Visitors of the website are prompted to notify if they are an establishment, 
    a hospital, regular visitors or agents.
    And then, afterwards the user is directed to the respective registeration/login page
    """
    
    return render_template('home.html')


@routes.route('/places')
@auto.doc()
def place():
    '''
    Lists all registered establishments.
    If visitors need to locate place to visit on the website, they can scan the qr-code to enter
    '''

    cur = mysql_connection()

    response = cur.execute('SELECT * FROM places')

    result = cur.fetchall()
    cur.close()
    
    if response > 0:
        return render_template('places.html', result=result)
    else:
        flash('There are no places registered yet', 'error')
        return redirect(url_for('routes.home'))



@routes.route('/dashboard')
@auto.doc()
def dashboard_a():
    '''
    Dashboard for Agents. Allows to search for visitor. See all visitors. Edit and all
    '''
    if 'user' in session:
        if 'admin' in session:
            cur = mysql_connection()
            cur.execute('SELECT * FROM visitors')
            visitors = cur.fetchall()

            cur.execute('SELECT * FROM places')
            places = cur.fetchall()

            #agents have to verify hospitals registeration by giving them a username and password to log in
            #therefore, hospitals that don't have usernames or passwords yet (both are given together anyway)
            #are displayed to agents for verification

            cur.execute('SELECT * FROM hospitals WHERE h_username IS NULL OR h_username = "" ')
            hospitals = cur.fetchall()

            return render_template('dashboard_a.html', places=places, visitors=visitors, hospitals=hospitals)
        else:
            return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))



@routes.route('/send', methods=['POST'])
def sendMail():
    if 'user' in session:
        if 'admin' in session:
            if request.method == "POST":
                user = request.form.get('username')
                pw = request.form.get('password')

                id = request.args.get('hid')
            
                cur = mysql_connection()

                #agent accepts hospital registration and provides username and password.
                #For hospitals to know about this new login details, I imagine an email
                #containing them would have to be sent, hence this section.
                #To see the functionality, uncomment this section and use a real email address
                '''
                cur.execute('SELECT h_name, h_email FROM hospitals WHERE hid = %s', [id])

                name, email = cur.fetchone()

                msgbody = f"""Hello,{name}, your registration on Corona Archive webapp has been accepted.
                Here are your login credentials for the website. 
                Username = {user}, Password = "{pw}".
                Regards, Corona Archive Team.
                """

                #enter valid email when testing this route
                #this email is not valid and is only used as a placeholder of sorts
                msg = Message("Login Info", sender="dummyMail@gmail.com",
                                recipients=[email], body=msgbody)
                mail.send(msg)
                '''

                #also update db
                cur.execute('UPDATE hospitals SET h_username = %s, h_password = %s WHERE hid = %s', (user, pw, id))
                mysql.connection.commit()
                cur.close()

                flash('Mail Sent!', 'success')
                return redirect(url_for('routes.dashboard_a'))
        else:
            return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))



@routes.route('/visits')
def visitor_place():
    if 'user' in session:
        if 'admin' in session:
            data1 = request.args.get('did')
            print(data1)
            
            data2 = request.args.get('pid')
            
            cur = mysql_connection()
            
            if data1:
                cur.execute('''
                    SELECT p.pid, p.p_name, p.p_address, vi.entry_date, vi.entry_time, vi.exit_date, vi.exit_time 
                    FROM visit AS vi JOIN places AS p ON p.pid = vi.place_id AND vi.device = %s
                    ''', (data1, ))
                
                thisVisitor = cur.fetchall()

                cur.execute('SELECT v_name FROM visitors WHERE device_id = %s', (data1, ))
                name = cur.fetchone()

                return render_template('foreach.html', visitor=thisVisitor, name=name)

            elif data2:
                cur.execute('''
                    SELECT v.vid, v.v_name, v.v_address, v.infected, vi.entry_date, vi.entry_time, vi.exit_date, vi.exit_time 
                    FROM visit AS vi JOIN visitors AS v ON vi.place_id = %s AND vi.device = v.device_id
                    ''', (data2, ))
                
                thisPlace = cur.fetchall()

                cur.execute('SELECT p_name FROM places WHERE pid = %s', (data2, ))
                name = cur.fetchone()

                return render_template('foreach.html', place=thisPlace, name=name)
        else:
            return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))



@routes.route('/page')
@auto.doc()
def dashboard_h():
    '''
    Dashboard for Hospitals. To see all registered visitors and mark them as infected or not
    '''
    if 'user' in session:
        if 'hospital' in session:
            cur = mysql_connection()

            cur.execute('SELECT * FROM visitors')
            visitors = cur.fetchall()

            return render_template('dashboard_h.html', visitors=visitors)
        else:
            return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))



@routes.route('/status/<int:id>')
def change_status(id):
    if 'user' in session:
        if 'hospital'in session:
            cur = mysql_connection()
            cur.execute('SELECT infected FROM visitors WHERE vid = %s', (id, ))

            res = cur.fetchone()

            if res['infected'] == 1:
                cur.execute('UPDATE visitors SET infected = %s WHERE vid = %s', (0, id))
                mysql.connection.commit()
            elif res['infected'] == 0:
                cur.execute('UPDATE visitors SET infected = %s WHERE vid = %s', (1, id))
                mysql.connection.commit()

            cur.close()
            return redirect(url_for('routes.dashboard_h'))
        else:
            return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))
        


@routes.route('/enter/<int:id>')
@auto.doc()
def enter(id):
    '''
    After Visitor scans QR-code and submits information, they enter the "You're in" Page.

    When they leave the place, the have to also logout from the website.
    '''
    if 'user' in session:
        if 'visitor' in session:
            cursor = mysql_connection()
            cursor.execute('SELECT place_id, device FROM visit WHERE visit_id=%s', [id])

            result = cursor.fetchone()

            cursor.execute('SELECT p_name FROM places WHERE pid=%s', (result['place_id'], ))
            place = cursor.fetchone()

            cursor.execute('SELECT v_name FROM visitors WHERE device_id=%s', (result['device'], ))
            visitor = cursor.fetchone()

            return render_template("enter.html", place=place['p_name'], visitor=visitor['v_name'])
        else:
            return redirect(url_for('routes.home'))
    else:
        return redirect(url_for('routes.home'))



@routes.route('/documentation')
@auto.doc()
def documentation():
    '''

    Web Application routes' documentation.
    '''
    return auto.html()
