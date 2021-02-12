from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Attr
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


@app.route('/SubmitNewUser', methods=["POST", "GET"])
def SubmitNewUser():
    # aws access keys
    aws_access_key_id = "ASIARSOHCYSCIOBBEJ7G"
    aws_secret_access_key = "5OcUb4STA0pBXNm+1raeM5CGIbWmt5xcH/DSOdK6"
    aws_session_token = "FwoGZXIvYXdzEGYaDH2HkQLWg9u1YyrjPSLIAbLYHadpcSMk7dCB7v7melCLm7lu3l94l8" \
                        "nDtT+Eq3YP8bqEBUOhfbGFASQI9KxJJlY13V6yI7nflAElGCVmM0pUv/Xk7cBYyqWJDCy3vq65T" \
                        "j66S4ngyaWC6PFavNxcUAYG1t0+h3pcvrrulnQX84vYWLG12D0j+HCpL4e2EG37X7rPkcjRW+t0BTE1" \
                        "ziA5viEd82ryNg1W1QOQJYGm+Nt7HDcLLxwtSj1TdsvU9xdWnP+U1+l0x7JNiJ7p5Qe8t3MbKPpta1" \
                        "nsKOmD/IAGMi1OYg6KYdDyJK0xxTwixWlxzyW2aS1IWy0noraVzeRiaQ6WtLK1uHNMwcgbtvc="

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

        userScan = dbResource.scan(FilterExpression=Attr("UserName").ne(userName))

        if not userScan:

            if password == passwordCheck:

                encrypted_resource.put_item(
                    TableName='Users',
                    Item={'UserID': userID,
                          'DateCreated': dateCreated,
                          'UserName': userName,
                          'UserEmail': userEmail,
                          'password': password
                          },
                    crypto_config=custom_crypto_config)

                return render_template('login.html')

            else:
                return render_template('register.html')
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
