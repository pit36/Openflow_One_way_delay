# based on: https://medium.com/python-pandemonium/build-simple-restful-api-with-python-and-flask-part-2-724ebf04d12
'''
from restDB import db
db.create_all()

'''


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

desiredLenght = 10

class Data(db.Model):
    IDRec = db.Column(db.Integer, primary_key=True)
    IDSender = db.Column(db.Integer, primary_key=True)
    latencyMap = db.Column(db.String(80))
    bandwithMap = db.Column(db.String(80))

    def __init__(self, id , IdTwo, latencyMap,bandwithMap):
        self.IDRec = id
        self.IDSender = IdTwo
        self.latencyMap = latencyMap
        self.bandwithMap = bandwithMap

class MapSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('IDRec','IDSender','latencyMap','bandwithMap')

def fillUpMapFloat(mapToFillUp, desiredLenght):
    filledUpMap = []
    difference = desiredLenght - len(mapToFillUp)
    for i in range(difference):
        filledUpMap.append(0)
    for x in mapToFillUp:
        filledUpMap.append(x['value'])
    return filledUpMap


def modify_db(dataMap):
    #parse all ids...
    Data.query.delete()
    #db.session.clear()
    for key1 in dataMap.keys():
        for key2 in dataMap[key1].keys():

            latencyMap = []
            bandwithMap = []

            #get latencymap
            #if map does not have enough values
            if(len(dataMap[key1][key2]['latencyEcho']) < desiredLenght):
                latencyMap = fillUpMapFloat(dataMap[key1][key2]['latencyEcho'], desiredLenght)
            else:
                preLatencyMap = dataMap[key1][key2]['latencyEcho'][-10:]
                for x in preLatencyMap:
                    latencyMap.append(x['value'])

            # get bandwithmap
            if(len(dataMap[key1][key2]['bw']) < desiredLenght):
                bandwithMap = fillUpMapFloat(dataMap[key1][key2]['bw'], desiredLenght)
            else:
                preBandwithMap = dataMap[key1][key2]['bw'][-10:]
                for x in preBandwithMap:
                    bandwithMap.append(x['value'])


            valuesStrLatency = ';'.join(str(e) for e in latencyMap)
            valuesStrBw = ';'.join(str(e) for e in bandwithMap)
            new_data = Data(key1, key2, valuesStrLatency, valuesStrBw)
            db.session.add(new_data)
    #TODO: DEBUG
    #print("BWMAP: {}, LATENCYMAP: {}".format(bandwithMap, latencyMap))
    db.session.commit()


map_schema = MapSchema()
maps_schema = MapSchema(many=True)

@app.route("/user", methods=["GET"])
def get_data():
    all_data = Data.query.all()
    result = maps_schema.dump(all_data)
    response = jsonify(result.data)
    response.headers.add('Access-Control-Allow-Origin','*')
    return response


if __name__ == '__main__':
    app.run(debug=True)