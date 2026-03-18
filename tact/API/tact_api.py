from flask import Flask, request, make_response
from os import path, makedirs
from shutil import rmtree
from werkzeug.utils import secure_filename
import tact.control.controller as controller

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
# 16mb max upload size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


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


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return make_response(({"message": "No file part"}, 400))
    
    files = request.files.getlist("file")
    
    if not files:
        return make_response(({"message": "No selected file(s)"}, 400))
        
    # Create a unique directory for current session
    # For future multi-user support, replace with the actual session UUID
    session_id = "default_user"
    upload_batch_dir = path.join("/tmp/uploads", session_id)
    
    # Wipe the user's directory to prevent endless file accumulation
    if path.exists(upload_batch_dir):
        rmtree(upload_batch_dir)
        
    makedirs(upload_batch_dir, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file and file.filename:
            # Secure filename to prevent directory traversal attacks
            basename = secure_filename(path.basename(file.filename))
            file_path = path.join(upload_batch_dir, basename)
            if not path.exists(file_path):
                file.save(file_path)
                saved_files.append(file_path)
                
    if not saved_files:
        return make_response(({"message": "No valid files received"}, 400))
        
    is_directory = len(saved_files) > 1
    input_path = upload_batch_dir if is_directory else saved_files[0]
    path_for_preview = saved_files[0]
    
    if controller.update_settings("parser", {
        "inputPath": input_path, 
        "pathForPreview": path_for_preview, 
        "isDirectory": is_directory
    }):
        return make_response(({"message": "File(s) uploaded and config updated"}, 200))
    else:
        return make_response(({"message": "File(s) uploaded but config update failed"}, 500))


@app.route("/analysis")
def analysis():
    if controller.analyze():
        return make_response(("Analysis complete.", 200))
    else:
        return make_response(("Analysis failed.", 404))


@app.route("/preview")
def preview():
    preview_type = request.args.get("preview_type")

    if preview_type and preview_type == "taxonomic_names":
        result = controller.generate_taxonomic_preview()
        if result:
            return make_response(
                ({"message": "Taxonomic name preview generated.", "data": result}, 200)
            )
        else:
            return make_response(("Taxonomic name preview generation failed.", 404))
    else:
        result = controller.generate_preview()
        if result:
            return make_response(
                ({"message": "Preview generated.", "data": result}, 200)
            )
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
    operation = request.args.get("operation")

    if operation == "enumerate_columns":
        if controller.flip_dataset():
            return make_response(("Dataset flipped successfully.", 200))
        else:
            return make_response(("Failed to flip dataset.", 404))
    elif operation == "pivot_columns":
        if controller.pivot_dataset():
            return make_response(("Dataset pivoted successfully.", 200))
        else:
            return make_response(("Failed to pivot dataset.", 404))
    elif operation == "combine_rows":
        if controller.combine_rows():
            return make_response(("Rows combined successfully.", 200))
        else:
            return make_response(("Failed to combine rows.", 404))
    elif operation == "merge_taxa":
        if controller.validate_taxonomic_names():
            return make_response(("Taxonomic names merged.", 200))
        else:
            return make_response(("Failed to merge taxonomic names.", 404))
    else:
        return make_response(
            (
                {
                    "message": "Invalid operation, please select enumerate_columns, combine_rows, or merge_taxa."
                },
                400,
            )
        )


import os

# launch API
if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
