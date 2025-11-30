import os
import requests
from requests_oauthlib import OAuth1

# =====================
#  環境変数の取得
# =====================
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

IMAGE_PATH = os.getenv("IMAGE_PATH")
POST_TEXT = os.getenv("POST_TEXT")  # ★ ここが重要（GAS→GitHubから渡す文章）


# =====================
#  認証（OAuth1.0a）
# =====================
auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


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
    print(f"Starting post_x.py")
    print(f"Using image: {IMAGE_PATH}")

    if not IMAGE_PATH:
        raise Exception("IMAGE_PATH が設定されていません")

    if not POST_TEXT:
        raise Exception("POST_TEXT（投稿文章）が空です。workflow_dispatch で渡してください。")

    # 画像アップロード
    media_id = upload_media(IMAGE_PATH)

    # 投稿
    post_tweet(POST_TEXT, media_id)

    print("✓ Tweet posted successfully")


if __name__ == "__main__":
    main()
