import json
import os
import io

from typing import Any, Optional, Iterable

from MonitoringService.src.collectors.base import BaseCollector

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload


class GoogleDriveCollector(BaseCollector):

    def __init__(self, scp='https://www.googleapis.com/auth/drive'):
        self.SCOPES = [scp]
        self.creds = service_account.Credentials.from_service_account_file('service_credentials.json',
                                                                           scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.creds)

    async def fetch_start_page_token(self) -> int:
        if os.path.exists('newStartPageToken'):
            with open('newStartPageToken', 'r') as f:
                try:
                    text = json.load(f)
                    return text['newStartPageToken']
                except:
                    print("Page token not found")
        return 1

    async def check_new_files(self, saved_start_page_token, **kwargs: Any) -> Optional[list]:
        try:
            page_token = saved_start_page_token
            changes = []
            while page_token is not None:
                response = self.service.changes().list(pageToken=page_token, includeRemoved=False).execute()
                changes = changes + [a.get('file') for a in response.get('changes') if a.get("file").get("mimeType") == "application/pdf"]

                if 'newStartPageToken' in response:
                    saved_start_page_token = response.get('newStartPageToken')
                    with open('newStartPageToken', 'w') as f:
                        json.dump({"newStartPageToken": saved_start_page_token}, f)

                page_token = response.get('nextPageToken')
        except HttpError as error:
            print(f'An error occurred: {error}')

        return changes

    async def collect(self, files: list, **kwargs: Any) -> None:
        for file in files:
            print(file)
            try:
                request = self.service.files().get_media(fileId=file['id'])
                buffer = io.BytesIO()
                downloader = MediaIoBaseDownload(buffer, request)

                print(F"File {file['name']} started:")
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(F'Download {int(status.progress() * 100)}')

                with open(f"pdf_files/{file['name']}.pdf", "wb") as f:
                    f.write(buffer.getvalue())

            except HttpError as error:
                print(f"File {file['name']}: An error occurred: {error}")

    async def process(self, **kwargs: Any):
        pass
