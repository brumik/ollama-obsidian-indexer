# This file will serve the api for the app
# - Serve query endpoint to ask questions
# - Serve endpoint for setting the folder
# - Serve the endpoint signalizing that indexing is in progress (maybe progress?)
# - Serve endpoint to reset the model


from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/indexing', methods = ['GET', 'POST', 'PATCH', 'DELETE'])
def indexing():
    if (request.method == 'GET'):
        return jsonify({
            'data': "Indexing is in progress"
        })

    if (request.method == 'POST'):
        new_file_path = request.json['file_path']
        # index the new file or the whole folder, depending if we got a filename or dir
        return jsonify({
            'data': file_path + ' created in the document store and index'
        })

    if (request.method == 'PATCH'):
        file_path = request.json['file_path']
        # reindex the file that was given
        return jsonify({
            'data': file_path + ' updated in the document store and index'
        })

    if (request.method == 'DELETE'):
        file_path = request.json['file_path']
        # delete the file from the index store
        return jsonify({
            'data': file_path + ' deleted from document store and index'
        })

@app.route('/', methods = ['POST'])
def index():
    if (request.method == 'POST'):
      query = request.json['query']
      # send it to the llm with context and return
      return jsonify({
          'data': 'Respones from LLM'
      })
        


if __name__ == '__main__': 
    app.run(debug = True)
