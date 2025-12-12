from flask import Blueprint, request, jsonify, g
from services.puzzle_service import PuzzleService
from utils.auth import login_required, admin_required

puzzles_bp = Blueprint("puzzles", __name__)


@puzzles_bp.route("", methods=["GET"])
def list_puzzles():
    puzzles = PuzzleService.list_puzzles()
    return jsonify([p.to_dict(include_answer=False) for p in puzzles]), 200


@puzzles_bp.route("/<int:puzzle_id>", methods=["GET"])
def get_puzzle(puzzle_id):
    puzzle = PuzzleService.get_puzzle(puzzle_id)
    if not puzzle:
        return jsonify({"error": "not_found"}), 404

    include_answer = False
    # 管理员可查看标准答案
    if getattr(g, "current_user", None) and getattr(g.current_user, "is_admin", False):
        include_answer = True

    return jsonify(puzzle.to_dict(include_answer=include_answer)), 200


@puzzles_bp.route("", methods=["POST"])
@admin_required
def create_puzzle():
    data = request.json or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    standard_answer = (data.get("standard_answer") or "").strip()

    if not title or not description or not standard_answer:
        return jsonify({"error": "missing_params"}), 400

    puzzle = PuzzleService.create_puzzle(
        title=title,
        description=description,
        standard_answer=standard_answer,
        created_by=g.current_user.id if getattr(g, "current_user", None) else None,
    )
    return jsonify(puzzle.to_dict(include_answer=True)), 201


@puzzles_bp.route("/<int:puzzle_id>", methods=["PUT"])
@admin_required
def update_puzzle(puzzle_id):
    data = request.json or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    standard_answer = (data.get("standard_answer") or "").strip()

    if not title or not description or not standard_answer:
        return jsonify({"error": "missing_params"}), 400

    puzzle, error = PuzzleService.update_puzzle(
        puzzle_id, title, description, standard_answer
    )
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404

    return jsonify(puzzle.to_dict(include_answer=True)), 200


@puzzles_bp.route("/<int:puzzle_id>", methods=["DELETE"])
@admin_required
def delete_puzzle(puzzle_id):
    error = PuzzleService.delete_puzzle(puzzle_id)
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404
    return jsonify({"message": "deleted"}), 200
