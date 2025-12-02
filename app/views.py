from flask import jsonify
from app import app
from app import hw_views



@app.route('/')
def home():
    return "Frame says 'Hello world!'"

@app.route('/lab02')
def resume():
    return app.send_static_file('lab02_resume.html')


@app.route('/phonebook')
def index():
    return app.send_static_file('phonebook.html')

# This route serves the dictionary d at the route /data
@app.route("/api/data")
def data():
    # define some data
    d = {
        "Alice": "(708) 727-2377",
        "Frame": "09-7198-9198"
    }
    return jsonify(d)  # convert your data to JSON and return
