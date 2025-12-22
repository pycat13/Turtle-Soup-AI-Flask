from typing import List, Optional, Tuple
from models.puzzle import Puzzle
from utils.db import db


class PuzzleService:
    @staticmethod
    def list_puzzles() -> List[Puzzle]:
        return Puzzle.query.order_by(Puzzle.id.desc()).all()

    @staticmethod
    def get_puzzle(puzzle_id: int) -> Optional[Puzzle]:
        return Puzzle.query.get(puzzle_id)

    @staticmethod
    def create_puzzle(
        title_zh: str,
        description_zh: str,
        standard_answer_zh: str,
        title_en: str = None,
        description_en: str = None,
        standard_answer_en: str = None,
        created_by: int = None,
    ) -> Puzzle:
        puzzle = Puzzle(
            title_zh=title_zh,
            description_zh=description_zh,
            standard_answer_zh=standard_answer_zh,
            title_en=title_en,
            description_en=description_en,
            standard_answer_en=standard_answer_en,
            created_by=created_by,
        )
        db.session.add(puzzle)
        db.session.commit()
        return puzzle

    @staticmethod
    def update_puzzle(
        puzzle_id: int,
        title_zh: str,
        description_zh: str,
        standard_answer_zh: str,
        title_en: str = None,
        description_en: str = None,
        standard_answer_en: str = None,
    ) -> Tuple[Optional[Puzzle], Optional[str]]:
        puzzle = Puzzle.query.get(puzzle_id)
        if not puzzle:
            return None, "not_found"
        puzzle.title_zh = title_zh
        puzzle.description_zh = description_zh
        puzzle.standard_answer_zh = standard_answer_zh
        puzzle.title_en = title_en
        puzzle.description_en = description_en
        puzzle.standard_answer_en = standard_answer_en
        db.session.commit()
        return puzzle, None

    @staticmethod
    def delete_puzzle(puzzle_id: int) -> Optional[str]:
        puzzle = Puzzle.query.get(puzzle_id)
        if not puzzle:
            return "not_found"
        db.session.delete(puzzle)
        db.session.commit()
        return None
