## Description

This repository contains an example Python API that is vulnerable to several different web API attacks.

## Installation

We will be using docker images and containers to install all the api. 

### MacOSX

* Download the latest version of [docker toolbox](https://www.docker.com/products/docker-toolbox)
* Go through installation steps
* Start up Kitematic ![kitematic](kitematic.png).
* In the search box type `mkam/vulnerable-api-demo` and click create ![create](create.png).
* On right side you will see an IP:PORT access url ![ip](ip.png).
* Copy it and paste into browser to navigate to the api ![browser](browser.png).
* Jump to [Install Burp Proxy](#install-burp-proxy)

### Windows

***YOU WILL NEED ADMIN RIGHTS TO INSTALL***

* Download the latest version of [docker toolbox](https://www.docker.com/products/docker-toolbox)
* Go through installation steps
* Start up Kitematic ![kitematic](kitematic_win.png).
* In the search box type `mkam/vulnerable-api-demo` and click create ![create](create.png).
* On right side you will see an IP:PORT access url ![ip](ip.png).
* Copy it and paste into browser to navigate to the api ![browser](browser.png).
* Jump to [Install Burp Proxy](#install-burp-proxy)

### Linux

* Install docker engine and docker client [on docker website](https://docs.docker.com/engine/installation/linux/ubuntulinux/)
* Run `docker run -tid -p 8081:8081 --name api mkam/vulnerable-api-demo`
* You can now test your api `curl localhost:8081 -v`

#### Install Burp Proxy

* Install java [from oracle website](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) if you don't have it already
* Download jar file from [burp website](https://portswigger.net/burp/downloadfree.html)
* Run java -jar burpsuite_free_v1.6.32.jar


## API Details

The example API can be accessed on the system at port 8081.

### What is vAPI

vAPI is an API written specifically to illustrate common API vulnerabilities.

vAPI is implemented using the Bottle Python Framework and consists of a user database and a token database.

### How is vAPI Used

#### vAPI Process flow

1. Request token from /tokens
  * Returns an auth token
  * Returns expiration date of auth token
  * Returns a user id
2. Request user record from /user/<user_id>
  * Requires the auth token
  * Returns the user record for the user specfied, provided the auth token is not expired and is valid for the user id specified
  * Each user can only access their own record

#### Test Users 

Included with install

| Username | Password |
|----------|----------|
|user{1-9} |pass{1-9} |
|admin1    |pass1     |

#### API Reference

##### URL

SYSTEM_IP:8081

##### POST /tokens
Request an Auth Token for a user

###### Request Headers
1. Accept: application/json
2. Content-Type: application/json or application/xml

###### Request JSON Object
1. username (string) - Name of user requesting token
2. password (string) – Password of user requesting a token

###### Response JSON Object
1. token
  * expires (string) – The Auth Token expiration date/time
  * token - id (string) – Auth Token
  * user - id (string) – Unique user ID
  * name (string) – Username

###### Status Code
1. 200 OK - Request completed successfullyi

###### Request

```
POST /tokens HTTP/1.1
Accept: application/json
Content-Length: 36
Content-Type: application/json
Host: 192.168.13.37:8081

{"auth":
    {"passwordCredentials":
        {"username": "USER_NAME",
          "password":"PASSWORD"}
    }
}

 
```

or

```
POST /tokens HTTP/1.1
Accept: */*
Content-Length: 170
Content-Type: application/xml
Host: 192.168.13.37:8081

<?xml version="1.0" encoding="UTF-8"?>
<auth>
    <passwordCredentials>
        <username>user1</username>
        <password>pass1</password>
    </passwordCredentials>
</auth>

 
```
###### Response
```
HTTP/1.0 200 OK
Date: Tue, 07 Jul 2015 15:34:01 GMT
Server: WSGIServer/0.1 Python/2.7.6
Content-Type: text/html; charset=UTF-8
 
{
    "access":
        {
            "token":
                {
                    "expires": "Tue Jul  7 15:39:01 2015",
                    "id": "AUTH_TOKEN"
                },
            "user":
                {
                    "id": 10,
                    "name": "USER_NAME"
                }
        }
}
```

##### GET /user/USER_ID
Retrieve the user's entry in the user database

###### Request Headers
1. Accept: application/json
2. Content-Type: application/json
3. X-Auth-Token: <TOKEN_ID> (from /tokens POST)

###### Request JSON Object
1. None

###### Response JSON Object
1. User 
  * id (string) – Unique user ID
  * name (string) – Username
  * password (string) – Password

###### Status Codes
1. 200 OK - Request completed successfully

###### Request
```
GET /user/1 HTTP/1.1
Host: 192.168.13.37:8081
X-Auth-Token: AUTH_TOKEN
Content-type: application/json
Accept: text/plain
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 0


```

###### Response
```
HTTP/1.0 200 OK
Date: Mon, 06 Jul 2015 22:08:56 GMT
Server: WSGIServer/0.1 Python/2.7.9
Content-Length: 73
Content-Type: application/json
 
{
    "response":
        {
            "user":
                {
                    "password": "PASSWORD",
                    "id": USER_ID,
                    "name": "USER_NAME"
                }
        }
}
```
##### POST /user
Creates an user with the given username and password.
2 Conditions:
  1. User cannot already exist
  2. Username has to meet strict naming guidlines. The username must be matched by this regular expression: ```([a-z]+)*[0-9]```. This means that a username has to start with a lowercase letter and end with numbers. So, usernames that look like "user1" or "abc123" will be accepted, but usernames that look like "USER1" or "1user" will not be accepted.

###### Request Headers
1. X-Auth-Token - Valid token for the admin user

###### Request JSON Object
1. User 
  * name (string) – Username that matches above conditions
  * password (string) – Password

###### Response JSON Object
1. response
  * user
    - username - the name of the succesfully created user
    - password - the password of the successfully created user

###### Status Code
1. 200 OK - Request completed successfullyi

###### Request

```
POST /user HTTP/1.1
User-Agent: curl/7.35.0
Host: 127.0.0.1:8081
Accept: */*
x-auth-token: ADMIN TOKEN
Content-type: application/json
Content-Length: 54

{"user":
	{"username": "USERNAME",
	"password": "PASSWORD"}
}


```

###### Response
```
HTTP/1.0 200 OK
Date: Mon, 06 Jul 2015 22:08:56 GMT
Server: WSGIServer/0.1 Python/2.7.9
Content-Length: 68
Content-Type: application/json
 
{
    "response":
        {
            "user":
                {
                    "password": "PASSWORD",
                    "name": "USER_NAME"
                }
        }
}


```

##### GET /uptime
##### GET /uptime/FLAG
Returns the server uptime, and now supports pretty formatting just by passing in command line flags. 
Super useful for system administrators!


###### Request JSON Object
1. None

###### Response JSON Object
1. Response
  * Command (string) - The system call you made
  * Output (string) - uptime

###### Status Codes
1. 200 OK - Request completed successfully

###### Request
```
GET /uptime/s HTTP/1.1
Host: 192.168.13.37:8081
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 0


```

###### Response
```
 HTTP/1.0 200 OK
 Date: Wed, 17 Feb 2016 22:44:27 GMT
 Server: WSGIServer/0.1 Python/2.7.6
 Content-Length: 90
 Content-Type: text/html; charset=UTF-8
 
{
  "response": {
    "Command": "uptime -s", 
    "Output": "2016-02-17 09:42:44\n"
  }
}

```

### List of Vulnerabilities
Vulnerability Categories Include:

1. Transport Layer Security
2. User enumeration
3. Information exposure through server headers
4. Authentication bypass
5. User input validation
6. SQL injection
7. Error handling
8. Session management
9. Encryption
10. AuthN bypass
11. Command Injection
12. Regex DDoS

