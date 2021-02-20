from datetime import datetime
# boto 3
import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_encryption_sdk.encrypted import CryptoConfig
# crypto imports
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext
from flask import Flask, render_template, request, redirect, url_for, flash

# socketIO/chat imports
from flask_socketio import SocketIO, send, emit

# flask-login
from flask_login import LoginManager

from models import User

# from livereload import Server commented this out so my IDE doesn't freak out. -DJ

application = app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'test_key'

# SocketIO Initialization
socketIO = SocketIO(app)

# flask login
login = LoginManager(app)
login.init_app(app)


# crypto items
class CryptoItems:
    aws_access_key_id = "ASIARSOHCYSCCAXFASUH"
    aws_secret_access_key = "KlqN8k+WLUl4c1UVrTNybL0kbsnyBgEX4nDauEeU"
    aws_session_token = "FwoGZXIvYXdzEOL//////////wEaDMOwDF4Rgj6z63GQPSLIAbXahFeqCqygvrwmKOann0cTXigG+HZX/K" \
                        "U5u67VZwhM8MMCRmpFKdcp2HuKPDNvqkRMg/65OWFXtgLzLIZ3P3oOhRHEtmPnTG0V+NM8EN5BbwVNL9pjPFu/j" \
                        "zGDIyynuZzz0IYUHlh7AO59+iqmNlpyMSOfLPeZsBQ7PvRNnHITddvBkyS8v7K5sJm0NmsDLxPWb7lFRn4K6e" \
                        "2uWyl9y1xw5J8a9iuKnejppYQripOsXEONU4gBz/3xDhxlenmt8Is+zXP+lT4EKKiel4EGMi1H/jeDdRt0XciK9" \
                        "NiHyhbWisFUgx1tvfUDg1loNNrE8PJQs88/Wb5mQWNvXCw="

    dbResource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token,
                                region_name='us-east-1').Table('Users')

    # crypto key and material provider
    aws_cmk_id = 'arn:aws:kms:us-east-1:108328567940:key/ac31eb77-1a66-452f-9744-8aec26b9aa74'
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id)

    # how the crypto is applied to attributes
    crypto_actions = AttributeActions(
        default_action=CryptoAction.DO_NOTHING,
        attribute_actions={
            'password': CryptoAction.ENCRYPT_AND_SIGN})

    crypto_context = EncryptionContext(table_name='Users')

    custom_crypto_config = CryptoConfig(materials_provider=aws_kms_cmp,
                                        attribute_actions=crypto_actions,
                                        encryption_context=crypto_context)

    encrypted_resource = EncryptedTable(table=dbResource, materials_provider=aws_kms_cmp,
                                        attribute_actions=crypto_actions)


@app.route('/index', methods=["GET"])
def index():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
@app.route('/', methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    return render_template('register.html')


@app.route('/Authenticate', methods=["POST", "GET"])
def Authenticate():
    if request.method == "POST":

        try:
            userName = str(request.form['username'])
            password = str(request.form['password'])

            response = CryptoItems.encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(userName),
                crypto_config=CryptoItems.custom_crypto_config
            )
            try:
                items = response['Items']
                pw = items[0]['password']
                try:
                    if password == pw:
                        flash('Success!', 'Success')
                        return redirect(url_for('chatmain'))
                    else:
                        flash('Bad UserName/Password', 'Failed')
                        return redirect(url_for('login'))
                except:
                    flash('Bad UserName/Password', 'Failed')
                    return redirect(url_for('login'))
            except:
                flash('Bad UserName/Password', 'Failed')
                return redirect(url_for('login'))

        except:
            flash('Bad UserName/Password', 'Failed')
            return redirect(url_for('login'))

    else:
        flash('Bad UserName/Password', 'Failed')
        return redirect(url_for('login'))


@app.route('/SubmitNewUser', methods=["POST", "GET"])
def SubmitNewUser():
    if request.method == 'POST':

        userName = str(request.form['userName'])
        userEmail = str(request.form['userEmail'])
        password = str(request.form['password'])
        passwordCheck = str(request.form['passwordCheck'])
        dateCreated = str(datetime.now().isoformat())

        count = CryptoItems.encrypted_resource.scan(crypto_config=CryptoItems.custom_crypto_config)
        userID = int(len(count['Items']) + 1)

        try:
            response = CryptoItems.encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(userName),
                crypto_config=CryptoItems.custom_crypto_config
            )

            items = response['Items']
            uniqueUser = items[0]['UserName']

            try:
                if uniqueUser == userName:
                    flash('Bad User Already Exists!', 'Failed')
                    return redirect(url_for('register'))
            except:
                flash('Bad User Already Exists!', 'Failed')
                return redirect(url_for('register'))
        except:
            try:
                if password == passwordCheck:
                    CryptoItems.encrypted_resource.put_item(
                        TableName='Users',
                        Item={'UserName': userName,
                              'UserID': userID,
                              'DateCreated': dateCreated,
                              'UserEmail': userEmail,
                              'password': password
                              },
                        crypto_config=CryptoItems.custom_crypto_config)

                    flash('Success! Please Login.', 'Success!')
                    return redirect(url_for('login'))
                else:
                    flash('Passwords Do Not Match!', 'Failed')
                    return redirect(url_for('register'))
            except:
                flash('Passwords Do Not Match!', 'Failed')
                return redirect(url_for('register'))


@app.route("/chatmain", methods=["GET", "POST"])
def chatmain():
    return render_template('chatmain.html')


# SocketIO Event Handler
@socketIO.on('message')
def message(data):
    send(data)
    emit('some-event', 'EVENT TEST')


if __name__ == '__main__':
    socketIO.run(app)
    """
    Use the following two lines to locally run the application with livereload (view changes as you make them)
    You will also need to comment out the app.run()
    
    server = Server(app.wsgi_app)
    server.serve()
    """