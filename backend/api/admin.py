from flask import Blueprint, request, jsonify
from services.puzzle_service import PuzzleService
from services.auth_service import AuthService
from utils.auth import admin_required


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = AuthService.list_users()
    data = [u.to_dict(include_sensitive=False) for u in users]
    return jsonify({"data": data}), 200


@admin_bp.route("/puzzles", methods=["GET"])
@admin_required
def admin_list_puzzles():
    puzzles = PuzzleService.list_puzzles()
    return jsonify({"data": [p.to_dict(include_answer=True) for p in puzzles]}), 200


@admin_bp.route("/puzzles", methods=["POST"])
@admin_required
def admin_create_puzzle():
    data = request.json or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    standard_answer = (data.get("standard_answer") or "").strip()
    created_by = data.get("created_by")

    if not title or not description or not standard_answer:
        return jsonify({"error": "missing_params"}), 400

    puzzle = PuzzleService.create_puzzle(
        title=title,
        description=description,
        standard_answer=standard_answer,
        created_by=created_by,
    )
    return jsonify(puzzle.to_dict(include_answer=True)), 201


@admin_bp.route("/puzzles/<int:puzzle_id>", methods=["PUT"])
@admin_required
def admin_update_puzzle(puzzle_id):
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


@admin_bp.route("/puzzles/<int:puzzle_id>", methods=["DELETE"])
@admin_required
def admin_delete_puzzle(puzzle_id):
    error = PuzzleService.delete_puzzle(puzzle_id)
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404
    return jsonify({"message": "deleted"}), 200
