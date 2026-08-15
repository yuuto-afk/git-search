from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    old = 'console.log("Hello");'
    new = 'console.log("Hello World");'
    return render_template("diff.html", old=old, new=new)

if __name__ == "__main__":
    app.run()
