# [en|de]crypt-python

## Requirements

Python 3: Tested on Python 3.10.6

Python packages: pycryptodome, Crypto, flask-restful

## Encryption

Using curl: 
```
curl -X POST -F "file=@yourfile.txt" http://localhost:5000/upload
```

## Decryption

Using curl:
``` 
curl -X GET http://localhost:5000/download/<file_id> -OJ
```
-OJ will use the filename from the Content-Disposition header

## Front-end website

Go to the following url: http://localhost:5000/
