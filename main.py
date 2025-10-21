from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import subprocess
import tempfile
import shutil
import requests

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")
USER_SECRET = os.getenv("USER_SECRET")

class Task(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: list
    evaluation_url: str
    attachments: list = []

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise Exception(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def create_github_repo(repo_name: str):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "name": repo_name,
        "private": False,
        "auto_init": False,
        "license_template": "mit"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repo {repo_name} created successfully")
    elif response.status_code == 422:
        # Repo exists
        print(f"Repo {repo_name} already exists")
    else:
        raise Exception(f"GitHub repo creation failed: {response.status_code} {response.text}")

def build_files(path, task, brief, round_num):
    os.makedirs(path, exist_ok=True)

    content = f"<html><head><title>{task}</title></head><body><h1>{brief}</h1>"
    if round_num == 2:
        content += "<p>Round 2 update applied!</p>"
    content += "</body></html>"

    with open(os.path.join(path, "index.html"), "w") as f:
        f.write(content)

    with open(os.path.join(path, "README.md"), "w") as f:
        f.write(f"# {task}\n\n{brief}\n\nLicensed under MIT.")

    with open(os.path.join(path, "LICENSE"), "w") as f:
        f.write("""MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
... rest of MIT License ...
""")

def push_repo(repo_name, path):
    run_cmd("git init", cwd=path)
    run_cmd('git config user.email "23f2002@ds.study.iitm.ac.in"', cwd=path)
    run_cmd('git config user.name "23f2002722"', cwd=path)
    run_cmd("git branch -m main", cwd=path)
    run_cmd(f"git remote add origin https://{GITHUB_TOKEN}@github.com/{USERNAME}/{repo_name}.git", cwd=path)
    run_cmd("git add .", cwd=path)
    run_cmd('git commit -m "Auto commit from LLM deployment"', cwd=path)
    run_cmd("git push -u origin main --force", cwd=path)

def enable_github_pages(repo_name):
    """Enable GitHub Pages source for the repo via GitHub API."""
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "source": {"branch": "main", "path": "/"}
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in (201, 204):
        print(f"GitHub Pages enabled for {repo_name}")
    elif response.status_code == 409:
        print("Pages already enabled or branch missing yet.")
    else:
        print(f"Failed to enable pages: {response.status_code} {response.text}")


@app.get("/")
async def root():
    return {"message": "API running. Use POST /api-endpoint to submit tasks."}

@app.post("/api-endpoint")
async def handle_request(req: Request):
    data = await req.json()

    if data.get("secret") != USER_SECRET:
        return {"error": "Invalid secret"}, 403

    task = data["task"].replace(" ", "-")
    round_num = data["round"]
    brief = data["brief"]
    email = data["email"]
    nonce = data["nonce"]
    eval_url = data["evaluation_url"]

    # Ensure repo exists or create it
    create_github_repo(task)

    temp_dir = tempfile.mkdtemp()

    try:
        build_files(temp_dir, task, brief, round_num)
        push_repo(task, temp_dir)
        enable_github_pages(task)

        repo_url = f"https://github.com/{USERNAME}/{task}"
        pages_url = f"https://{USERNAME}.github.io/{task}/"

        payload = {
            "email": email,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_url,
            "commit_sha": "latest",
            "pages_url": pages_url,
        }

        eval_response = requests.post(eval_url, json=payload)
        print(f"Evaluation server responded with status {eval_response.status_code}")

        return {"status": "ok", "repo_url": repo_url, "pages_url": pages_url}

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        shutil.rmtree(temp_dir)
