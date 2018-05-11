from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route('/')
def index():
	return redirect('/welcome')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
	return render_template('welcome.html')

@app.route('/userinput', methods=['GET','POST'])
def userinput():
	return render_template('userinput.html')

@app.route('/projectinfo', methods=['GET','POST'])
def projectinfo():
	return render_template('projectinfo.html')

@app.route('/results', methods=['GET','POST'])
def results():
	return render_template('results.html')

if __name__ == "__main__":
    app.run(debug=True)
