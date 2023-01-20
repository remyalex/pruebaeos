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

@app.route("/files")
def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

@app.route("/files/<path:path>")
def get_file(path):
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

api = Api(app)
eosapi = API('remygalan', '3os4pi_choco')
ee = EarthExplorer('remygalan', '3os4pi_choco')

class Catalog(Resource):
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
        self.logs = []
        scenes = eosapi.search(
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

        gpOut = {
            "escenas_encontradas": str(len(scenes)),
            "escenas": scenes
        }
        return gpOut


class Download(Resource):
    downloadRequest = {
        "escena": fields.Str(required=True),
        "output_dir": fields.Str(required=True),
        "accion": fields.Str(required=True)
    }
    @use_kwargs(downloadRequest)
    def post(self, escena, output_dir, accion):
        if accion=="descarga":
            ee.download(escena, output_dir=output_dir)
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
        return gpOut
    '''
    def ZipShape(self, path):
        path, name = os.path.split(path)
        zip_path = os.path.join(path, name.split('.')[0] +'_'+datetime.now().strftime('%Y%m%d%H%M%S') + '.zip')
        zip = zipfile.ZipFile(zip_path, 'w')
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path,f)) and not f.endswith('.zip'):
                zip.write(os.path.join(path,f), f)
                os.remove(os.path.join(path,f))
        zip.close()
        return zip
    '''
api.add_resource(Catalog, '/catalog')
api.add_resource(Download, '/download')

# This error handler is necessary for usage with Flask-RESTful.
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(error_status_code, errors=err.messages)
    eosapi.logout()

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0')
