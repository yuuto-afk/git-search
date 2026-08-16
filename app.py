import os
import shutil
import subprocess
from flask import Flask, render_template, request, jsonify
import html

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
        ["git", "-C", "repo-dir", "branch", "-a"],
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

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    keyword = data["keyword"]

    # grep -R で全文検索
    result = subprocess.run(
        ["grep", "-R", "-n", "--exclude-dir=.git", keyword, "repo-dir"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

    lines = result.stdout.splitlines()

    results = []
    for line in lines:
        try:
            path, line_no, content = line.split(":", 2)
            line_no = int(line_no)

            # ファイルを読み込んで前後3行を取得
            full_path = os.path.join("repo-dir", path.replace("repo-dir" + "/", ""))

            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                file_lines = f.readlines()

            start = max(0, line_no - 4)
            end = min(len(file_lines), line_no + 3)

            context = file_lines[start:end]

            # HTMLを無害化
            safe_context = [html.escape(l.rstrip("\n")) for l in context]
            safe_content = html.escape(content)

            results.append({
                "path": path.replace("repo-dir" + "/", ""),
                "line": line_no,
                "match": safe_content,
                "context": safe_context,
                "context_start": start + 1
            })

        except Exception as e:
            continue

    return jsonify({"results": results})
