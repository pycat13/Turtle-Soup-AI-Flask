# backend/app.py
import os
from flask import Flask, send_from_directory
from api.play import play_bp
from api.scores import scores_bp
from api.auth import auth_bp
from api.puzzles import puzzles_bp
from api.admin import admin_bp
from utils.db import db


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///haiguitang.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(play_bp, url_prefix='/api/play')
    app.register_blueprint(scores_bp, url_prefix='/api/scores')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(puzzles_bp, url_prefix='/api/puzzles')

    @app.route('/ping')
    def ping():
        return {'message': 'pong'}

    # 静态文件托管：用于直接访问前端 HTML/CSS/JS
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_frontend(path):
        target_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(target_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, 'index.html')

    # 简单的全局 CORS 处理，便于前后端分开部署时调用
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    return app


def seed_puzzles():
    """
    简单种子数据，方便开发阶段演示。
    """
    try:
        from models.puzzle import Puzzle
        from utils.db import db
        if Puzzle.query.count() == 0:
            samples = [
                Puzzle(
                    title="The Sea Turtle Soup",
                    description="A man walks into a restaurant, orders sea turtle soup... Why?",
                    standard_answer="He once survived a wreck eating fake turtle; the real taste made him realize the lie and he took his life."
                ),
                Puzzle(
                    title="The Broken Wood",
                    description="A man lies dead in a field. Next to him is a package. Why?",
                    standard_answer="He jumped with a parachute that failed; the wooden box held the chute."
                ),
                Puzzle(
                    title="Elevator Man",
                    description="A short man takes the elevator to the 10th floor and walks the rest of the way. Why?",
                    standard_answer="He can only reach the 10th floor button unless it rains and he uses an umbrella to reach higher."
                ),
                Puzzle(
                    title="The Phone Call",
                    description="A man calls his wife, then immediately calls the police. Why?",
                    standard_answer="He heard his wife answer from the home phone even though she should be traveling, fearing danger."
                ),
                Puzzle(
                    title="Desert and Water",
                    description="Two men walk into the desert. One brings water, one brings a gun. Only one returns. Why?",
                    standard_answer="They planned a mercy kill if water ran out; the gun carrier shot the other to end suffering and survived."
                ),
                Puzzle(
                    title="The Blindfold",
                    description="A man is found blindfolded, dead in his own backyard. Why?",
                    standard_answer="He was part of a firing squad game; the blindfold signaled execution, and he was shot by mistake."
                ),
            ]
            db.session.add_all(samples)
            db.session.commit()
    except Exception:
        # 开发辅助函数，不阻断应用启动
        pass


def seed_admin():
    """
    创建一个开发用的管理员账户 admin / admin123，如果不存在。
    """
    try:
        from models.user import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username="admin").first():
            admin_user = User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                is_admin=True,
            )
            db.session.add(admin_user)
            db.session.commit()
    except Exception:
        pass


if __name__ == '__main__':
    app = create_app()

    # 创建所有表结构
    with app.app_context():
        db.create_all()
        seed_puzzles()
        seed_admin()

    app.run(debug=True)
