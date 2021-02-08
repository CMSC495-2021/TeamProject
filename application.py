from datetime import datetime
#boto 3
import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_encryption_sdk.encrypted import CryptoConfig
# crypto imports
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions, EncryptionContext
from flask import Flask, render_template, request

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


@app.route('/Authenticate', methods=["POST", "GET"])
def Authenticate():
    # aws access keys
    aws_access_key_id = "ASIARSOHCYSCDUTLSRYE"
    aws_secret_access_key = "XD/msFVUmEQPqHvVdUfXxJeQJT6E4ne6Rd+M+4h9"
    aws_session_token = "FwoGZXIvYXdzEI///////////wEaDNErMUf8vZhX6iJ7liLIAcReUHyar5V292FIS7OjgQNgc38MqHTxHMN/6G5G" \
                        "7JPOYOsOKiTlxaa3c1YV2KYXDTQJwkFBR7Ll78V2va5/J9NRd3aQiRN2gDUcfFP7KqyJNED5gsm1JYiGxwL2C/FMsi" \
                        "u/0hgaiUu5rKnYOo50bFAOV3D2hvpDIf/CCDCfmio2CplLuAJ/mrFjw+FsylcO3cxPXVUSC1q5tZD5YOvmmnH6apcHfb" \
                        "ps1o6GriLgwX9mYMBfgqRkvHUDEMfjVxL8iwdgN8+LoijUKMP/hIEGMi0XvM4PEnA13g8s83X/Yor8nDWkTGRY" \
                        "okb12nKv219nL4vps0Q+zKmrHRTKjhU="

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
                        return render_template('chatmain.html')
                    else:
                        return render_template('login.html')
                except:
                    return render_template('login.html')
            except:
                return render_template('login.html')

        except:
            return render_template('login.html')

    else:
        return render_template('login.html')


@app.route('/SubmitNewUser', methods=["POST", "GET"])
def SubmitNewUser():
    # aws access keys
    aws_access_key_id = "ASIARSOHCYSCDUTLSRYE"
    aws_secret_access_key = "XD/msFVUmEQPqHvVdUfXxJeQJT6E4ne6Rd+M+4h9"
    aws_session_token = "FwoGZXIvYXdzEI///////////wEaDNErMUf8vZhX6iJ7liLIAcReUHyar5V292FIS7OjgQNgc38MqHTxHMN/6G5G" \
                        "7JPOYOsOKiTlxaa3c1YV2KYXDTQJwkFBR7Ll78V2va5/J9NRd3aQiRN2gDUcfFP7KqyJNED5gsm1JYiGxwL2C/FMsi" \
                        "u/0hgaiUu5rKnYOo50bFAOV3D2hvpDIf/CCDCfmio2CplLuAJ/mrFjw+FsylcO3cxPXVUSC1q5tZD5YOvmmnH6apcHfb" \
                        "ps1o6GriLgwX9mYMBfgqRkvHUDEMfjVxL8iwdgN8+LoijUKMP/hIEGMi0XvM4PEnA13g8s83X/Yor8nDWkTGRY" \
                        "okb12nKv219nL4vps0Q+zKmrHRTKjhU="

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
                    return render_template('register.html')
            except:
                return render_template('register.html')
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

                    return render_template('login.html')
                else:
                    return render_template('register.html')
            except:
                return render_template('register.html')


if __name__ == '__main__':
    app.run()
    """
    Use the following two lines to locally run the application with livereload (view changes as you make them)
    You will also need to comment out the app.run()
    
    server = Server(app.wsgi_app)
    server.serve()
    """
