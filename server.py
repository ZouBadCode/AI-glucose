from flask import Flask, request, jsonify, render_template, Response
import os
import json
from datetime import datetime
from datetime import datetime, timedelta
import openai
import base64
import requests
app = Flask(__name__)

###API Require

@app.route('/')
def render_main_page():  
    return render_template("main_page.html")

def find_nearest_hours(timestamp):
    # 將字符串格式的timestamp轉換為datetime對象
    specified_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    if specified_time.minute == 0:
        previous_hour = specified_time - timedelta(hours=1)
        next_hour = specified_time
    else:
        previous_hour = specified_time.replace(minute=0, second=0, microsecond=0)
        next_hour = previous_hour + timedelta(hours=1)
    
    return previous_hour, next_hour

def save_data_to_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)

def update_glucose_data(json_file, previous_hour, next_hour, new_data):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    updated = False
    for item in data:
        item_time = datetime.strptime(item["t"], '%Y-%m-%dT%H:%M:%S.%fZ')
        if previous_hour <= item_time < next_hour:
            item.update(new_data)
            updated = True
    
    if not updated:
        data.append(new_data)
    
    save_data_to_json(json_file, data)

@app.route('/submit', methods=['POST'])
def submit_glucose():
    data = request.json
    timestamp = data['t']

    previous_hour, next_hour = find_nearest_hours(timestamp)

    update_glucose_data('diabete_project_main/json/blood_sugar.json', previous_hour, next_hour, data)

    return jsonify({"status": "success", "message": "血糖值接收成功"})

@app.route("/view-plot")
def render_plot():
    return render_template("plot.html")

@app.route('/get-data', methods=['GET'])
def get_data():
    # 假設您的JSON數據存儲在data.json文件中
    with open('diabete_project_main/json/blood_sugar.json', 'r') as file:
        data = json.load(file)
    return jsonify(data)


@app.route('/guess_food', methods=['POST'])
def relay_to_gpt4v():
    if 'file' not in request.files:
        return jsonify({'message': '沒有檔案部分'})
    file = request.files['file']
    api_key = "INPUT API KEY"
    sendtofrontend = submit(file, api_key)
    print(sendtofrontend)
    return jsonify({'response': sendtofrontend})

def submit(image, api_key):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    image_data = image.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "system",
                "content": "你是一個專業的營養師",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "食物圖片，現在請你猜測此食物的碳水(g)數，並且給出此相關資訊，與此食物對糖尿病患者的影響，回答必須包含碳水g數，250字內",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        "max_tokens": 500,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()

    send_result = response.json()["choices"][0]["message"]["content"]
    return send_result

@app.route('/analyzejson', methods=['POST'])
def analyze_json():
    with open('C:/Users/User/Desktop/diabete/diabete_project_main/json/blood_sugar.json', 'r', encoding='utf-8') as file:
        g_json = json.load(file)
        api_key = "INPUT API KEY"
        result_advice = submit_advice(g_json, api_key)
        print(result_advice)
        return jsonify({'response': result_advice})
def submit_advice(data, api_key):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4-0125-preview",
        "messages": [
            {
                "role": "system",
                "content": "你是一個專業的營養師，你會分析數據(g:血糖,c:碳水(g),e:運動(min),i:胰島素,t:時間)，給出繁體中文建議",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{data},分析數據，給糖尿病患者護理建議，不要寫出數據分析過程，只給出建議，例如:注射劑量的調整、運動、飲食",
                    },
                ],
            },
        ],
        "max_tokens": 1000,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()

    send_result = response.json()["choices"][0]["message"]["content"]
    return send_result




@app.route('/cal-glu')
def cal_glu():
    return render_template("CAL.html")



if __name__ == '__main__':
    app.run(debug=True)





