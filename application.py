from flask import Flask, render_template, request
import boto3
from numpy import random
from livereload import Server
from datetime import date

aws_access_key_id = "ASIARSOHCYSCJG67Z3HC"
aws_secret_access_key = "AoQQN2y0lJoTMV+qTqUlifbCw9Yy7z1tslYzBrXW"
aws_session_token = "FwoGZXIvYXdzEDkaDOoYHA4OSqRoKQeyNCLIAZ+/xl0OesEZTg+ZXdaJdhQRMu2pbXf" \
                    "a7EjzK/X3ceCohnka3bBBhylClBkkWn29NwAjyeve6a3M+T4YInG5QLyjsAuS2cUOP96qJRAyw" \
                    "3u9asnWwNldpjF/4OdeDxOiC79GabhkiH02dhWXbGVY7QcvZBfOmy9e51oijYqe+vCGJYDfYl9xCmpJ" \
                    "4qfonbwE4OnBqheFFTupEgM+/fXuLdyA/CsZGMKNqfKtA5HSIRJrOsn/jz87M+IBFOnsk92R05pIdP" \
                    "FeBbk1KLKC8oAGMi2tgY+ZgUacKTxJqpyMSugBcRkXwZVOcPtf1E2VLrcsID0xyt9FDIo35kzBIvM="

dbResource = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token,
                            region_name='us-east-1')

dynamoDBClient = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token,
                              region_name='us-east-1')

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
    if request.method == 'POST':
        userName = str(request.form['userName'])
        userEmail = str(request.form['userEmail'])
        password = str(request.form['password'])
        passwordCheck = str(request.form['passwordCheck'])
        dateCreated = str(date)
        userID = str(random.randint(9999))

        TABLE_NAME = 'Users'

        if password == passwordCheck:
            dynamoDBClient.put_item(
                TableName=TABLE_NAME,
                Item={'UserName': {'S': userName},
                      'UserID': {'N': userID},
                      'UserEmail': {'S': userEmail},
                      'DateCreated': {'S': dateCreated},
                      'password': {'S': password}
                      })

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
    

