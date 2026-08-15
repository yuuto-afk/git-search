from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>vue_pager</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/diff2html/2.3.3/diff2html.min.css">
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/3.4.0/diff.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/diff2html/2.3.3/diff2html.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/diff2html/2.3.3/diff2html-ui.min.js"></script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const unifiedDiff = JsDiff.createPatch("fileName", "a\nb\nc\d\ne\n\nf", "a\nb\nac\d\ne\n\n\nf", "test", "test");
        const diff2htmlUi = new Diff2HtmlUI({diff: unifiedDiff});
        diff2htmlUi.draw('#app', {inputFormat: 'json', showFiles: true, matching: 'lines'});
    });
    </script>
    </head>
    <body>
    <div id="app">
    </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

