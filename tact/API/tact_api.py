from flask import Flask, request, make_response
import tact.control.controller as controller

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route("/config/<string:config_type>", methods=["GET", "PATCH"])
def config(config_type):
    if request.method == "GET":
        field = request.args.get("field")
        if field:
            result = controller.get_settings_json(config_type)
            if field in result:
                return make_response((result[field], 200))
            else:
                return make_response(
                    ({"message": f"{field} not found in {config_type}."}, 404)
                )
        else:
            result = controller.get_settings_json(config_type)
            if result:
                return make_response((result, 200))
            else:
                return make_response(({"message": f"{config_type} not found."}, 404))

    elif request.method == "PATCH":
        incoming_changes = request.get_json()

        if incoming_changes:
            if controller.update_settings(config_type, incoming_changes):
                return make_response(("Settings updated.", 200))
            else:
                return make_response(("Settings update failed.", 404))
        else:
            return make_response(
                (
                    {
                        "message": "No incoming changes, please specify config values to be updated."
                    },
                    400,
                )
            )


@app.route("/analysis")
def analysis():
    if controller.analyze():
        return make_response(("Analysis complete.", 200))
    else:
        return make_response(("Analysis failed.", 404))


@app.route("/preview")
def preview():
    result = controller.generate_preview()
    if result:
        return make_response(({"message": "Preview generated.", "data": result}, 200))
    else:
        return make_response(("Preview generation failed.", 404))


@app.route("/process")
def process():
    if controller.process():
        return make_response(("File processing complete.", 200))
    else:
        return make_response(("File processing failed.", 404))


@app.route("/data")
def data():
    result = controller.get_data(kwargs=request.args.to_dict())
    if result:
        return {"message": "Returning dataset.", "data": result}, 200

    else:
        return make_response(("Failed to retrieve dataset.", 404))


@app.route("/transform", methods=["POST"])
def transform():
    operation = request.json.get("operation")

    if operation == "enumerate_columns":
        if controller.flip_dataset():
            return make_response(("Dataset flipped successfully", 200))
        else:
            return make_response(("Failed to flip dataset.", 404))
    elif operation == "combine_rows":
        if controller.combine_rows():
            return make_response(("Rows combined successfully", 200))
        else:
            return make_response(("Failed to combine rows.", 404))
    else:
        return make_response(
            (
                {
                    "message": "Invalid operation, please select enumerate_columns, or combine_rows."
                },
                400,
            )
        )


# launch API
if __name__ == "__main__":
    app.run()
