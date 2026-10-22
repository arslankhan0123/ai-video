# YouTube Auto-Upload — one-time setup

`python talk.py --upload` publishes the finished video to your channel. Before
the first upload, set up API access (takes ~10 minutes, done once).

## Steps
1. Go to **console.cloud.google.com** and create (or pick) a project.
2. **APIs & Services → Library →** enable **"YouTube Data API v3"**.
3. **APIs & Services → OAuth consent screen:** configure it (External is fine),
   and under **Test users** add your own Google account (the channel owner).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →**
   Application type **Desktop app**. Download the JSON.
5. Rename that file to **`client_secret.json`** and put it in the project root
   (`C:\Users\Arslan Khan\ai-video\client_secret.json`).

## First upload
```
python talk.py --upload
```
A browser window opens asking you to sign in and allow upload access. After you
approve, a `youtube_token.json` is saved and reused — you won't be asked again.

## Privacy
- Default is **private** (safe). To publish publicly:
  ```
  python talk.py --upload --privacy public
  ```
  or set `YT_PRIVACY = "public"` in `generator/talking_config.py`.

## Important limitation (read this)
YouTube restricts videos uploaded through the API by **unverified** projects:
they may be forced to **private** regardless of the privacy you set, until your
Google Cloud project passes YouTube's API audit. For a brand-new project:
- The upload works and the video appears in **YouTube Studio**.
- It may stay **private/locked** until you either request an audit, or simply
  open the video in YouTube Studio and switch it to Public manually.

So "fully automatic public upload" may require the one-time audit. Until then,
the script uploads it for you and you flip it to Public in Studio with one click.

## Files this creates (keep them private — never commit to git)
- `client_secret.json`  — your OAuth app secret
- `youtube_token.json`  — your saved login token
Add both to `.gitignore`.
