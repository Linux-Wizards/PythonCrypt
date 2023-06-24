# [en|de]crypt-pyton
Requirements: pycryptodome, pycrypto, Crypto, flask-restful

Upload and encrypt -> curl -X POST -F "file=@yourfile.txt" http://localhost:5000/upload

Download and decrypt -> curl -X GET http://localhost:5000/download/<file_id> --output downloaded_file.txt
