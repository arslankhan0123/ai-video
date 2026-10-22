"""
Upload a finished video to YouTube via the YouTube Data API v3.

One-time setup (see YOUTUBE-SETUP.md):
  1. In Google Cloud Console: enable "YouTube Data API v3".
  2. Create an OAuth client (type: Desktop app) and download the JSON as
     `client_secret.json` into the project root.
  3. First run opens a browser to authorize your channel; the token is then
     saved to `youtube_token.json` and reused.

Requires:
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
"""

import os

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_credentials(root):
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    token_path = os.path.join(root, "youtube_token.json")
    secret_path = os.path.join(root, "client_secret.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secret_path):
                raise RuntimeError(
                    "Missing client_secret.json in the project folder. "
                    "See YOUTUBE-SETUP.md to create it."
                )
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds


def upload(video_path, title, description, tags, root,
           privacy="private", category_id="24", made_for_kids=False):
    """
    Upload `video_path` to YouTube. Returns the video id.
    privacy: "private" | "unlisted" | "public".
    category 24 = Entertainment.
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    creds = _get_credentials(root)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4900],
            "tags": tags[:30],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True,
                            mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body,
                                      media_body=media)

    print(f"  → uploading to YouTube ({privacy}) ...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    {int(status.progress() * 100)}% uploaded")

    vid = response["id"]
    print(f"  ✓ uploaded: https://youtu.be/{vid}  (privacy: {privacy})")
    return vid
