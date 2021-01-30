from flask import Flask

html = '''
<html>
<head>
<title>Test Flask App </title>
</head>
<body> 
<h1>This is a test application!!</h1>
</body>
</html>
'''

application = app = Flask(__name__)
app.add_url_rule('/', 'index', (lambda: html))

if __name__ == '__main__':
    app.debug = True
    app.run()

