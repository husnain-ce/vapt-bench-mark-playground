#!/usr/bin/env python3
# Lab 02 - AWS-Lambda-Secret-Leak
# A minimal AWS Lambda control-plane API. The functions keep secrets in plaintext
# environment variables, and anyone able to call ListFunctions /
# GetFunctionConfiguration (a very common over-grant, e.g. lambda:GetFunction*)
# can read them straight out - no invoke needed.
# Exploit with curl, or the AWS CLI:
#   aws --endpoint-url http://localhost:9132 lambda get-function-configuration \
#       --function-name prod-report-generator
import json
from flask import Flask, Response

app = Flask("lambda")

FUNCTIONS = {
    "prod-report-generator": {
        "FunctionName": "prod-report-generator",
        "Runtime": "python3.12",
        "Role": "arn:aws:iam::123456789012:role/prod-report-role",
        "Handler": "main.handler",
        "Environment": {"Variables": {
            "DB_HOST": "prod-db.internal",
            "DB_PASSWORD": "Lambda-Prod-DB-Pw-EXAMPLE!",
            "STRIPE_SECRET_KEY": "STRIPE_API_KEY_PLACEHOLDER",
            "JWT_SIGNING_KEY": "prod-jwt-signing-key-rotate-me",
        }},
    },
    "image-thumbnailer": {
        "FunctionName": "image-thumbnailer", "Runtime": "nodejs20.x",
        "Role": "arn:aws:iam::123456789012:role/thumb-role",
        "Handler": "index.handler",
        "Environment": {"Variables": {"BUCKET": "acme-thumbnails"}},
    },
}

def j(obj, code=200):
    return Response(json.dumps(obj, indent=2), status=code, mimetype="application/json")

@app.route("/2015-03-31/functions/")
def list_functions():
    return j({"Functions": list(FUNCTIONS.values())})

@app.route("/2015-03-31/functions/<name>/configuration")
def get_config(name):
    f = FUNCTIONS.get(name)
    if not f:
        return j({"Type": "ResourceNotFoundException",
                  "message": f"Function not found: {name}"}, 404)
    return j(f)

@app.route("/2015-03-31/functions/<name>/invocations", methods=["POST"])
def invoke(name):
    if name not in FUNCTIONS:
        return j({"Type": "ResourceNotFoundException"}, 404)
    return j({"statusCode": 200, "body": "report generated"})

@app.route("/")
def home():
    return j({"app": "AWS Lambda (control plane, minimal)",
              "hint": "GET /2015-03-31/functions/  and  "
                      "/2015-03-31/functions/<name>/configuration"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9132, threaded=True)
