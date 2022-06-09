from flask import request, Blueprint, session
from auth.models import User

auth_app = Blueprint("auth_app", __name__)

@auth_app.route("/register", methods=["POST"])
def register():
    if request.method=="POST":
        data = request.json
        if "username" in data and "email" in data and "password" in data:
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            existUser = User.query.filter_by(email=email).first()

            if not existUser:
                user = User()
                user.username = username
                user.email = email
                user.password = password
                user.save()
                return "Registration Sucessful", 200
            else:
                return "User already exists", 409
        else:
            return "Request Failure", 400

@auth_app.route("/login", methods=['POST'])
def login():
    if request.method=="POST":
        data = request.json
        if "email" in data and "password" in data:
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            existUser = User.query.filter_by(email=email).first()

            if existUser and existUser.password==password:
                session["loged_in"]=True
                session["user_id"]=existUser.id
                return "Login Sucessful", 200
            else:
                return "Invalid uasername or password", 403
        else:
            return "Request Failure", 400

@auth_app.route("/getUserId", methods=['GET'])
def getCurrentUser():

    if session["loged_in"]:
        return {"user_id":session["user_id"]}, 200

    return "No Found", 403

@auth_app.route("/logout", methods=['POST'])
def logout():
    session['loged_in']=False
    session['user_id']=None
    return "Successfully Logged Out", 200