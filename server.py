import os
import sys
import torch
import numpy as np
from PIL import Image
from flask import Flask, jsonify, render_template, request, send_from_directory

# YOLOv5 모듈 경로 추가 (상대 경로)
sys.path.append('/Users/yuseunghun/yolov5')


from models.common import DetectMultiBackend
from utils.general import non_max_suppression
from utils.torch_utils import select_device
from utils.augmentations import letterbox

app = Flask(__name__)

# 상대 경로로 경로 지정
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'yolov5', 'tomato_project', 'yolov5s_results3', 'weights', 'best.pt')
DEVICE = 'cpu'

# 업로드 폴더 없으면 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 모델 로딩
model = DetectMultiBackend(MODEL_PATH, device=DEVICE)
model.eval()

CLASS_NAMES = ["정상", "곰팡이병", "세균성 점무늬병"]

def predict_yolov5(img_path):
    img = Image.open(img_path).convert('RGB')
    img = np.array(img)
    img = letterbox(img, new_shape=640)[0]
    img = img.transpose((2, 0, 1))
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(DEVICE).float() / 255.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    pred = model(img, augment=False)
    pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

    results = []

    if pred[0] is None or not isinstance(pred[0], torch.Tensor) or pred[0].ndim == 0 or len(pred[0]) == 0:
        return [{"result": "No tomato detected"}]

    for *xyxy, conf, cls in pred[0]:
        class_id = int(cls)
        label = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else str(class_id)
        results.append({"class": label, "confidence": float(conf)})

    return results

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "❌ No image part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "❌ No selected file"}), 400

    filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    return jsonify({"message": f"✅ Image {filename} uploaded successfully"}), 200

@app.route('/')
def home():
    return "Welcome to the Tomato AI Server! Visit /analyze-latest or /result for analysis."

@app.route('/analyze-latest')
def analyze_latest():
    files = sorted(os.listdir(UPLOAD_DIR))
    if not files:
        return jsonify({"result": "❌ No image found"})
    latest_file = os.path.join(UPLOAD_DIR, files[-1])
    result = predict_yolov5(latest_file)
    return jsonify({"result": result})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/result')
def show_result():
    files = sorted(os.listdir(UPLOAD_DIR))
    if not files:
        return "❌ 업로드된 이미지가 없습니다."

    latest_file = files[-1]
    image_url = f"/uploads/{latest_file}"
    result = predict_yolov5(os.path.join(UPLOAD_DIR, latest_file))

    return render_template("result.html", image_path=image_url, result=result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
