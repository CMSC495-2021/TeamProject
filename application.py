from datetime import datetime
# boto 3
import boto3
from boto3.dynamodb.conditions import Key
# from dynamodb_encryption_sdk.encrypted import CryptoConfig
# # crypto imports
# from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
# from dynamodb_encryption_sdk.identifiers import CryptoAction
# from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
# from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext
from flask import Flask, render_template, request, redirect, url_for, flash

# socketIO/chat imports
from flask_socketio import SocketIO, send

# from livereload import Server commented this out so my IDE doesn't freak out. -DJ

application = app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'test_key'

# SocketIO Initialization
socketIO = SocketIO(app)


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
    # aws access keys
    aws_access_key_id = "ASIARSOHCYSCPAKIX45G"
    aws_secret_access_key = "rmCRDLvLQ4e2rTMPXsGslfyj7eez7t08BD8ACsk3"
    aws_session_token = "FwoGZXIvYXdzEN3//////////wEaDKjIorszqcZ13xm7YiLIAeK35pNEyKjBgNsxivnFjAOsWwok1rmeo" \
                        "9lzkqUUpC4519DsAtIbJZIYCQ1+l5hQ08rSw/q2GVAioylm+oCxsCld1FKUVgfvRaq2gYQ3c7vhvUpxC/fpO7jVNg" \
                        "fena/gi2Hw9DxGvSQaeDwEBoeDwQkBsMGbqo9zuBvxmW5ii2DIp/EryyCqfuFulvVoH3TbQu9/6i/IiMGFL4fw" \
                        "0v5mp0c0PgamS3F/j/3HsiE5z462oOm9Oc+IYqk16mJpP7kwc5Gmr13AF36lKIyZloEGMi22LtCMl9hX76b0b" \
                        "PrufhZICKbIWoK/Pv+tHwIOeK0/Y2swTxMIzWQca3bvUDg="

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

    if request.method == "POST":

        try:
            userName = str(request.form['username'])
            password = str(request.form['password'])

            response = encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(userName),
                crypto_config=custom_crypto_config
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
    # aws access keys
    aws_access_key_id = "ASIARSOHCYSCPAKIX45G"
    aws_secret_access_key = "rmCRDLvLQ4e2rTMPXsGslfyj7eez7t08BD8ACsk3"
    aws_session_token = "FwoGZXIvYXdzEN3//////////wEaDKjIorszqcZ13xm7YiLIAeK35pNEyKjBgNsxivnFjAOsWwok1rmeo" \
                        "9lzkqUUpC4519DsAtIbJZIYCQ1+l5hQ08rSw/q2GVAioylm+oCxsCld1FKUVgfvRaq2gYQ3c7vhvUpxC/fpO7jVNg" \
                        "fena/gi2Hw9DxGvSQaeDwEBoeDwQkBsMGbqo9zuBvxmW5ii2DIp/EryyCqfuFulvVoH3TbQu9/6i/IiMGFL4fw" \
                        "0v5mp0c0PgamS3F/j/3HsiE5z462oOm9Oc+IYqk16mJpP7kwc5Gmr13AF36lKIyZloEGMi22LtCMl9hX76b0b" \
                        "PrufhZICKbIWoK/Pv+tHwIOeK0/Y2swTxMIzWQca3bvUDg="

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

    if request.method == 'POST':

        userName = str(request.form['userName'])
        userEmail = str(request.form['userEmail'])
        password = str(request.form['password'])
        passwordCheck = str(request.form['passwordCheck'])
        dateCreated = str(datetime.now().isoformat())

        count = encrypted_resource.scan(crypto_config=custom_crypto_config)
        userID = int(len(count['Items']) + 1)

        try:
            response = encrypted_resource.query(
                KeyConditionExpression=Key('UserName').eq(userName),
                crypto_config=custom_crypto_config
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
                    encrypted_resource.put_item(
                        TableName='Users',
                        Item={'UserName': userName,
                              'UserID': userID,
                              'DateCreated': dateCreated,
                              'UserEmail': userEmail,
                              'password': password
                              },
                        crypto_config=custom_crypto_config)

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


if __name__ == '__main__':
    socketIO.run(app)
    """
    Use the following two lines to locally run the application with livereload (view changes as you make them)
    You will also need to comment out the app.run()
    
    server = Server(app.wsgi_app)
    server.serve()
    """
