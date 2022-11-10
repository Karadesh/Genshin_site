from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "index"

@app.route("/authorisation")
def authorisation():
    return "authorisation"

@app.route("/posts")
def posts():
    return "posts"

@app.route("/register")
def authorisation():
    return "register"

@app.route("/profile")
def authorisation():
    return "profile"

if __name__ == "__main__":
    app.run(debug=True)
