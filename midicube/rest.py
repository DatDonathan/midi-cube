import flask, threading

app = flask.Flask(__name__)

def start_server():
    threading.Thread(target=app.run).start()

@app.route('/www/<path:path>')
def static_sites(path):
    return flask.send_from_directory('../qwww', path)
