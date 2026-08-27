"""
GitHub Direct Uploader for Animaker AI
Uploads project files directly to GitHub Repository using GitHub API without needing Git installed.
"""

import os
import sys
import base64
import requests

REPO_OWNER = "paipai1999"
REPO_NAME = "pai-ai-animation-video"
BRANCH = "main"

# Excluded folders and files
EXCLUDE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", ".next", "out",
    "build", "dist", ".gemini", "storage"
}
EXCLUDE_FILES = {
    ".env", ".env.local", "cloudflared", "cloudflared.exe", "app.db"
}
EXCLUDE_EXTS = {
    ".mp4", ".mp3", ".wav", ".png", ".jpg", ".jpeg", ".db", ".sqlite", ".log"
}


def should_upload_file(rel_path: str) -> bool:
    parts = rel_path.replace("\\", "/").split("/")
    for p in parts[:-1]:
        if p in EXCLUDE_DIRS:
            return False
    filename = parts[-1]
    if filename in EXCLUDE_FILES:
        return False
    ext = os.path.splitext(filename)[1].lower()
    if ext in EXCLUDE_EXTS:
        # Keep essential assets if any
        if not (filename.endswith(".png") and "favicon" in filename):
            return False
    return True


def get_all_files(root_dir: str):
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        # filter dirs in place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, root_dir).replace("\\", "/")
            if should_upload_file(rel_path):
                file_list.append((full_path, rel_path))
    return file_list


def upload_to_github(token: str):
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    base_api = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

    # 1. Test token and repository access
    print(f"🔍 Checking repository access for {REPO_OWNER}/{REPO_NAME}...")
    res = requests.get(base_api, headers=headers)
    if res.status_code == 401:
        print("❌ Error: Invalid GitHub Token. Please check your Personal Access Token (PAT).")
        return False
    elif res.status_code == 404:
        print(f"❌ Error: Repository {REPO_OWNER}/{REPO_NAME} not found or token has no access.")
        return False
    elif res.status_code != 200:
        print(f"❌ Error accessing repo: {res.status_code} - {res.text}")
        return False

    print("✅ Repository access confirmed!")

    files = get_all_files(os.getcwd())
    print(f"📦 Total files to upload: {len(files)}")

    success_count = 0
    for full_path, rel_path in files:
        try:
            with open(full_path, "rb") as f:
                content_bytes = f.read()

            content_b64 = base64.b64encode(content_bytes).decode("utf-8")

            # Check if file already exists on GitHub to get sha
            file_url = f"{base_api}/contents/{rel_path}"
            check_res = requests.get(file_url, headers=headers, params={"ref": BRANCH})
            sha = check_res.json().get("sha") if check_res.status_code == 200 else None

            payload = {
                "message": f"Upload {rel_path}",
                "content": content_b64,
                "branch": BRANCH
            }
            if sha:
                payload["sha"] = sha

            put_res = requests.put(file_url, headers=headers, json=payload)
            if put_res.status_code in [200, 201]:
                print(f"  ✓ Uploaded: {rel_path}")
                success_count += 1
            else:
                print(f"  ⚠️ Failed ({put_res.status_code}): {rel_path}")
        except Exception as e:
            print(f"  ⚠️ Error uploading {rel_path}: {e}")

    print("\n" + "=" * 60)
    print(f"🎉 Upload Complete! {success_count}/{len(files)} files uploaded.")
    print(f"👉 View your repository: https://github.com/{REPO_OWNER}/{REPO_NAME}")
    print("=" * 60 + "\n")
    return True


if __name__ == "__main__":
    token = ""
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("=" * 60)
        print("  🚀 GITHUB DIRECT FILE UPLOADER (NO GIT REQUIRED)")
        print("=" * 60)
        print("Please enter your GitHub Personal Access Token (PAT):")
        print("(You can create one at: https://github.com/settings/tokens)")
        token = input("GitHub Token: ").strip()

    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)

    upload_to_github(token)
