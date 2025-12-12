from flask import Blueprint, jsonify, request, g
from services.score_service import ScoreService
from utils.auth import login_required


scores_bp = Blueprint('scores', __name__)


@scores_bp.route('', methods=['GET'])
def get_scores():
    """
    获取排行榜
    """
    limit = request.args.get("limit", default=20, type=int)
    data = ScoreService.get_leaderboard(limit=limit)
    return jsonify({"data": data}), 200


@scores_bp.route('/submit', methods=['POST'])
@login_required
def submit_score():
    """
    手动提交一条得分（主要用于调试/补录），正常情况下 finish_game 会自动写入。
    需要登录。
    """
    payload = request.json or {}
    puzzle_id = payload.get("puzzle_id")
    score_value = payload.get("score")

    if puzzle_id is None or score_value is None:
        return jsonify({"error": "missing_params"}), 400

    try:
        score_value = int(score_value)
    except ValueError:
        return jsonify({"error": "invalid_score"}), 400

    score = ScoreService.submit_score(
        user_id=g.current_user.id,
        puzzle_id=puzzle_id,
        score_value=score_value,
    )
    return jsonify(
        {
            "message": "submitted",
            "score": {
                "id": score.id,
                "score": score.score,
                "puzzle_id": score.puzzle_id,
                "user_id": score.user_id,
                "created_at": score.created_at.isoformat() if score.created_at else None,
            },
        }
    ), 201
