# post_x.py  ← この名前で保存
import os
import time
import hmac
import hashlib
import binascii
import requests
from urllib.parse import quote

def post_with_media(status, image_path):
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

    oauth_nonce = binascii.b2a_hex(os.urandom(16)).decode()
    oauth_timestamp = str(int(time.time()))

    # ← これが最重要！statusも署名に含める！！
    params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": oauth_nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": oauth_timestamp,
        "oauth_token": access_token,
        "oauth_version": "1.0",
        "status": status  # ← ここを追加！これがないと401になる
    }

    # 正しい base string 作成
    base_string = "POST&" + quote("https://api.twitter.com/1.1/statuses/update_with_media.json") + "&" + \
                  quote("&".join([f"{quote(k)}={quote(v)}" for k, v in sorted(params.items())]))

    signing_key = f"{quote(consumer_secret)}&{quote(access_token_secret)}"
    oauth_signature = binascii.b2a_base64(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    )[:-1].decode()

    auth_header = (
        f'OAuth oauth_consumer_key="{consumer_key}", '
        f'oauth_nonce="{oauth_nonce}", '
        f'oauth_signature="{quote(oauth_signature)}", '
        f'oauth_signature_method="HMAC-SHA1", '
        f'oauth_timestamp="{oauth_timestamp}", '
        f'oauth_token="{access_token}", '
        f'oauth_version="1.0"'
    )

    files = {"media[]": open(image_path, "rb")}
    data = {"status": status}

    response = requests.post(
        "https://api.twitter.com/1.1/statuses/update_with_media.json",
        headers={"Authorization": auth_header},
        data=data,
        files=files
    )

    print("Status:", response.status_code)
    print("Response:", response.text)
    return response

if __name__ == "__main__":
    image_path = os.getenv("IMAGE_PATH", "etf_chart.png")
    status = f"レバレッジETFレポート　{time.strftime('%Y/%m/%d（%a）')}\n\nRSI（週足）70以上：SOXL TECL TQQQ\nRS387足）45以下：TSDD SPXS\n\n#レバレッジETF #米国株"

    post_with_media(status, image_path)
