from flask import Flask, request
from flask_restful import Resource, Api
import tact.control.controller as controller

app = Flask(__name__)
api = Api(app)


class Config(Resource):
    def get(self, config_type):
        field = request.args.get("field")

        if field:
            result = controller.get_settings_json(config_type)
            if field in result:
                return result[field], 200
            else:
                return {"message": f"{field} not found in {config_type}."}, 404
        else:
            result = controller.get_settings_json(config_type)
            if result:
                return result, 200  # return data and 200 OK
            else:
                return {"message": f"{config_type} not found."}, 404

    def patch(self, config_type):
        incoming_changes = request.get_json()

        if incoming_changes:
            if controller.update_settings(config_type, incoming_changes):
                return {"message": "Settings updated."}, 200
            else:
                return {"message": "Settings update failed."}, 404
        else:
            return {
                "message": "No incoming changes, please specify config values to be updated."
            }, 400


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


class Data(Resource):
    def get(self):
        result = controller.get_data(kwargs=request.args.to_dict())
        if result:
            return {
                "message": "Returning dataset as dict.",
                "data": result,
            }, 200
        else:
            return {"message": "Failed to retrieve dataset."}, 404


# add endpoints
api.add_resource(Config, "/config/<string:config_type>")
api.add_resource(Analysis, "/analysis")
api.add_resource(Preview, "/preview")
api.add_resource(Process, "/process")
api.add_resource(Data, "/data")

# launch API
if __name__ == "__main__":
    app.run()
