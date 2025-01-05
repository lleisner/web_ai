from flask import Flask, request
import traceback

app = Flask(__name__)

@app.route("/")
def start():
    return "<form action='reversed' method='get'><input name='rev'></input></form>"


@app.route("/reversed")
def reversed():
    return "<h1>"+request.args.get('rev')[::-1]+"</h1>"

@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"