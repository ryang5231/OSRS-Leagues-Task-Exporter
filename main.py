from flask import Flask, request, send_file, jsonify
import io
import pandas as pd
import shattered_relics
import trailblazer_reloaded
# import raging_echoes

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def run_option():
    data = request.get_json(silent=True) or {}
    option = data.get("league-option")

    # Map options to functions in worker.py
    options_map = {
        "3-shattered_relics": {
                                "caller_function": shattered_relics.get_task_excel,
                                "file_name": "OSRS_3_Shattered_League_Tasks"
                            },
        "4-trailblazer_reloaded": {
                                "caller_function": trailblazer_reloaded.get_task_excel,
                                "file_name": "OSRS_4_Trailblazer_Reloaded_Tasks"
                            },
        # "5-raging_echoes": {
        #                         "caller_function": raging_echoes.get_task_excel,
        #                         "file_name": "OSRS_5_Raging_Echoes_Tasks"
        #                     },
    }

    if option not in options_map:
        return jsonify({"error": "Invalid League selected"}), 400
    else:
        print("invoking...")
        excel_bytes = options_map[option]['caller_function']()
        excel_file = io.BytesIO(excel_bytes)

    return send_file(
        excel_file,
        as_attachment=True,
        download_name=f"{options_map[option]['file_name']}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(debug=True)
