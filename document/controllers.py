from flask import request, Blueprint, session
from document.models import Document
from auth.models import User
from datetime import datetime

document_app = Blueprint("document_app", __name__)



@document_app.route("/documents", methods=["GET"])
def getAllDocuments():
    if request.method=="GET":
        if session["loged_in"]:
            user_id = session["user_id"]
            cur_user = User.query.get(user_id)
            response = {
                "document":cur_user.get_documents()
            }

            return response, 200
        else:
            return "Login Required", 401

@document_app.route("/documents/new", methods=["POST"])
def newDocument():
    if request.method=="POST":
        if session["loged_in"]:
            data = request.json
            if "document_name" in data:
                user_id = session["user_id"]
                cur_user = User.query.get(user_id)
                document_name = data.get("document_name")
                new_doc = Document(document_name=document_name, content="", user=cur_user)
                new_doc.save()
                return "Successfully Created New Document", 200
            else:
                return "Request Failure", 400
        else:
            return "Login Required", 401

@document_app.route("/document/<doc_id>", methods=["GET"])
def getDocument(doc_id):
    if session["loged_in"]:
        if request.method=="GET":
            document = Document.query.get_or_404(doc_id)
            if document:
                return document.encode(), 200
            else:
                "Not Found", 403
    else:
        return "Login Required", 401


@document_app.route("/document/update/<doc_id>/name", methods=["POST"])
def rename_document(doc_id):
    if request.method=="POST":
        data = request.json
        if session["loged_in"]:
            if "name" in data:
                name = data.get("name")
                document = Document.query.get_or_404(doc_id)
                if document:
                    document.document_name = name
                    document.last_updated_date = datetime.utcnow()
                    document.update()
                    return "Updated Sucessfull", 200
                else:
                    "Not Found", 403
            else:
                return "Request Failure", 400
        else:
            return "Login Required", 401

@document_app.route("/document/update/<doc_id>/content", methods=["POST"])
def save_document(doc_id):
    if request.method=="POST":
        data = request.json
        if session["loged_in"]:
            if "content" in data:
                content = data.get("content")
                document = Document.query.get_or_404(doc_id)
                if document:
                    document.content = content
                    document.last_updated_date = datetime.utcnow()
                    document.update()
                    return "Saved Successfully", 200
                else:
                    "Not Found", 403
            else:
                return "Request Failure", 400
        else:
            return "Login Required", 401
    

@document_app.route("/document/delete/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
        if request.method=="DELETE":
            if session["loged_in"]:
                document = Document.query.get_or_404(doc_id)
                if document:
                    document.delete()
                    return "{} Deleted Successfully".format(document.document_name), 200
                else:
                    "Not Found", 403
        else:
            return "Login Required", 401

