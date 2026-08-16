import os
import shutil
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("diff.html")

@app.route("/diff", methods=["POST"])
def diff():
    data = request.get_json()
    repo_url = data["url"]

    # git diff を取得
    if os.path.exists("repo-dir"):
        shutil.rmtree("repo-dir")

    result = subprocess.run(
        ["git clone https://github.com/yuuto-afk/git-search.git repo-dir && cd repo-dir && git diff HEAD~1 HEAD"],  # 例: 1つ前のコミットとの差分
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    diff_text = result.stdout
    print(diff_text)
    print(result.stderr)

    return jsonify({"diff": diff_text})

