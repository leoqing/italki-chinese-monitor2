import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
import os

# 配置从环境变量读取（GitHub Secrets）
SMTP_SERVER = "smtp.qq.com"  # QQ 示例，Gmail 用 smtp.gmail.com
SMTP_PORT = 465
SENDER_EMAIL = os.environ.get('SMTP_EMAIL')
SENDER_PASSWORD = os.environ.get('SMTP_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')
SERVER_CHAN_KEY = os.environ.get('SERVER_CHAN_KEY')

URL = "https://support.italki.com/hc/en-us/articles/115001499873-Is-my-language-open-for-application"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def send_email(subject, content):
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
        print("邮箱配置不全，跳过邮件发送")
        return
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] 邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def send_server_chan(title, content):
    if not SERVER_CHAN_KEY:
        print("Server酱 Key 未配置，跳过微信推送")
        return
    try:
        url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
        data = {"title": title, "desp": content}
        requests.post(url, data=data, timeout=10)
        print(f"[{datetime.now()}] 微信推送成功")
    except Exception as e:
        print(f"微信推送失败: {e}")

def is_chinese_open():
    try:
        r = requests.get(URL, headers=headers, timeout=10)
        r.raise_for_status()
        text = r.text
        import re
        # 如果没列 Chinese = Open；否则找 Open/Closed
        if "Chinese" not in text:
            return True
        pattern = r'Chinese.*?>(Open|Closed)'
        match = re.search(pattern, text, re.I | re.S)
        return match and "Open" in match.group(1)
    except Exception as e:
        print(f"页面检查失败: {e}")
        return None

def main():
    print(f"[{datetime.now()}] 开始检查 italki 中文状态...")
    status = is_chinese_open()
    if status is None:
        print("检查失败")
        return
    if status:
        msg = (f"🎉 italki 中文教学申请已开放！\n"
               f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
               "申请链接：https://support.italki.com/hc/en-us/articles/115001499873-Is-my-language-open-for-application")
        send_email("italki 中文开放啦！", msg)
        send_server_chan("italki 中文开放！", msg)
        print("✅ 中文开放，已发送提醒！")
    else:
        print("❌ 中文仍 Closed，继续等待...")

if __name__ == "__main__":
    main()
