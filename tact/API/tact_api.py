from flask import Flask
from flask_restful import Resource, Api, reqparse
import tact.control.controller as controller

app = Flask(__name__)
api = Api(app)


class Config(Resource):
    def get(self, config_type):
        # go out to controller
        result = controller.get_settings_json(config_type)

        if result:
            return result, 200  # return data and 200 OK
        else:
            return {"message": config_type + " not found."}, 404

    def patch(self, config_type):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('outgoing_config_json', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary

        if controller.update_settings(config_type, args.outgoing_config_json):
            return {"message": "Settings updated."}, 200
        else:
            return {"message": "Settings update failed."}, 404


class Analysis(Resource):
    def get(self):
        if controller.analyze():
            return {"message": "Analysis complete."}, 200
        else:
            return {"message": "Analysis failed."}, 404


class Preview(Resource):
    def get(self):
        result = controller.generate_preview()
        if result:
            return {"message": "Preview generated.", "data": result}, 200
        else:
            return {"message": "Preview generation failed."}, 404


class Process(Resource):
    def get(self):
        if controller.process():
            return {"message": "File processing complete."}, 200
        else:
            return {"message": "File processing failed."}, 404


api.add_resource(Config, '/config/<string:config_type>')  # add endpoints
api.add_resource(Analysis, '/analysis')
api.add_resource(Preview, '/preview')
api.add_resource(Process, '/process')

if __name__ == '__main__':
    app.run()  # run our Flask app
