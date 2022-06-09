from flask import Flask
from config import db
from gec.gec_model import TagEncoder

app = Flask(__name__)
app.secret_key = "_gec_private_key_"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resource/gec_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)

from auth.controllers import auth_app
app.register_blueprint(auth_app)

from document.controllers import document_app
app.register_blueprint(document_app)

from gec.controllers import gec_app
app.register_blueprint(gec_app)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run()