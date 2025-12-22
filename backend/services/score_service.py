from typing import List, Dict
from sqlalchemy import desc
from models.score import Score
from models.user import User
from utils.db import db


class ScoreService:

    @staticmethod
    def calculate_score(session, puzzle):
        """
        返回整数分数：
        - success：原规则（0–100）
        - fail（放弃/失败）：倒扣，每交互一次 -10 分（至少 -10）
        """

        # 失败：倒扣（每次交互 -10）
        if getattr(session, "status", None) == "fail":
            used = int(getattr(session, "question_count", 0) or 0)
            return -10 * max(1, used)

        mode = session.mode

        if mode == "free":
            base = 100
            used = session.question_count
            score = max(10, base - used * 5)

        elif mode == "timed":
            total_time = 300
            used_time = (session.end_time - session.start_time).total_seconds()
            remaining = max(0, total_time - used_time)
            score = int(50 + remaining / 6)

        elif mode == "limited_questions":
            total_q = 20
            used = session.question_count
            remaining = max(0, total_q - used)
            score = 40 + remaining * 3

        else:
            score = 0

        return max(0, min(100, score))

    @staticmethod
    def submit_score(user_id: int, puzzle_id: int, score_value: int) -> Score:
        score = Score(user_id=user_id, puzzle_id=puzzle_id, score=score_value)
        db.session.add(score)
        db.session.commit()
        return score

    @staticmethod
    def get_leaderboard(limit: int = 20, lang: str = "zh") -> List[Dict]:
        """
        用户维度排行榜（总分）。

        计分规则（按每道题目独立结算，然后汇总到用户总分）：
        1) 放弃（负分）会累加，直到第一次成功为止
        2) 成功只记录第一次通过得分；同题目后续成绩不再影响排行榜

        说明：为兼容历史数据（可能存在重复成功/成功后继续产生负分），此处按时间顺序
        在内存中做“遇到第一次成功后忽略后续”的裁剪计算。
        """
        rows = (
            db.session.query(
                User.id.label("user_id"),
                User.username.label("username"),
                Score.puzzle_id.label("puzzle_id"),
                Score.score.label("score"),
                Score.created_at.label("created_at"),
                Score.id.label("score_id"),
            )
            .outerjoin(Score, Score.user_id == User.id)
            .order_by(User.id.asc(), Score.puzzle_id.asc(), Score.created_at.asc(), Score.id.asc())
            .all()
        )

        user_totals: Dict[int, Dict] = {}
        user_solved_puzzles: Dict[int, set] = {}

        for r in rows:
            user_id = int(r.user_id)
            if user_id not in user_totals:
                user_totals[user_id] = {"user_id": user_id, "username": r.username, "total_score": 0}
                user_solved_puzzles[user_id] = set()

            if r.puzzle_id is None:
                continue

            puzzle_id = int(r.puzzle_id)
            if puzzle_id in user_solved_puzzles[user_id]:
                continue

            score_value = int(r.score or 0)
            user_totals[user_id]["total_score"] += score_value

            if score_value >= 0:
                user_solved_puzzles[user_id].add(puzzle_id)

        leaderboard = list(user_totals.values())
        leaderboard.sort(key=lambda x: (x["total_score"], x["user_id"]), reverse=True)
        return leaderboard[: int(limit)]
