from flask import Flask
from flask_mysqldb import MySQL
from flask_qrcode import QRcode
from flask_mail import Mail
#import uuid
import yaml

mysql = MySQL()
qrcode = QRcode()
mail = Mail()


def create_app():
    app = Flask(__name__)
    #key = uuid.uuid4().hex

    app.config['SECRET_KEY'] = '12we34rfdm*(@Jn()JMEW0endms__'
    
    ENV = 'prod' #change to prod

    if ENV == 'dev':
        cred = yaml.safe_load(open('db.yaml'))

        app.config['MYSQL_HOST'] = cred['mysql_host']
        app.config['MYSQL_USER'] = cred['mysql_user']
        app.config['MYSQL_PASSWORD'] = cred['mysql_password']
        app.config['MYSQL_DB'] = cred['mysql_db']
    else:
        app.config['MYSQL_HOST'] = 'ilzyz0heng1bygi8.chr7pe7iynqr.eu-west-1.rds.amazonaws.com'
        app.config['MYSQL_USER'] = 'b81kttppc93lrlno'
        app.config['MYSQL_PASSWORD'] = 'ipa12449elbmd2ar'
        app.config['MYSQL_DB'] = 'l3yfcmrnn48v57ar'

    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    #Initialize db    
    mysql.init_app(app)

    app.app_context().push()
    qrcode.init_app(app)

    
    #config parameters for mail client to be implemented by agents in web app
    #for mail client to work, actual email has to be used
    #if this functionality is to be seen, uncomment this section and use a real email address
    '''
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'dummyMail@gmail.com'  
    app.config['MAIL_PASSWORD'] = '*****'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.init_app(app)
    '''
    
    from routes import auto
    auto.init_app(app)
    

    '''
    An agent account created for testing purposes
    '''
    agent_name = "testadmin"
    agent_password = "testadmin123%"
    
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM agents WHERE a_username = %s AND a_password = %s', (agent_name, agent_password))
    agent = cursor.fetchone()

    if agent is None:
        cursor.execute('INSERT INTO agents(a_username, a_password) VALUES(%s, %s)', (agent_name, agent_password))
        mysql.connection.commit()
    cursor.close()

    from routes import routes
    app.register_blueprint(routes, url_prefix='/')

    from auth import auth
    app.register_blueprint(auth, url_prefix='/')

    return app