from flask import Flask, render_template, session, request, redirect, flash
import subprocess
import secrets
import random
import redis
import uuid
import os
import re

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
flag = os.environ.get('FLAG','ASIS{test-flag}')
rds = redis.Redis(host='redis', port=6379)
uuidReg = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

@app.route('/')
def index():
	return render_template('main.html')

@app.route('/rate',methods=['POST'])
def rate():
	link = request.form.get('link')
	if not link or re.search(r'[\x00-\x20\[\]%{}\-]',link) or not link.isascii():
		return 'Invalid link', 400, {'Content-Type': 'text/plain'}
	try:
		p = subprocess.run(["/usr/bin/curl",link],capture_output=True,timeout=0.5)
		if(p.returncode == 0):
			resultID = str(uuid.uuid4())
			rds.set(resultID,str(random.randint(1,9)))
			return redirect(f'/result?id={resultID}')
	except Exception as e:
		print(e)
	return 'Something bad happened', 500, {'Content-Type': 'text/plain'}

@app.route('/result')
def result():
	rid = request.args.get('id')
	if(not rid):
		return 'Result ID is missing', 400, {'Content-Type': 'text/plain'}
	if(not uuidReg.match(rid)):
		return 'Invalid ID', 400, {'Content-Type': 'text/plain'}
	result = rds.get(rid)
	if(not result):
		return 'Result not found', 400, {'Content-Type': 'text/plain'}
	result = int(result)
	if(result == 10):
		return render_template('result.html', msg=flag)
	else:
		return render_template('result.html', msg=f'Your cat got {result}/10')

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080)
