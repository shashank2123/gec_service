from flask import request, Blueprint, session
from gec.predict import Prediction

prediction = Prediction()


gec_app = Blueprint("gec_app", __name__)


@gec_app.route("/suggetions", methods=["POST"])
def get_suggetions():
    if request.method=="POST":
        data = request.json
        if "text" in data:
            suggetions = prediction.predict(data.get("text"))

            corrections = []

            for idx, correction in enumerate(suggetions):
                suggetion = {}
                suggetion["ids"] = idx+1
                suggetion["correction"]=correction
                corrections.append(suggetion)

            return {"suggetions":corrections}, 200
        else:
            return "Request Failure", 400


