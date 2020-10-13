# based on: https://medium.com/python-pandemonium/build-simple-restful-api-with-python-and-flask-part-2-724ebf04d12

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Latency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latencyMap = db.Column(db.String(80), unique=True)

    def __init__(self, latencyMap):
        self.latencyMap = latencyMap



class LatencyMapSchema(ma.Schema):
    class Meta:
        # Fields to expose
        field = ('latencyMap')


latency_schema = LatencyMapSchema()
latencies_schema = LatencyMapSchema(many=True)


# endpoint to create new user
#@app.route("/user", methods=["POST"])
#def add_user():
#    username = request.json['username']
#    email = request.json['email']#

#    new_user = User(username, email)

#    db.session.add(new_user)
#    db.session.commit()

#    return jsonify(new_user)


# endpoint to show all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = Latency.query.all()
    result = latencies_schema.dump(all_users)
    return jsonify(result.data)

'''
# endpoint to get user detail by id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = Latency.query.get(id)
    return latency_schema.jsonify(user)
'''
'''
# endpoint to update user
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = Latency.query.get(id)
    username = request.json['username']
    email = request.json['email']

    user.email = email
    user.username = username

    db.session.commit()
    return latency_schema.jsonify(user)


# endpoint to delete user
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)
'''

if __name__ == '__main__':
    app.run(debug=True)