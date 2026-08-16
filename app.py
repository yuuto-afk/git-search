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

    # ファイルごとにまとめる
    file_hits = {}

    for line in lines:
        try:
            path, line_no, content = line.split(":", 2)
            line_no = int(line_no)

            rel_path = os.path.relpath(path, "repo-dir")

            if rel_path not in file_hits:
                file_hits[rel_path] = []

            file_hits[rel_path].append({
                "line": line_no,
                "content": content,
                "abs_path": path
            })
        except Exception as e:
            print("PARSE ERROR:", e)
            continue

    results = []

    # ▼ ファイルごとに「まとまり（hunk）」を作る
    for rel_path, hits in file_hits.items():
        abs_path = hits[0]["abs_path"]
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                file_lines = f.readlines()
        except Exception as e:
            print("FILE OPEN ERROR:", abs_path, e)
            continue

        hunks = []
        current_hunk = None

        for hit in hits:
            line_no = hit["line"]

            # 前後3行
            start = max(0, line_no - 4)
            end = min(len(file_lines), line_no + 3)

            if current_hunk is None:
                current_hunk = {
                    "start": start,
                    "end": end,
                    "hits": [hit]
                }
            else:
                # ▼ 前後3行が重なるなら同じまとまりに統合
                if start <= current_hunk["end"]:
                    current_hunk["end"] = max(current_hunk["end"], end)
                    current_hunk["hits"].append(hit)
                else:
                    # ▼ 離れているので新しいまとまりを作る
                    hunks.append(current_hunk)
                    current_hunk = {
                        "start": start,
                        "end": end,
                        "hits": [hit]
                    }

        if current_hunk:
            hunks.append(current_hunk)

        # ▼ HTMLエスケープして返す
        safe_hunks = []
        for h in hunks:
            context = file_lines[h["start"]:h["end"]]
            safe_context = [html.escape(l.rstrip("\n")) for l in context]

            safe_hunks.append({
                "start": h["start"] + 1,
                "context": safe_context,
                "hits": [
                    {
                        "line": hit["line"],
                        "content": html.escape(hit["content"])
                    }
                    for hit in h["hits"]
                ]
            })

        results.append({
            "path": rel_path,
            "hunks": safe_hunks
        })

    print(results)
    return jsonify({"results": results})
