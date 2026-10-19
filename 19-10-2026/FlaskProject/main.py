from flask import Flask
app=Flask(__name__)
@app.route("/")
def home():
    return "Hello from flask"

@app.route("/about")
def about():
    return "This is a simple flask application"

@app.route("/hello/<name>")
def hello(name):
    return f"Hello {name}"

if __name__=='__main__':
    app.run(debug=True)