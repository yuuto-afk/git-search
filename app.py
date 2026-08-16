import os
import shutil
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("diff.html")

@app.route("/clone", methods=["POST"])
def clone_repo():
    data = request.get_json()
    repo_url = data["url"]

    if os.path.exists("repo-dir"):
        shutil.rmtree("repo-dir")

    # clone
    result = subprocess.run(
        ["GIT_LFS_SKIP_SMUDGE=1 git clone {repo_url} repo-dir".format(repo_url=repo_url)],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

    # ブランチ一覧取得
    branches_raw = subprocess.run(
        ["git", "-C", TARGET_DIR, "branch", "-a"],
        stdout=subprocess.PIPE,
        text=True
    ).stdout.splitlines()

    branches = [b.replace("* ", "").strip() for b in branches_raw]

    return jsonify({"branches": branches})

@app.route("/commits", methods=["POST"])
def commits():
    data = request.get_json()
    branch = data["branch"]

    # ブランチ切り替え
    subprocess.run(["git", "-C", "repo-dir", "checkout", branch])

    # コミット一覧取得
    result = subprocess.run(
        ["git", "-C", "repo-dir", "log", "--pretty=format:%H|%s|%cd", "--date=short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

    commits = []
    for line in result.stdout.splitlines():
        hash, msg, date = line.split("|", 2)
        commits.append({"hash": hash, "message": msg, "date": date})

    return jsonify({"commits": commits})

@app.route("/diff", methods=["POST"])
def diff():
    data = request.get_json()
    a = data["a"]
    b = data["b"]

    result = subprocess.run(
        ["git", "-C", "repo-dir", "diff", a, b],
        stdout=subprocess.PIPE,
        text=True
    )
    diff_text = result.stdout
    print(diff_text)
    print(result.stderr)

    return jsonify({"diff": diff_text})

