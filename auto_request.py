import os
import time
import requests

UPLOAD_DIR = "/Users/yuseunghun/uploads"
SERVER_URL = "http://192.0.0.2:10000/upload"  # 서버 IP 확인
SERVER_ANALYZE_URL = "http://192.0.0.2:5000/analyze-latest"  # 서버 IP 확인

def get_latest_image():
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('.jpg', '.jpeg'))]
    if not files:
        return None
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(UPLOAD_DIR, f)))
    return os.path.join(UPLOAD_DIR, latest_file)

def upload_image(image_path):
    with open(image_path, 'rb') as img:
        files = {'image': (os.path.basename(image_path), img, 'image/jpeg')}
        response = requests.post(SERVER_URL, files=files)
        return response

while True:
    try:
        latest_image = get_latest_image()
        if latest_image:
            print(f"🖼️ 최신 이미지: {latest_image}")
            
            # 서버에 이미지 업로드
            upload_response = upload_image(latest_image)
            if upload_response.status_code == 200:
                print("✅ 이미지 업로드 성공")
                
                # 분석 요청
                analyze_res = requests.get(SERVER_ANALYZE_URL)
                print("🧠 분석 결과:", analyze_res.json())
            else:
                print("❌ 이미지 업로드 실패:", upload_response.text)
        else:
            print("❌ 분석할 이미지가 없습니다.")
    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")

    time.sleep(60)  # 1분 대기
