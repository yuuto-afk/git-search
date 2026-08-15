import subprocess
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # git diff を取得
    result = subprocess.run(
        ["rm -rf git-search || git clone https://github.com/yuuto-afk/git-search.git && cd git-search && git diff HEAD~1 HEAD"],  # 例: 1つ前のコミットとの差分
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    diff_text = result.stdout
    print(diff_text)
    print(result.stderr)

    return render_template("diff.html", diff=diff_text)

if __name__ == "__main__":
    app.run()
