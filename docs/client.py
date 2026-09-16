import io
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from sheets.auth import get_credentials


def _drive_service():
    return build("drive", "v3", credentials=get_credentials())


def create_doc(title: str, content: str, folder_id: Optional[str] = None) -> str:
    """Create a native Google Doc from plain-text content.

    Uploads the content as plain text and lets Drive auto-convert it into
    a native Google Doc, optionally placed inside `folder_id`. Returns the
    new file's ID.
    """
    drive = _drive_service()
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
    }
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaIoBaseUpload(io.BytesIO(content.encode("utf-8")), mimetype="text/plain")
    file = drive.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
    return file
