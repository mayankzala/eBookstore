from flask import Flask, render_template, request, send_file,Response
from pymongo import MongoClient
import gridfs
import io
import base64
import json
client = MongoClient('mongodb://localhost:27017/')
db = client['practice']
temp = db['temp']
fs = gridfs.GridFS(db)

prac = Flask(__name__)
prac.config['SECRET_KEY'] = 'some random'


@prac.route("/", methods=['GET', 'POST'])
def home():
    if request.method=='POST':
        print("helo2")
        print(request.form.get('s_name'))
        print(request.form.get('name'))
        # data=request.get_json()
        # print(data['category'])
        return 'nice'
    return render_template('temp_forn.html')
# @prac.route('/submit',methods=['POST'])
# def sumit():
#     print("helo")
#     data=request.form
#     print(data['category'])
#     return data
if __name__ == "__main__":
    prac.run(debug=True)

# for download_code