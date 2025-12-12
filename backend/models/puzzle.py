from datetime import datetime
from utils.db import db


class Puzzle(db.Model):
    __tablename__ = "puzzles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    standard_answer = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer)  # 可选：记录创建人
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_answer: bool = False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_answer:
            data["standard_answer"] = self.standard_answer
        return data
