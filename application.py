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
from flask import Flask, render_template, request, redirect, url_for, flash, session, copy_current_request_context

# logging
from flask.logging import create_logger

# socketIO/chat imports
from flask_socketio import SocketIO, emit, disconnect

# flask-login
# from flask_login import LoginManager

# from models import User

# from livereload import Server commented this out so my IDE doesn't freak out. -DJ

application = app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'test_key'

# SocketIO Initialization
socketIO = SocketIO(app)

# flask login
#login = LoginManager(app)
#login.init_app(app)

# logging setup
LOG = create_logger(application)

# crypto items
#Try-except set up to bypass crypto issues when key is expired
class CryptoItems:
    aws_access_key_id = "ASIARSOHCYSCJJ7F5XTQ"
    aws_secret_access_key = "Q0MbFA3TS8MjSjSz6Loa9/crOJwC+Q55kxoaHld/"
    aws_session_token = "FwoGZXIvYXdzEAgaDHS9Y1Z3r2Nc3Bo9PiLIATx2D5SCjtAvmrZclqdJ+EhrBoQTPCfQREw" \
                        "c/21cWyND5We6HpQDh6iQZqwx9rsQUBdFpf+UsllJZVPEwfhEK6/kGG3lBgnJSz+1U66RnzBN1TY4E1Hl48x4OOk" \
                        "dHgvFuwL29jtBMmea5pbFlzu+Spt8UrBQ3jtxHjmEHxTdfXVGVqeUwQ4HmSWM/Ko9CqSLTcc2WslVpjfyNBLnv5CT" \
                        "OckGCAhmPkPcPOlQX9xdpZu2BOJzU+QZfilgVG/dBHakyoVZRKgtkArPKMP5j4IGMi1Rqq5sJ/ESXRwkqPrBm3wyw" \
                        "qiCoV+YckEfqIC3UaRcZ1fMBsBwQUAsbdMjtk="

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
    

@app.route('/login', methods=["GET", "POST"])
@app.route('/index', methods=["GET"])
@app.route('/', methods=["GET", "POST"])
def login():
    #FIXME Remove if else
    # if not CryptoItems.users:
        #KEEP THIS LINE AND UN-INDENT
        return render_template("login.html")
    # else:
    #     flash('Temporary DB in use', 'Failed')
    #     return render_template("login.html")
    #End Remove if-else
@app.route('/register', methods=["POST", "GET"])
def register():
    return render_template('register.html')

#TODO Restrict to auth'd user in session
@app.route('/editProfile', methods=["GET","POST"])
def profile():
    
    #on POST update user info in DB, on error flash error and make no change  
    if request.method == "POST":
        req = request.form
        userName = str(req['userName'])
        userEmail = str(req['userEmail'])
        password = str(req['password'])
        userInitials = str(req['userInitials'])
        passwordCheck = str(req['passwordCheck'])
        dateUpdated = str(datetime.now().isoformat())
        
        # try:
        #     #FIXME This was C/P from submit user and is likely the wrong call
        #     #but I instered it anyway to clear 'no try' error
        #     CryptoItems.encrypted_resource.put_item(
        #         TableName='Users',
        #         Item={'UserName': userName,
        #                 'UserID': userID,
        #                 'UserInitials': userInitials,
        #                 'DateCreated': dateCreated,
        #                 'UserEmail': userEmail,
        #                 'password': password
        #                 },
        #         crypto_config=CryptoItems.custom_crypto_config)
        # except:
        #     flash('unable to save user info', 'Failed')
        #     return redirect(url_for('profile'))
        
        #TODO Re-load session with new user object
        return render_template("profile.html",
                                userName = userName,
                                userEmail = userEmail,
                                userInitials = userInitials,
                                password = password,
                                passwordCheck = passwordCheck)
        
@app.route('/Authenticate', methods=["POST", "GET"])
def Authenticate():
    if request.method == "POST":
        try:
            # req = request.form
            username = str(request.form['username'])
            password = str(request.form['password'])
            print("USER ENTERED: "+username+","+password)
            #Original db call for user KEEP and un-indent!
            response = CryptoItems.encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(username),
                crypto_config=CryptoItems.custom_crypto_config
            )
            print(response)
            try:
                items = response['Items']
                pw = items[0]['password']
                try:
                    if password == pw:
                        #Load user into session for use...
                        session['USERNAME'] = items[0]['UserName']
                        session['INITIALS'] = items[0]['UserInitials']
                        print("LOADED USER IN SESSION")
                        flash('User created!', 'Success')
                        return redirect(url_for('chatmain'))
                    else:
                        flash('Bad UserName/Password', 'Failed')
                        return redirect(url_for('login'))
                except Exception as e:
                    print("EXCEPTION: "+str(e))
                    flash('Bad UserName/Password', 'Failed')
                    return redirect(url_for('login'))
            except Exception as e:
                print("EXCEPTION: "+str(e))
                flash('Bad UserName/Password', 'Failed')
                return redirect(url_for('login'))
            #End original call
        except Exception as e:
            print("EXCEPTION: "+str(e))
            flash('Bad UserName/Password', 'Failed')
            return redirect(url_for('login'))
    else:
        flash('Bad UserName/Password', 'Failed')
        return redirect(url_for('login'))


@app.route('/SubmitNewUser', methods=["POST", "GET"])
def SubmitNewUser():
    if request.method == 'POST':
        req = request.form
        userName = str(req['userName'])
        userEmail = str(req['userEmail'])
        userInitials = str(req['userInitials'])
        password = str(req['password'])
        passwordCheck = str(req['passwordCheck'])
        dateCreated = str(datetime.now().isoformat())
        
        try:
            count = CryptoItems.encrypted_resource.scan(crypto_config=CryptoItems.custom_crypto_config)
            userID = int(len(count['Items']) + 1)
        except Exception as e:
            print("TEST Error: " + str(e))


        #Why is this check set up as a try-except?
        #How does the password check fire if the username
        #check succeeds and skips the except?
        #Haven't actually tested since keys required for DB
        try:
            response = CryptoItems.encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(userName),
                crypto_config=CryptoItems.custom_crypto_config
            )

            items = response['Items']
            uniqueUser = items[0]['UserName']

            #Same question here about wrapping the if in a try-except...
            try:
                if uniqueUser == userName:
                    flash('User Already Exists!', 'Failed')
                    return redirect(url_for('register'))
            except:
                flash('Error checking username!', 'Failed')
                return redirect(url_for('register'))
        except:
            try:
                if password == passwordCheck:
                    CryptoItems.encrypted_resource.put_item(
                        TableName='Users',
                        Item={'UserName': userName,
                              'UserID': userID,
                              'UserInitials': userInitials,
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

#Added basic session info for use in template
#May need to build out based on feedback
#TODO Restrict to auth'd user
@app.route("/chatmain", methods=["GET", "POST"])
def chatmain():
    username = session['USERNAME']
    initials = session['INITIALS']
    return render_template('chatmain.html', 
                            username = username, 
                            initials = initials,)

# SocketIO Event Handler template
# @socketIO.on('message')
# def message(data):
#     send(data)
#     emit('some-event', 'EVENT TEST')

# Broadcast message to all conencted sockets
@socketIO.on('broadcast_event', namespace='/chatmain')
def broadcast_message(message):
    emit('response',
    {
        'data': message['data'],
        'username': session['USERNAME'],
        'initials': session['INITIALS']
    },
        broadcast=True)

#TODO Use for logoff?
#FIXME This isn't working yet for some reason it immediately reconnects
#probably need to investigate the disconnect method or tie the req
#to the app's user session kill...
#Maybe look into flask_login as well
@socketIO.on('disconnect_event', namespace='/chatmain')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    emit('response',
    {
        'data': 'Disconnected!',
        'username': session['USERNAME'],
        'initials': session['INITIALS']
    },
    broadcast=True,
    callback=can_disconnect)


if __name__ == '__main__':
    socketIO.run(app)
    """
    Use the following two lines to locally run the application with livereload (view changes as you make them)
    You will also need to comment out the app.run()
    
    server = Server(app.wsgi_app)
    server.serve()
    """
