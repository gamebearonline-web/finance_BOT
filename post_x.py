import os
import tweepy
import sys
from datetime import datetime
import pytz

def main():
    # GitHub Secrets / 環境変数から取得
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print("[ERROR] Twitter API credentials が不足しています")
        sys.exit(1)
    
    # 画像パス（ETF or BTCで切り替え）
    image_path = os.getenv("IMAGE_PATH", "etf_chart.png")
    if not os.path.exists(image_path):
        print(f"[ERROR] 画像ファイルが見つかりません → {image_path}")
        sys.exit(1)

    # ===== JST 現在時刻 =====
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    date_str = now.strftime("%Y/%m/%d（%a）")

    # ===== 投稿文（ETF or BTCで切り替え） =====
    chart_type = os.getenv("CHART_TYPE", "ETF")  # ETF or BTC
    if chart_type == "BTC":
        tweet_text = f"BTC・取引所・マイニング銘柄レポート　{date_str}\n\nRSI（週足）70以上：MARA RIOT CLSK\nRSI（週足）40以下：該当なし\n\n#Bitcoin #BTC #暗号資産"
    else:
        tweet_text = f"レバレッジETFレポート　{date_str}\n\nRSI（週足）70以上：SOXL TECL TQQQ\nRSI（週足）45以下：TSDD SPXS\n\n#レバレッジETF #米国株"

    print(f"[INFO] 投稿タイプ: {chart_type}")
    print(f"[INFO] 投稿文: {tweet_text}")

    # ===== v1.1 (画像アップロード) =====
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret,
            access_token, access_token_secret
        )
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=image_path)
        media_id = str(media.media_id)
        print(f"[INFO] 画像アップロード成功 → media_id={media_id}")
    except Exception as e:
        print("[ERROR] 画像アップロード失敗:", repr(e))
        sys.exit(1)

    # ===== v2 (投稿) =====
    try:
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        response = client.create_tweet(
            text=tweet_text,
            media_ids=[media_id]
        )
        tweet_id = response.data["id"]
        # username の取得（安全に処理）
        try:
            user_info = client.get_me()
            username = user_info.data.username if user_info.data else "unknown_user"
        except:
            username = "unknown_user"
        print(f"[SUCCESS] 投稿完了 → https://x.com/{username}/status/{tweet_id}")
        print(f"[INFO] 投稿内容:\n{tweet_text}")
    except Exception as e:
        print("[ERROR] ツイート投稿失敗:", repr(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
