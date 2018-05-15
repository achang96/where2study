from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from database import data
import json
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(16)


# Set database
db = data()


# Convert a list to a comma separated string
def li_to_str(li):
	st = ""
	if li != []:
		st = ', '.join(li)
	return st


# Process user's answers to form
def processform(f):
	selections = {}

	for key in f.keys():
		for value in f.getlist(key):
			if key == "gpa":
				if "<" in value:
					grade = re.search("< (\d.\d\d)", value)
					selections[key] = [0, float(grade.group(1))]
				else:
					grade = re.search("(\d.\d\d)-(\d.\d\d)", value)
					selections[key] = [float(grade.group(1)), float(grade.group(2))]
			elif key == "cost":
				if "<" in value:
					cost = re.search("< (\d{2},\d{3})", value)
					selections[key] = [0, int(cost.group(1).replace(',',''))]
				elif ">" in value:
					cost = re.search("> (\d{2},\d{3})", value)
					selections[key] = [int(cost.group(1).replace(',','')), 100000]
				else:
					cost = re.search("(\d{2},\d{3})-(\d{2},\d{3})", value)
					selections[key] = [int(cost.group(1).replace(',','')),
									   int(cost.group(2).replace(',',''))]
			elif key in selections:
				temp = selections[key]
				if isinstance(temp, str):
					selections[key] = [temp, value]
				else:
					selections[key].append(value)
			else:
				selections[key] = value

	return selections


# Stringify program description from database entry
def program_description(di):
	t1 = "\t Academic Year Requirement: " + li_to_str(di["year"]) + "\n"
	t2 = "\t GPA Requirement: " + str(di["gpa"]) + "\n"
	t3 = "\t Purpose: " + li_to_str(di["purpose"]) + "\n"
	t4 = "\t Second Language Requirement: " + li_to_str(di["seclang"]) + "\n"
	t5 = "\t Cost: " + str(di["cost"]) + "\n"
	t6 = "\t Housing Options: " + li_to_str(di["housing"]) + "\n"
	t7 = "\t Extra Curricular Activities Available: " + li_to_str(di["extra"]) + "\n"
	t8 = "\t Program Seasons and Durations: " + li_to_str(di["length"]) + "\n"
	t9 = "\t Credit Type: " + li_to_str(di["credit"]) + "\n"
	text = t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9
	return text


# Rank programs based on user inputs
def rank(selections):
	rankings = []

	for (prog, desc) in db.items():
		if selections["year"] in desc["year"]:
			desc["index"] += 1
		if selections["school"] in desc["school"] or desc["school"] == []:
			desc["index"] += 1
		if selections["gpa"][0] <= desc["gpa"] <= selections["gpa"][1]:
			desc["index"] += 1
		if selections["seclang"] in desc["seclang"]:
			desc["index"] += 1
		if isinstance(selections["purpose"], str) and selections["purpose"] in desc["purpose"]:
			desc["index"] += 1
		if isinstance(selections["purpose"], list):
			for ele in selections["purpose"]:
				if ele in desc["purpose"]:
					desc["index"] += 1
		if isinstance(selections["credit"], str) and selections["credit"] in desc["credit"]:
			desc["index"] += 1
		if isinstance(selections["credit"], list):
			for ele in selections["credit"]:
				if ele in desc["credit"]:
					desc["index"] += 1
		if selections["region"] in desc["region"]:
			desc["index"] += 1
		if selections["cost"][0] <= desc["cost"] <= selections["cost"][1]:
			desc["index"] += 1
		if selections["housing"] in desc["housing"]:
			desc["index"] += 1
		if isinstance(selections["activity"], str) and selections["activity"] in desc["extra"]:
			desc["index"] += 1
		if isinstance(selections["activity"], list):
			for ele in selections["activity"]:
				if ele in desc["extra"]:
					desc["index"] += 1
		if selections["length"] in desc["length"]:
			desc["index"] += 1

		rankings.append((desc["index"], prog))
		rankings.sort(reverse=True)

	return rankings


@app.route('/')
def index():
	return redirect('/welcome')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
	return render_template('welcome.html')

@app.route('/userinput', methods=['GET','POST'])
def userinput(message=None):
	if request.method == "GET":
		return render_template('userinput.html', message = message)
	elif request.method == "POST":
		try:
			selections = processform(request.form)
			rankings = rank(selections)

			sug1 = (str(rankings[0][1]), program_description(db[rankings[0][1]]), db[rankings[0][1]]["link"])
			sug2 = (str(rankings[1][1]), program_description(db[rankings[1][1]]), db[rankings[1][1]]["link"])
			sug3 = (str(rankings[2][1]), program_description(db[rankings[2][1]]), db[rankings[2][1]]["link"])

			return render_template('results.html', first = sug1, second = sug2, third = sug3)
		except(KeyError):
			# print("test")
			return render_template('userinput.html', message = "Please make selections in all fields before submitting.")

@app.route('/results', methods=['GET','POST'])
def results(first, second, third):
	return render_template('results.html', first = sug1, second = sug2, third = sug3)


# Run Flask app with debugging feature
if __name__ == "__main__":
    app.run(debug=True)
