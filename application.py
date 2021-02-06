from dynamodb_encryption_sdk.encrypted import CryptoConfig
from flask import Flask, render_template, request
import boto3
from numpy import random
from datetime import date

# crypto imports
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext

# from livereload import Server commented this out so my IDE doesn't freak out. -DJ

application = app = Flask(__name__, static_folder='static', static_url_path='/static')


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


@app.route('/SubmitNewUser', methods=["POST", "GET"])
def SubmitNewUser():

    # aws access keys
    aws_access_key_id = "ASIARSOHCYSCHK6L2RFY"
    aws_secret_access_key = "pcg/B6f7+3ybMuOGLmCeCMu47/GXmJzS+pksUFvn"
    aws_session_token = "FwoGZXIvYXdzEFIaDOUnumPvLcdcOe0xQyLIAf97MMV66fbAuy3ffr8GLX+wyUkGN" \
                        "Z/VB6ZX5uR2qObxI0CkqzyVrSjVKq8hJNsnrxH5pYbfdsOoUOxBbFWEFJsjdvxE3KmIQId7jB" \
                        "VNTOE0XRHAw0/qO+TuWsROdVt0bIxEeXZuOLHBHnfnFdIVOYIXN2AncIh62J6zqb96dhth4mb3hwR7+7" \
                        "EcCTjwydXWmbSvF647f9vuwlQfTuw07npfV37REpERXmg6vDjhoxG4yh7WKQ32eZ62NgrEtFQmKiF2Q6RfWuy" \
                        "XKK/B94AGMi0qaBDet+nqoZC39xpa9yeJb9p/GSPu4gjBX4Tc62ZW2wDTkyCsxpwtcdppuKk="

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
        dateCreated = str(date)
        userID = int(random.randint(9999))

        if password == passwordCheck:
            encrypted_resource.put_item(
                TableName='Users',
                Item={'UserName': userName,
                      'UserID': userID,
                      'UserEmail': userEmail,
                      'DateCreated': dateCreated,
                      'password': password
                      }, crypto_config=custom_crypto_config)

            return render_template('login.html')

        else:
            return render_template('register.html')

    return 'ERROR! Did not create a user!'


if __name__ == '__main__':
    app.run()
    """
    Use the following two lines to locally run the application with livereload (view changes as you make them)
    You will also need to comment out the app.run()
    
    server = Server(app.wsgi_app)
    server.serve()
    """
