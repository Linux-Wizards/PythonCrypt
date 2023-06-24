from flask import Flask, request, send_file
from flask_restful import Resource, Api
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import os
import json

app = Flask(__name__)
api = Api(app)

BLOCK_SIZE = 16  # Bytes


class UploadAPI(Resource):
    def post(self):
        file = request.files['file']
        filename = file.filename
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_data = cipher.encrypt(pad(file.read(), BLOCK_SIZE))
        encrypted_filename = b64encode(cipher.encrypt(pad(bytes(filename, 'utf-8'), BLOCK_SIZE))).decode('utf-8')
        
        # save the encrypted data and the key together
        with open(f'encrypted_files/{encrypted_filename}', 'wb') as enc_file:
            enc_file.write(key + encrypted_data)

        return {"message": "File uploaded and encrypted successfully", "file_id": encrypted_filename}, 200


class DownloadAPI(Resource):
    def get(self, file_id):
        with open(f'encrypted_files/{file_id}', 'rb') as enc_file:
            data = enc_file.read()

        # the first 16 bytes are the key
        key = data[:16]
        encrypted_data = data[16:]
        cipher = AES.new(key, AES.MODE_ECB)

        decrypted_data = unpad(cipher.decrypt(encrypted_data), BLOCK_SIZE)
        with open(f'tmp/{file_id}', 'wb') as dec_file:
            dec_file.write(decrypted_data)

        return send_file(f'tmp/{file_id}', as_attachment=True)


api.add_resource(UploadAPI, '/upload')
api.add_resource(DownloadAPI, '/download/<string:file_id>')

if __name__ == '__main__':
    if not os.path.exists('encrypted_files'):
        os.makedirs('encrypted_files')
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    app.run(debug=True)
