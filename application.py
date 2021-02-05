from flask import Flask, render_template
from livereload import Server

application = app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == '__main__':
    #app.run()
    server = Server(app.wsgi_app)
    server.serve()

