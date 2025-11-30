import os
import time
import hmac
import hashlib
import binascii
import requests
from urllib.parse import quote

def create_oauth_header(consumer_key, consumer_secret, access_token, access_token_secret, status, media_path):
    oauth_nonce = binascii.b2a_hex(os.urandom(16)).decode('ascii')
    oauth_timestamp = str(int(time.time()))

    params = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': oauth_nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': oauth_timestamp,
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }

    # ベース文字列作成（statusも含める）
    base_params = params.copy()
    base_params['status'] = status
    base_string = 'POST&' + quote('https://api.twitter.com/1.1/statuses/update_with_media.json') + '&' + \
                  quote('&'.join([f'{quote(k)}={quote(v)}' for k, v in sorted(base_params.items())]))

    signing_key = f'{quote(consumer_secret)}&{quote(access_token_secret)}'
    oauth_signature = binascii.b2a_base64(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    )[:-1].decode('ascii')

    header = f'OAuth oauth_consumer_key="{consumer_key}", ' \
             f'oauth_nonce="{oauth_nonce}", ' \
             f'oauth_signature="{quote(oauth_signature)}", ' \
             f'oauth_signature_method="HMAC-SHA1", ' \
             f'oauth_timestamp="{oauth_timestamp}", ' \
             f'oauth_token="{access_token}", ' \
             f'oauth_version="1.0"'

    return header

# ============== メイン ==============
if __name__ == "__main__":
    ck = os.getenv("TWITTER_API_KEY")
    cs = os.getenv("TWITTER_API_SECRET")
    at = os.getenv("TWITTER_ACCESS_TOKEN")
    ats = os.getenv("TWITTER_ACCESS_SECRET")
    image_path = os.getenv("IMAGE_PATH", "etf_chart.png")  # デフォルトも対応

    # ここだけ好きなテキストに変更
    status = "レバレッジETFレポート　" + time.strftime("%Y/%m/%d（%a）") + \
             "\n\nRSI（週足）70以上：SOXL TECL TQQQ\nRSI（週足）45以下：TSDD SPXS\n\n#レバレッジETF #米国株"

    header = create_oauth_header(ck, cs, at, ats, status, image_path)

    files = {'media[]': open(image_path, 'rb')}
    data = {'status': status}

    r = requests.post(
        "https://api.twitter.com/1.1/statuses/update_with_media.json",
        headers={"Authorization": header},
        data=data,
        files=files
    )

    print("Status Code:", r.status_code)
    print("Response:", r.text)

    if r.status_code == 200:
        print("投稿成功！！！！！")
    else:
        print("失敗…でももうすぐだ！！")
