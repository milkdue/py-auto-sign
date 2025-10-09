import requests
import time
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from threading import Timer
import json
import os

base_url = "https://edu.definesys.cn";

def login(username, password):
    url = f"{base_url}/edu-api/user/login";
    data = {
        "type": "account",
        "phone": username,
        "password": password
    };
    try:
        response = requests.post(url, json=data);
        if response.status_code == 200:
            resp = response.json();
            if resp["code"] == "ok":
                return resp["data"];
            else:
                return None;
        else:
            print(f"登录失败: {response.status_code}");
            return None;
    except requests.exceptions.RequestException as e:
        print(f"登录失败: {e}");
        return None;

def sign(token):
    url = f"{base_url}/edu-api/forumSign/sign";
    headers = {
        "token": token
    }
    try:
        requests.get(url, headers=headers);
    except requests.exceptions.RequestException as e:
        print(f"<UNK>: {e}");
    return
def comment(token):
    url = f"{base_url}/edu-api/forum/add/comment";
    data = {
        "commentContent": "你说的对",
        "commentId": "718840335383396352",
        "postId": "718771683434954752",
        "rootId": "718840335383396352"
    }
    headers = {
        "token": token
    }
    try:
        response = requests.post(url, json=data, headers=headers);
        if response.status_code == 200:
            resp = response.json();
            if resp["code"] != "ok":
                return print(f"评论失败 {resp}");
            else:
                return resp;
        else:
            print(f"评论失败 {response.status_code}");
            return None;
    except requests.exceptions.RequestException as e:
        print(f"评论失败 : {e}");
        return None;

def task():
    user_info = login("15249152404", "welcome1")
    if user_info:
        token = user_info["token"];
        sign(token);
        for i in range(10):
            comment(token);
            time.sleep(2);
    return;

def task2():
    # 设置定时任务，每天早上8点执行
    # 计算从现在到明天早上8点的秒数
    seconds = (datetime.now().replace(hour=17, minute=0, second=0, microsecond=0) - datetime.now()).total_seconds();
    # 如果已经过了今天的执行时间，则加上一天的秒数
    if seconds < 0:
        seconds += 86400
    # 创建并启动定时器
    Timer(seconds, task).start();

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"code": "ok", "message": "定时任务已启动，每日8点进行执行"}).encode("utf-8"));
        return

if __name__ == '__main__':
    print('PY-AUTO-SIGN');

