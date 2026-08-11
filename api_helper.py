"""
API接口对接 + 消息通知工具
影刀用法：传入参数调API，返回结果给影刀
"""

import requests
import json
import hashlib
import time
import hmac


class APIClient:
    """通用API客户端"""
    
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint, params=None, headers=None):
        """GET请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def post(self, endpoint, data=None, json_data=None, headers=None):
        """POST请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = self.session.post(url, data=data, json=json_data, 
                                  headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def put(self, endpoint, json_data=None, headers=None):
        """PUT请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = self.session.put(url, json=json_data, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def delete(self, endpoint, headers=None):
        """DELETE请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = self.session.delete(url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()


class WeComNotifier:
    """企业微信机器人通知"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_text(self, content, mentioned_list=None):
        """发送文本"""
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or []
            }
        }
        return self._post(data)
    
    def send_markdown(self, content):
        """发送Markdown"""
        data = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }
        return self._post(data)
    
    def send_news(self, title, description, url, pic_url=''):
        """发送图文"""
        data = {
            "msgtype": "news",
            "news": {
                "articles": [{
                    "title": title,
                    "description": description,
                    "url": url,
                    "picurl": pic_url
                }]
            }
        }
        return self._post(data)
    
    def _post(self, data):
        resp = requests.post(self.webhook_url, json=data, timeout=10)
        return resp.json()


def dingtalk_notify(webhook_url, msg, at_mobiles=None):
    """钉钉机器人通知"""
    data = {
        "msgtype": "text",
        "text": {"content": msg},
        "at": {"atMobiles": at_mobiles or []}
    }
    resp = requests.post(webhook_url, json=data, timeout=10)
    return resp.json()


def feishu_notify(webhook_url, title, content):
    """飞书机器人通知"""
    data = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [{"tag": "text", "text": content}]
                    ]
                }
            }
        }
    }
    resp = requests.post(webhook_url, json=data, timeout=10)
    return resp.json()


def call_api_with_sign(api_url, api_key, api_secret, params, method='POST'):
    """带签名的API调用"""
    timestamp = str(int(time.time()))
    
    # MD5签名
    sign_str = f"{api_key}{timestamp}{json.dumps(params, ensure_ascii=False)}{api_secret}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key,
        'X-Timestamp': timestamp,
        'X-Sign': sign
    }
    
    if method.upper() == 'POST':
        resp = requests.post(api_url, json=params, headers=headers, timeout=30)
    else:
        resp = requests.get(api_url, params=params, headers=headers, timeout=30)
    
    resp.raise_for_status()
    return resp.json()


# ===== 影刀入口 =====
if __name__ == '__main__':
    # 企业微信通知
    webhook = "{{企业微信Webhook地址}}"
    msg_type = "{{消息类型}}"  # text / markdown
    
    if msg_type == 'text':
        notifier = WeComNotifier(webhook)
        result = notifier.send_text("{{消息内容}}")
    else:
        notifier = WeComNotifier(webhook)
        result = notifier.send_markdown("{{Markdown内容}}")
    
    # 输出到影刀
    notify_result = result
