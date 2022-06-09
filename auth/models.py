from config import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    documents = db.relationship('Document', backref='user')

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def get_documents(self):
        return [ doc.encode() for doc in self.documents]

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email})"