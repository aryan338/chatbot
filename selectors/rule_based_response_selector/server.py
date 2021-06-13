#!/usr/bin/env python

import logging
import numpy as np
import time

from flask import Flask, request, jsonify
from os import getenv
import sentry_sdk


sentry_sdk.init(getenv("SENTRY_DSN"))

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/respond", methods=["POST"])
def respond():
    st_time = time.time()

    dialogs = request.json["dialogs"]
    response_candidates = [dialog["utterances"][-1]["hypotheses"] for dialog in dialogs]

    selected_skill_names = []
    selected_responses = []
    selected_confidences = []

    for i, dialog in enumerate(dialogs):
        confidences = []
        responses = []
        skill_names = []

        for skill_data in response_candidates[i]:
            if skill_data["text"] and skill_data["confidence"]:
                logger.info(f"Skill {skill_data['skill_name']} returned non-empty hypothesis with non-zero confidence.")

            confidences += [skill_data["confidence"]]
            responses += [skill_data["text"]]
            skill_names += [skill_data["skill_name"]]

        best_id = np.argmax(confidences)

        selected_skill_names.append(skill_names[best_id])
        selected_responses.append(responses[best_id])
        selected_confidences.append(confidences[best_id])

    total_time = time.time() - st_time
    logger.info(f"rule_based_response_selector exec time = {total_time:.3f}s")
    return jsonify(list(zip(selected_skill_names, selected_responses, selected_confidences)))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=3000)
