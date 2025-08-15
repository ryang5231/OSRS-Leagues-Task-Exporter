from flask import Flask, request, send_file, jsonify
import io
import pandas as pd
import shattered_relics

app = Flask(__name__)

@app.route("/run-option", methods=["POST"])
def run_option():
    data = request.get_json(silent=True) or {}
    option = data.get("league-option")

    # Map options to functions in worker.py
    options_map = {
        "3-shattered_relics": shattered_relics.get_task_excel,
        # "4-trailblazer_reloaded": trailblazer_reloaded.get_task_excel,
        # "5-raging_echoes": raging_echoes.get_task_excel,
    }

    if option not in options_map:
        return jsonify({"error": "Invalid League selected"}), 400

    excel_file = options_map[option]()

if __name__ == "__main__":
    app.run(debug=True)
