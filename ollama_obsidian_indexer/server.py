from flask import Flask, request
from .llm import index_dir, index_file, query, delete_index
import os

app = Flask(__name__)

base_path = os.getenv("NOTES_BASE_PATH", "")


@app.route("/indexing", methods=["GET", "POST", "PATCH", "DELETE"])
def indexing():
    if request.method == "GET":
        return "Indexing is in progress"

    if request.method == "POST":
        path = request.get_json()["path"]

        indexed_count = index_dir(os.path.join(base_path, path))

        return str(indexed_count) + " new files were (re)indexed."

    if request.method == "PATCH":
        path = request.get_json()["path"]

        if os.path.isdir(os.path.join(base_path, path)):
            indexed_count = index_dir(os.path.join(base_path, path))
        else:
            indexed_count = index_file(os.path.join(base_path, path))

        if indexed_count == 0:
            return "No update was needed for " + path + "."
        elif indexed_count == -1:
            return "No file found at " + path + "."

        return path + " got updated index."

    if request.method == "DELETE":
        file_path = request.get_json()["path"]

        delete_index(os.path.join(base_path, file_path))

        return file_path + " deleted from document store and index"


@app.route("/", methods=["POST"])
def index():
    if request.method == "POST":
        user_query = request.get_json()["query"]

        response = query(user_query)

        return response
