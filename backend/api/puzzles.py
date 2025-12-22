from flask import Blueprint, request, jsonify
from services.puzzle_service import PuzzleService

puzzles_bp = Blueprint("puzzles", __name__)


@puzzles_bp.route("", methods=["GET"])
def list_puzzles():
    lang = request.args.get("lang", "zh")
    puzzles = PuzzleService.list_puzzles()
    return jsonify([p.to_public_dict(lang=lang) for p in puzzles]), 200


@puzzles_bp.route("/<int:puzzle_id>", methods=["GET"])
def get_puzzle(puzzle_id):
    lang = request.args.get("lang", "zh")
    puzzle = PuzzleService.get_puzzle(puzzle_id)
    if not puzzle:
        return jsonify({"error": "not_found"}), 404
    # 公共接口不返回标准答案；管理端走 /api/admin/*
    return jsonify(puzzle.to_public_dict(lang=lang)), 200
