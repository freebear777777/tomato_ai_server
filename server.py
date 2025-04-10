# server.py
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Tomato AI Server is Running!'

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No image part in the request', 400

    image = request.files['image']
    if image.filename == '':
        return 'No selected image', 400

    os.makedirs("uploads", exist_ok=True)
    save_path = os.path.join("uploads", image.filename)
    image.save(save_path)

    return f'Image saved to {save_path}', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render가 포트 환경변수로 줌
    app.run(host='0.0.0.0', port=port)
