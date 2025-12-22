from datetime import datetime
from utils.db import db


class Puzzle(db.Model):
    __tablename__ = "puzzles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 方案A：中文字段复用现有列名，避免破坏已有数据库
    title_zh = db.Column("title", db.String(200), nullable=False)
    description_zh = db.Column("description", db.Text, nullable=False)
    standard_answer_zh = db.Column("standard_answer", db.Text, nullable=False)

    # 英文字段新增列（可为空，缺失时 fallback 到中文）
    title_en = db.Column(db.String(200))
    description_en = db.Column(db.Text)
    standard_answer_en = db.Column(db.Text)

    created_by = db.Column(db.Integer)  # 可选：记录创建人
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def _pick_lang(self, lang: str):
        return (lang or "zh").lower()

    def get_title(self, lang: str = "zh"):
        lang = self._pick_lang(lang)
        if lang.startswith("en") and self.title_en:
            return self.title_en
        return self.title_zh

    def get_description(self, lang: str = "zh"):
        lang = self._pick_lang(lang)
        if lang.startswith("en") and self.description_en:
            return self.description_en
        return self.description_zh

    def get_standard_answer(self, lang: str = "zh"):
        lang = self._pick_lang(lang)
        if lang.startswith("en") and self.standard_answer_en:
            return self.standard_answer_en
        return self.standard_answer_zh

    def to_public_dict(self, lang: str = "zh"):
        return {
            "id": self.id,
            "title": self.get_title(lang),
            "description": self.get_description(lang),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_admin_dict(self):
        return {
            "id": self.id,
            "title_zh": self.title_zh,
            "description_zh": self.description_zh,
            "standard_answer_zh": self.standard_answer_zh,
            "title_en": self.title_en,
            "description_en": self.description_en,
            "standard_answer_en": self.standard_answer_en,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
