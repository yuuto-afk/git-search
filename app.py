from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>初めてのアプリ</title>
        <style>
            body {
                font-family: 'メイリオ', sans-serif;
                text-align: center;
                padding: 100px;
                background-color: #f0f8ff;
            }
            h1 {
                color: #4169e1;
            }
        </style>
    </head>
    <body>
        <h1>🎉 Hello, World!</h1>
        <p>初めてのアプリ公開成功！</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

