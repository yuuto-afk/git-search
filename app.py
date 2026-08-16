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

    # git diff を取得
    if os.path.exists("repo-dir"):
        shutil.rmtree("repo-dir")

    result = subprocess.run(
        ["GIT_LFS_SKIP_SMUDGE=1 git clone {repo_url} repo-dir".format(repo_url=repo_url)],  # 例: 1つ前のコミットとの差分
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    commits = []
    for line in result.stdout.splitlines():
        hash, msg = line.split("|", 1)
        commits.append({"hash": hash, "message": msg})

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

