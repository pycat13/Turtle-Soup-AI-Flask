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
    def create_puzzle(title: str, description: str, standard_answer: str, created_by: int = None) -> Puzzle:
        puzzle = Puzzle(
            title=title,
            description=description,
            standard_answer=standard_answer,
            created_by=created_by,
        )
        db.session.add(puzzle)
        db.session.commit()
        return puzzle

    @staticmethod
    def update_puzzle(puzzle_id: int, title: str, description: str, standard_answer: str) -> Tuple[Optional[Puzzle], Optional[str]]:
        puzzle = Puzzle.query.get(puzzle_id)
        if not puzzle:
            return None, "not_found"
        puzzle.title = title
        puzzle.description = description
        puzzle.standard_answer = standard_answer
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
