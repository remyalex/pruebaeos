import os
import json
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from datetime import datetime
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser

app = Flask(__name__)

UPLOAD_DIRECTORY = "./geoprocess_files"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Api(app)

class Catalog(Resource):
    init_every_request = True
    def __init__(self):
        self.eosapi = API('remygalan', '3os4pi_choco')
        self.logs = []

    catalogRequest = {
        "dataset": fields.Str(required=True),
        "lat": fields.Float(required=True),
        "lon": fields.Float(required=True),
        "fecha_inicio": fields.Str(required=True),
        "fecha_fin": fields.Str(required=False),
        "nubosidad_max": fields.Str(required=False)
    }

    @use_kwargs(catalogRequest)
    def post(self, dataset, lat, lon, fecha_inicio, fecha_fin, nubosidad_max):
        scenes = self.eosapi.search(
            dataset=dataset,
            latitude=lat,
            longitude=lon,
            start_date=fecha_inicio,
            end_date=fecha_fin,
            max_cloud_cover=nubosidad_max
        )

        gpLog = str(datetime.now()) + ' - (GeoProccess) '+ dataset +' feats: ' + str(len(scenes))
        print (gpLog)
        self.logs.append(gpLog)
        self.eosapi.logout()
        gpOut = {
            "escenas_encontradas": str(len(scenes)),
            "escenas": scenes
        }
        return gpOut


class Download(Resource):
    init_every_request = True
    def __init__(self):
        self.ee = EarthExplorer('remygalan', '3os4pi_choco')

    downloadRequest = {
        "escena": fields.Str(required=True),
        "output_dir": fields.Str(required=True),
        "accion": fields.Str(required=True)
    }

    @use_kwargs(downloadRequest)
    def post(self, escena, output_dir, accion):
        if accion=="descarga":
            self.ee.download(escena, output_dir=output_dir)
            print (str(datetime.now()) + ' - (GET) feats: ' + str(escena))
            gpOut = {
                "escena": str(escena),
                "url": str(escena)
            }
        elif accion=="listar":
            files = []
            for filename in os.listdir(output_dir):
                path = os.path.join(output_dir, escena)
                if os.path.isfile(path):
                    files.append(filename)
            gpOut = jsonify(files)
        self.ee.logout()
        return gpOut

api.add_resource(Catalog, '/catalog')
api.add_resource(Download, '/download')

# This error handler is necessary for usage with Flask-RESTful.
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(error_status_code, errors=err.messages)

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0')
