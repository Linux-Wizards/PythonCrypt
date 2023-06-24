from flask import Flask, request, send_file, redirect
from flask_restful import Resource, Api
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from flask_cors import CORS
import uuid
import os

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"*": {"origins": "*"}})



BLOCK_SIZE = 16  # Bytes
key_location = './key.key'


def generate_key():
    # This function will generate a key and save it into a file
    if not os.path.exists(key_location):
        key = get_random_bytes(16)
        with open(key_location, 'wb') as key_file:
            key_file.write(key)


def get_key():
    # This function will load the key
    with open(key_location, 'rb') as key_file:
        key = key_file.read()
    return key


class UploadAPI(Resource):
    def post(self):
        file = request.files['file']
        filename = file.filename
        key = get_key()
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_filename = str(uuid.uuid4())
        encrypted_data = cipher.encrypt(pad(file.read(), BLOCK_SIZE))
        metadata_filename = encrypted_filename + '.metadata'
        encrypted_metadata = cipher.encrypt(pad(bytes(filename, 'utf-8'), BLOCK_SIZE))
        
        with open(f'encrypted_files/{encrypted_filename}', 'wb') as enc_file:
            enc_file.write(encrypted_data)

        with open(f'encrypted_files/{metadata_filename}', 'wb') as meta_file:
            meta_file.write(encrypted_metadata)

        return {"message": "File uploaded and encrypted successfully", "file_id": encrypted_filename}, 200


class DownloadAPI(Resource):
    def get(self, file_id):
        key = get_key()
        cipher = AES.new(key, AES.MODE_ECB)
        with open(f'encrypted_files/{file_id}', 'rb') as enc_file:
            encrypted_data = enc_file.read()

        with open(f'encrypted_files/{file_id}.metadata', 'rb') as enc_metadata_file:
            encrypted_metadata = enc_metadata_file.read()

        decrypted_data = unpad(cipher.decrypt(encrypted_data), BLOCK_SIZE)
        decrypted_metadata = unpad(cipher.decrypt(encrypted_metadata), BLOCK_SIZE)
        with open(f'tmp/{file_id}', 'wb') as dec_file:
            dec_file.write(decrypted_data)

        return send_file(f'tmp/{file_id}', as_attachment=True, download_name=decrypted_metadata.decode())

@app.route('/')
def redirect_index():
    return redirect("/static/index.html", code=301)

api.add_resource(UploadAPI, '/upload')
api.add_resource(DownloadAPI, '/download/<string:file_id>')


if __name__ == '__main__':
    if not os.path.exists('encrypted_files'):
        os.makedirs('encrypted_files')
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    generate_key()
    app.run(debug=True)
