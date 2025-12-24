# download_from_drive.py
import argparse
import json
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def build_drive_service(service_account_json: str):
  creds = service_account.Credentials.from_service_account_info(
      json.loads(service_account_json),
      scopes=["https://www.googleapis.com/auth/drive.readonly"],
  )
  return build("drive", "v3", credentials=creds)

def download_by_id(service, file_id: str, output_path: str):
  request = service.files().get_media(fileId=file_id)
  fh = io.FileIO(output_path, "wb")
  downloader = MediaIoBaseDownload(fh, request)

  done = False
  while not done:
    status, done = downloader.next_chunk()
    if status:
      print(f"Downloading... {int(status.progress() * 100)}%")

  print(f"✓ Downloaded by id: {file_id} -> {output_path}")

def find_first_by_name_in_folder(service, file_name: str, folder_id: str):
  # trashed=false かつ フォルダ内、同名一致
  query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
  results = (
      service.files()
      .list(
        q=query,
        # ✅ updatedTime を返して並び替えできるように
        fields="files(id, name, updatedTime)",
        # ✅ ついでに newest を先頭に
        orderBy="modifiedTime desc",
        pageSize=10,
      )
      .execute()
      .get("files", [])
  )
  if not results:
    raise Exception(f"Drive folder '{folder_id}' に '{file_name}' が見つかりません")
  return results[0]  # newest

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--id", required=False, help="Drive file id (preferred)")
  parser.add_argument("--name", required=False, help="Drive file name (fallback)")
  parser.add_argument("--output", required=True, help="Save path")
  args = parser.parse_args()

  service_account_json = os.environ["GOOGLE_SERVICE_ACCOUNT"]
  folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

  service = build_drive_service(service_account_json)

  if args.id:
    download_by_id(service, args.id, args.output)
  else:
    if not args.name:
      raise SystemExit("ERROR: --id か --name のどちらかを指定してください")
    f = find_first_by_name_in_folder(service, args.name, folder_id)
    print(f"Using newest by name: {f['name']} id={f['id']} updatedTime={f.get('updatedTime')}")
    download_by_id(service, f["id"], args.output)
