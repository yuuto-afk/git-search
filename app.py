import subprocess
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # git diff を取得
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "HEAD"],  # 例: 1つ前のコミットとの差分
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    diff_text = result.stdout

    return render_template("diff.html", diff=diff_text)

if __name__ == "__main__":
    app.run()
