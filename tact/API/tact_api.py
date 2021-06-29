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


api.add_resource(Config, '/config/<string:config_type>')  # add endpoints

if __name__ == '__main__':
    app.run()  # run our Flask app
