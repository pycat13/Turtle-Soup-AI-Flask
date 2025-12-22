from flask import Blueprint, request, jsonify, g
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


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id: int):
    payload = request.json or {}
    if "is_admin" not in payload:
        return jsonify({"error": "missing_params"}), 400

    user, error = AuthService.set_admin(user_id=user_id, is_admin=bool(payload["is_admin"]))
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404
    if error == "cannot_modify_super_admin":
        return jsonify({"error": "cannot_modify_super_admin"}), 400
    if error == "cannot_remove_last_admin":
        return jsonify({"error": "cannot_remove_last_admin"}), 400

    return jsonify({"user": user.to_dict(include_sensitive=False)}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id: int):
    error = AuthService.delete_user(user_id=user_id, requester_user_id=g.current_user.id)
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404
    if error in ("cannot_delete_self", "cannot_delete_last_admin", "cannot_modify_super_admin"):
        return jsonify({"error": error}), 400
    return jsonify({"message": "deleted"}), 200


@admin_bp.route("/puzzles", methods=["GET"])
@admin_required
def admin_list_puzzles():
    puzzles = PuzzleService.list_puzzles()
    return jsonify({"data": [p.to_admin_dict() for p in puzzles]}), 200


@admin_bp.route("/puzzles", methods=["POST"])
@admin_required
def admin_create_puzzle():
    data = request.json or {}
    title_zh = (data.get("title_zh") or "").strip()
    description_zh = (data.get("description_zh") or "").strip()
    standard_answer_zh = (data.get("standard_answer_zh") or "").strip()
    title_en = (data.get("title_en") or "").strip() or None
    description_en = (data.get("description_en") or "").strip() or None
    standard_answer_en = (data.get("standard_answer_en") or "").strip() or None
    created_by = data.get("created_by")

    if not title_zh or not description_zh or not standard_answer_zh:
        return jsonify({"error": "missing_params"}), 400

    puzzle = PuzzleService.create_puzzle(
        title_zh=title_zh,
        description_zh=description_zh,
        standard_answer_zh=standard_answer_zh,
        title_en=title_en,
        description_en=description_en,
        standard_answer_en=standard_answer_en,
        created_by=created_by,
    )
    return jsonify(puzzle.to_admin_dict()), 201


@admin_bp.route("/puzzles/<int:puzzle_id>", methods=["PUT"])
@admin_required
def admin_update_puzzle(puzzle_id):
    data = request.json or {}
    title_zh = (data.get("title_zh") or "").strip()
    description_zh = (data.get("description_zh") or "").strip()
    standard_answer_zh = (data.get("standard_answer_zh") or "").strip()
    title_en = (data.get("title_en") or "").strip() or None
    description_en = (data.get("description_en") or "").strip() or None
    standard_answer_en = (data.get("standard_answer_en") or "").strip() or None

    if not title_zh or not description_zh or not standard_answer_zh:
        return jsonify({"error": "missing_params"}), 400

    puzzle, error = PuzzleService.update_puzzle(
        puzzle_id,
        title_zh=title_zh,
        description_zh=description_zh,
        standard_answer_zh=standard_answer_zh,
        title_en=title_en,
        description_en=description_en,
        standard_answer_en=standard_answer_en,
    )
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404

    return jsonify(puzzle.to_admin_dict()), 200


@admin_bp.route("/puzzles/<int:puzzle_id>", methods=["DELETE"])
@admin_required
def admin_delete_puzzle(puzzle_id):
    error = PuzzleService.delete_puzzle(puzzle_id)
    if error == "not_found":
        return jsonify({"error": "not_found"}), 404
    return jsonify({"message": "deleted"}), 200
