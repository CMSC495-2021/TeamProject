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

application = app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'test_key'

# SocketIO Initialization
socketIO = SocketIO(app)

# logging setup
LOG = create_logger(application)


# crypto items
class CryptoItems:
    with open('aws') as v:
        aws_access_key_id = str(v.readline().strip())
        aws_secret_access_key = str(v.readline().strip())

    dbResource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name='us-east-1').Table('Users')

    # crypto key and material provider
    aws_cmk_id = 'arn:aws:kms:us-east-1:910140038075:key/353f6f4c-0d0b-47b1-99fc-3aeec929b973'
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
    return render_template("login.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    return render_template('register.html')


# # TODO Comment out first, then remove after testing
# @app.route('/editProfile', methods=["GET", "POST"])
# def profile():
#     # on POST update user info in DB, on error flash error and make no change
#     if request.method == "POST":
#         req = request.form
#         userName = str(req['userName'])
#         userEmail = str(req['userEmail'])
#         password = str(req['password'])
#         userInitials = str(req['userInitials'])
#         passwordCheck = str(req['passwordCheck'])

#         return render_template("profile.html",
#                                userName=userName,
#                                userEmail=userEmail,
#                                userInitials=userInitials,
#                                password=password,
#                                passwordCheck=passwordCheck)


@app.route('/Authenticate', methods=["POST", "GET"])
def Authenticate():
    if request.method == "POST":
        try:
            # req = request.form
            username = str(request.form['username'])
            password = str(request.form['password'])

            # Original db call for user KEEP and un-indent!
            response = CryptoItems.encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(username),
                crypto_config=CryptoItems.custom_crypto_config
            )

            try:
                items = response['Items']
                pw = items[0]['password']
                try:
                    if password == pw:
                        # Load user into session for use...
                        session['USERNAME'] = items[0]['UserName']
                        session['INITIALS'] = items[0]['UserInitials']
                        print("LOADED USER IN SESSION")
                        return redirect(url_for('chatmain'))
                    else:
                        flash('Bad UserName/Password', 'Failed')
                        return redirect(url_for('login'))
                except Exception as e:
                    print("EXCEPTION: " + str(e))
                    flash('Bad UserName/Password', 'Failed')
                    return redirect(url_for('login'))
            except Exception as e:
                print("EXCEPTION: " + str(e))
                flash('Bad UserName/Password', 'Failed')
                return redirect(url_for('login'))
            # End original call
        except Exception as e:
            print("EXCEPTION: " + str(e))
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

        try:
            response = CryptoItems.encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(userName),
                crypto_config=CryptoItems.custom_crypto_config
            )

            items = response['Items']
            uniqueUser = items[0]['UserName']

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


# Added basic session info for use in template
# May need to build out based on feedback
@app.route("/chatmain", methods=["GET", "POST"])
def chatmain():
    username = session['USERNAME']
    initials = session['INITIALS']
    return render_template('chatmain.html',
                           username=username,
                           initials=initials, )


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
    socketIO.run(app, host="0.0.0.0", port=80)
