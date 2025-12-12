from typing import List, Dict
from sqlalchemy import desc
from models.score import Score
from models.user import User
from models.puzzle import Puzzle
from utils.db import db


class ScoreService:

    @staticmethod
    def calculate_score(session, puzzle):
        """
        返回整数分数，依据模式使用不同规则
        """

        mode = session.mode

        # ====== 1. 自由模式：提问越少分越高 ======
        if mode == "free":
            base = 100
            used = session.question_count
            score = max(10, base - used * 5)   # 每多问一个扣5分

        # ====== 2. 限时模式：剩余时间越多分越高 ======
        elif mode == "timed":
            total_time = 300   # 5分钟
            used_time = (session.end_time - session.start_time).total_seconds()
            remaining = max(0, total_time - used_time)
            score = int(50 + remaining / 6)   # 最高100分

        # ====== 3. 限题模式：剩余提问数越多分越高 ======
        elif mode == "limited_questions":
            total_q = 20
            used = session.question_count
            remaining = max(0, total_q - used)
            score = 40 + remaining * 3

        else:
            score = 0

        return max(0, min(100, score))  # 限制在 0–100 区间

    @staticmethod
    def submit_score(user_id: int, puzzle_id: int, score_value: int) -> Score:
        score = Score(user_id=user_id, puzzle_id=puzzle_id, score=score_value)
        db.session.add(score)
        db.session.commit()
        return score

    @staticmethod
    def get_leaderboard(limit: int = 20) -> List[Dict]:
        """
        返回最新的高分榜，按得分降序、时间降序。
        """
        rows = (
            db.session.query(Score, User.username, Puzzle.title)
            .join(User, User.id == Score.user_id)
            .join(Puzzle, Puzzle.id == Score.puzzle_id)
            .order_by(desc(Score.score), desc(Score.created_at))
            .limit(limit)
            .all()
        )

        leaderboard = []
        for score, username, puzzle_title in rows:
            leaderboard.append(
                {
                    "id": score.id,
                    "username": username,
                    "puzzle_title": puzzle_title,
                    "puzzle_id": score.puzzle_id,
                    "score": score.score,
                    "created_at": score.created_at.isoformat() if score.created_at else None,
                }
            )
        return leaderboard
