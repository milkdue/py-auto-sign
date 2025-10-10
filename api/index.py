import requests
from http.server import BaseHTTPRequestHandler
import json
import os
from google import genai

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
def comment_action(token, data):
    url = f"{base_url}/edu-api/forum/add/comment";
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
def get_post_list(token):
    url = f"{base_url}/edu-api/forum/query/postList";
    headers = {
        "token": token
    };
    data = {
        "keyword": "",
        "lable": "",
        "order": "",
        "page": 1,
        # "pageSize": 12,
        "pageSize": 3,
        "type": "全部"
    };
    try:
        response = requests.post(url, json=data, headers=headers);
        if response.status_code == 200:
            resp = response.json();
            if resp["code"] != "ok":
                print("查询失败 code != ok");
                return None;
            else:
                return resp["data"]["result"];
        else:
            print("网络异常");
            return None;
    except requests.exceptions.RequestException as e:
        print(f"<UNK> : {e}");
        return None;
def get_post_detail(token, id):
    url = f"{base_url}/edu-api/forum/query/detail?id={id}";
    headers = {
        "token": token
    };
    try:
        response = requests.get(url, headers=headers);
        if response.status_code == 200:
            resp = response.json();
            if resp["code"] != "ok":
                print("查询详细失败，code != ok")
                return None;
            else:
                return resp["data"];
        else:
            print("未知错误");
            return None;
    except requests.exceptions.RequestException as e:
        print(f"<UNK> : {e}");
        return None;
def get_post_detail_comment(token, id, page_size):
    url = f"{base_url}/edu-api/forum/query/detailCommentList?page=1&pageSize={page_size}&postId={id}";
    headers = {
        "token": token
    };
    try:
        response = requests.get(url, headers=headers);
        if response.status_code == 200:
            resp = response.json();
            if resp["code"] != "ok":
                print("<UNK>code != ok");
                return None;
            else:
                return resp["data"]["result"];
        else:
            print("<UNK> 网络异常");
            return None;
    except requests.exceptions.RequestException as e:
        print(f"<UNK> : {e}");
        return None;

def comment(token):
    post_list = get_post_list(token);
    ai_count = 0;
    if post_list is not None:
        if len(post_list) != 0:
            for post in post_list:
                if post["postTopFlag"]:
                    continue;
                flag = True;
                if post["postCommentNum"] != 0:
                    comment_list = get_post_detail_comment(token, post["id"], post["postCommentNum"]);
                    if comment_list is not None:
                        flag = any(c["userId"] == "100393409317300076544" for c in comment_list);

                if flag:
                    detail = get_post_detail(token, post["id"]);
                    if detail is not None:
                        content = f"{detail["postTitle"]} {detail["postContent"]}";
                        api_key = os.environ.get("GOOGLE_API_KEY");
                        client = genai.Client(api_key=api_key);
                        model = "gemini-2.0-flash";
                        response = client.models.generate_content(
                            model=model,
                            contents=content
                        );
                        if response.text:
                            ai_count += 1;
                            comment_action(token, { "postId": post["id"], "commentContent": response.text + "\n---本次回答由gemini提供。" });

    for i in range(10 - ai_count):
        comment_action(token, { "commentContent": "1", "commentId": "718840335383396352", "postId": "718771683434954752", "rootId": "718840335383396352"});

def task():
    userList = os.environ.get("USER_INFO_LIST");
    print(userList);
    userList = userList.split(",");
    for user in userList:
        username = user.split("=")[0];
        password = user.split("=")[1];
        user_info = login(username, password)
        if user_info:
            token = user_info["token"];
            sign(token);
            comment(token);
    return;

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        task();
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"code": "ok", "message": "定时任务已启动，每日8点进行执行"}).encode("utf-8"));
        return

if __name__ == '__main__':
    userList = "1524=api_key"
    userList = userList.split(",");
    print(userList);
    for user in userList:
        username = user.split("=")[0];
        password = user.split("=")[1];
        print(username);
        print(password);
        user_info = login(username, password);
        token = user_info["token"];




