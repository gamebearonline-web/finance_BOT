# download_from_drive.py
import argparse
import json
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def download_file_from_drive(file_name, output_path, service_account_json, folder_id):
  """Google Drive の指定フォルダから file_name を検索しダウンロード"""

  creds = service_account.Credentials.from_service_account_info(
      json.loads(service_account_json),
      scopes=["https://www.googleapis.com/auth/drive.readonly"],
  )

  service = build("drive", "v3", credentials=creds)

  # 指定フォルダ内のみ検索
  query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"

  results = (
      service.files()
      .list(q=query, fields="files(id, name)")
      .execute()
      .get("files", [])
  )

  if not results:
    raise Exception(f"Drive フォルダ内に '{file_name}' が見つかりません")

  file_id = results[0]["id"]

  request = service.files().get_media(fileId=file_id)
  fh = io.FileIO(output_path, "wb")
  downloader = MediaIoBaseDownload(fh, request)

  done = False
  while not done:
    _, done = downloader.next_chunk()

  print(f"✓ Downloaded: {output_path}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--name", required=True, help="Drive file name")
  parser.add_argument("--output", required=True, help="Save path")
  args = parser.parse_args()

  service_account_json = os.environ["GOOGLE_SERVICE_ACCOUNT"]
  folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

  download_file_from_drive(args.name, args.output, service_account_json, folder_id)
