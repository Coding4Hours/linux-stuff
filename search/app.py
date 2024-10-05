from flask import Flask, request, render_template
from search_engine import search

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search_query():
    query = request.args.get("query", "")
    if query:
        results = search(query)
        return render_template("results.html", query=query, results=results)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=False)
