Target 7. DVWS-node — REST + SOAP + GraphQL (Damn Vulnerable Web Services)  ✅ (verified working via native run + cached mongo/mysql on this box)

DVWS-node is an insecure Node.js web service (Express + MongoDB + MySQL) with a deliberately broad attack surface across REST, SOAP/XML, XML-RPC and GraphQL — one of the widest API-vuln catalogues of the set.

1: Get the repo:   unzip DVWS-node.zip && cd DVWS-node   # (fresh box: git clone https://github.com/snoopysecurity/dvws-node)
2a: Deploy (Docker — normal method):  docker compose up -d --build     # web:80 + MongoDB + MySQL, auto-seeds
2b: Deploy (native — what was verified here, uses local Node + two DB containers):
    npm install
    docker run -d --name dvws-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=mysecretpassword -e MYSQL_DATABASE=dvws_sqldb mysql:8 --default-authentication-plugin=mysql_native_password
    docker run -d --name dvws-mongo -p 27017:27017 mongo:4.4
    export SQL_LOCAL_CONN_URL=127.0.0.1 SQL_USERNAME=root SQL_PASSWORD=mysecretpassword SQL_DB_NAME=dvws_sqldb \
           MONGO_LOCAL_CONN_URL=mongodb://127.0.0.1:27017/node-dvws JWT_SECRET=access EXPRESS_JS_PORT=8085
    node scripts/seed-database.js && node src/server.js
Open in browser:   http://localhost:8085/api-docs   <-- Swagger  |  /api (REST)  |  /graphql  |  /dvwsuserservice (SOAP)  |  /xmlrpc
# Quick win: GraphQL introspection is ENABLED — dump the schema:
#   curl -s -X POST localhost:8085/graphql -H 'Content-Type: application/json' -d '{"query":"{__schema{types{name}}}"}'   (leaks User, Passphrase, Notebook, File ...)
3: Stop:  Ctrl-C ; docker rm -f dvws-mysql dvws-mongo   (Docker path: docker compose down)

Seed users: MongoDB admin/letmein, test/test ; MySQL passphrases: admin = md5("password")

Requirements:
    Docker + docker compose  (Docker path)  OR  Node.js + npm + cached mongo:4.4/mysql:8 containers (native path)
    Burp / Postman / curl    (REST, SOAP, XML-RPC and GraphQL requests)

List of Vulnerabilities (verified: GraphQL introspection):

    GraphQL: introspection enabled [VERIFIED], access-control issues, arbitrary file write, batching brute force
    Mass Assignment  |  NoSQL Injection  |  SQL Injection
    JSON Web Token (JWT) secret-key brute force (JWT_SECRET = "access")
    Hidden API functionality exposure  |  API endpoint brute forcing
    XXE  |  XML Injection  |  XML Bomb (DoS)  |  SOAP Injection  |  XPATH Injection
    Command Injection  |  CRLF Injection  |  Path Traversal
    XML-RPC user enumeration  |  Sensitive Data Exposure  |  CSRF
