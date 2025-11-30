import os
import requests
from requests_oauthlib import OAuth1
from datetime import datetime
import pytz

# =====================
#  環境変数の取得
# =====================
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
IMAGE_PATH = os.getenv("IMAGE_PATH")
IMAGE_TYPE = os.getenv("IMAGE_TYPE", "ETF")  # ETF / BTC


# =====================
#  認証
# =====================
auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


# =====================
#  投稿文自動生成
# =====================
def generate_text(image_type):
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.now(jst)
    dt = now.strftime("%Y/%m/%d %H:%M")

    if image_type == "ETF":
        return f"""【レバレッジETF RSI 🧮】
更新時刻：{dt}

最新のRSI・市場状況をまとめました。
くわしくは画像をご覧ください📊

#ETF #レバレッジETF #投資 #RSI
"""
    else:  # BTC
        return f"""【BTC・暗号資産 RSI 📈】
更新時刻：{dt}

ビットコイン・マイニング関連銘柄の
RSIレポートです。

#Bitcoin #BTC #暗号資産 #仮想通貨 #RSI
"""


# =====================
#  メディアアップロード（v1.1）
# =====================
def upload_media(image_path):
    url = "https://upload.twitter.com/1.1/media/upload.json"

    with open(image_path, "rb") as f:
        files = {"media": f}
        response = requests.post(url, auth=auth, files=files)

    if response.status_code != 200:
        raise Exception(f"Media Upload Failed: {response.text}")

    media_id = response.json()["media_id_string"]
    print(f"✓ Media uploaded: {media_id}")
    return media_id


# =====================
#  ツイート投稿（v2）
# =====================
def post_tweet(text, media_id):
    url = "https://api.twitter.com/2/tweets"
    payload = {
        "text": text,
        "media": {"media_ids": [media_id]}
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        url,
        auth=auth,
        json=payload,
        headers=headers
    )

    print("Tweet status:", response.status_code)
    print(response.text)

    if response.status_code not in [200, 201]:
        raise Exception(f"Tweet Failed: {response.text}")


# =====================
#  メイン処理
# =====================
def main():
    print(f"Starting post_x.py for {IMAGE_TYPE}")
    print(f"Using image: {IMAGE_PATH}")

    media_id = upload_media(IMAGE_PATH)

    text = generate_text(IMAGE_TYPE)

    post_tweet(text, media_id)

    print("✓ Tweet posted successfully")


if __name__ == "__main__":
    main()
