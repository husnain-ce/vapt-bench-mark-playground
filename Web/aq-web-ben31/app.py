from flask import Flask, request, send_file
from multiprocessing import Pool, cpu_count
from subprocess import check_output, Popen, PIPE
import re
import tempfile
import os
import requests
import shutil

### Utils
def get_emails(args):
    repo_url, author = args
    repo_dir = tempfile.mkdtemp()
    try:
        p = Popen(['git', 'clone', '--mirror', '--', repo_url, repo_dir],
                stdout=PIPE, stderr=PIPE)
        p.wait()
        if p.returncode != 0:
            raise Exception(f'Failed to clone repo {repo_url}')

        # list commits from branches
        out = check_output(['git', 'branch', '--list'], cwd=repo_dir)
        branches = out.decode().strip().split('\n')
        branches = [branch.strip('* ') for branch in branches]
        res = set()
        for branch in branches:
            emails = check_output(
                ['git', 'log', '--pretty=format:%ae', 
                *([f'--author={author}'] if author else []),
                branch],
                cwd=repo_dir
            ).decode().split()
            res.update(emails)
    finally:
        shutil.rmtree(repo_dir)
    return res


### Flask app
app = Flask(__name__)
pool = Pool(processes=cpu_count())

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/find', methods=['POST'])
def check():
    if 'repo_url' in request.form:
        repo_urls = [url.strip() for url in request.form['repo_url'].splitlines() if url.strip()]
        repo_urls = repo_urls[:5]
    else:
        return 'Invalid request'

    
    for repo_url in repo_urls:
        if not re.match(r'^https?://', repo_url):
            return f'Invalid URL: {repo_url}'

    res = set()
    try:
        author = request.form.get('github_username')
        emails = pool.map(get_emails, ((url, author) for url in repo_urls))
        for e in emails:
            res.update(e)
    except Exception as e:
        return f'Error processing repositories: {str(e)}'
    res = list(res)
    return "<h1>Emails found:</h1><br>" + "<br>".join(res)


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
