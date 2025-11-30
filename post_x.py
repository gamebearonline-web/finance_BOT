import os
import tweepy
import sys
from datetime import datetime
import pytz
import mimetypes

def main():
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print("[ERROR] Twitter API credentials が不足しています")
        sys.exit(1)
    
    image_path = os.getenv("IMAGE_PATH", "etf_chart.png")
    if not os.path.exists(image_path):
        print(f"[ERROR] 画像ファイルが見つかりません → {image_path}")
        sys.exit(1)

    # ファイルサイズチェック
    size = os.path.getsize(image_path)
    if size == 0:
        print(f"[ERROR] 画像が0バイトです → {image_path}")
        sys.exit(1)
    print(f"[INFO] 画像サイズ: {size} bytes")

    # 拡張子が無ければ強制で .png を付ける（これが最重要！）
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        temp_path = image_path + ".png"
        os.rename(image_path, temp_path)
        image_path = temp_path
        print(f"[INFO] 拡張子を追加 → {image_path}")

    # MIMEタイプを明示的に付与（これで確実に通る）
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"  # デフォルトはpng
    print(f"[INFO] 検出されたMIME: {mime_type}")

    # JST日付
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    date_str = now.strftime("%Y/%m/%d（%a）")

    # 投稿文
    chart_type = os.getenv("CHART_TYPE", "ETF")
    if chart_type == "BTC":
        tweet_text = f"BTC・取引所・マイニング銘柄レポート　{date_str}\n\nRSI（週足）70以上：MARA RIOT CLSK\nRSI（週足）40以下：該当なし\n\n#Bitcoin #BTC #暗号資産"
    else:
        tweet_text = f"レバレッジETFレポート　{date_str}\n\nRSI（週足）70以上：SOXL TECL TQQQ\nRSI（週足）45以下：TSDD SPXS\n\n#レバレッジETF #米国株"

    print(f"[INFO] 投稿文:\n{tweet_text}")

    # ===== v1.1 画像アップロード（ここが最重要修正）=====
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret,
            access_token, access_token_secret
        )
        api_v1 = tweepy.API(auth)
        
        # ここで filename= と mime_type= を明示的に渡す
        media = api_v1.media_upload(
            filename=image_path,
            file=open(image_path, 'rb'),
            media_category="tweet_image",
            mime_type=mime_type
        )
        media_id = str(media.media_id)
        print(f"[SUCCESS] 画像アップロード成功 → media_id={media_id}")
    except Exception as e:
        print("[ERROR] 画像アップロード失敗:", repr(e))
        sys.exit(1)

    # ===== v2 投稿 =====
    try:
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        tweet_id = response.data["id"]
        user_info = client.get_me()
        username = user_info.data.username
        print(f"[VICTORY] 投稿完了 → https://x.com/{username}/status/{tweet_id}")
    except Exception as e:
        print("[ERROR] 投稿失敗:", repr(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
