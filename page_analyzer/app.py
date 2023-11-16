from flask import Flask,render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/two')
def two():
    return render_template('two.html')


if __name__ == "__main__":
    app.run(debug=True)
