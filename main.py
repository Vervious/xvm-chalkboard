from flask import Flask
import storage

app = Flask(__name__)

@app.route("/")
def hello():
    storage.write_ip_and_chalkboardid('0.0.0.0', 1)
    return "Hello World! Test Deploy! Test Deploy 2! Test Deploy 3! Test Deploy 3.5!"

@app.route("/results")
def results():
    return str(storage.read_total_counts_for_chalkboardid(1))

if __name__ == "__main__":
    # for debugging only
    app.debug = True
    app.run(host='0.0.0.0')
