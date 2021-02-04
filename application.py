from flask import Flask, render_template

application = app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/index', methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
@app.route('/', methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template("register.html")



if __name__ == '__main__':
    app.run()

