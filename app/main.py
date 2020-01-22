import datetime
import connect_to_bq
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def root():

    if request.method == 'POST':
        distinctUsers = connect_to_bq.getDistinctUsers()
        data = request.form['listname']
        filterResult = connect_to_bq.filterByUser(data.lower())
        return render_template('index.html', data=filterResult.to_html(index=False), distuser=distinctUsers)

    else:
        distinctUsers = connect_to_bq.getDistinctUsers()
        return render_template('index.html', data="", distuser=distinctUsers) 


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)