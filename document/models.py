from config import db
from datetime import datetime

class Document(db.Model):
    __tabel__ = "document"
    document_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_date = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def encode(self):
        return {
            "document_id":self.document_id,
            "document_name": self.document_name,
            "content":self.content,
            "created_date": self.created_date,
            "last_updated_date": self.last_updated_date
        }

    def __repr__(self):
        return f"Document('{self.document_id}', '{self.document_name}')"
