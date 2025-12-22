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
                    title_zh="不用救他",
                    description_zh="当我们开着救护车赶到食物中毒的那户人家时，所有的人连站都站不起来，脸上全无血色。正当我们打算将危险性最高的老人先抬上救护车时，所有人却异口同声地大叫：“不用救他！”为什么？",
                    standard_answer_zh="老人已经病故了，家人是为了给他准备葬礼才聚集到一起，他们不幸集体食物中毒而昏倒，所以当救护人员想先救老人时，家人叫“不用救他”。",
                    title_en="‘Don't Save Him’",
                    description_en="When we arrived at a family with an ambulance for food poisoning, everyone couldn’t even stand and had no color in their faces. Just as we were about to put the most at-risk old man into the ambulance first, everyone shouted in unison: 'Don't save him!' Why?",
                    standard_answer_en="The old man had already died; the family had gathered to prepare for his funeral. They all suffered food poisoning and collapsed, so when the rescuers tried to save the old man first, the family shouted ‘Don't save him’ because he was already dead.",
                ),
                Puzzle(
                    title_zh="忠诚的狗",
                    description_zh="小强养了一只忠诚的狗，有一天他牵着狗上街，结果小强死了。为什么？",
                    standard_answer_zh="小强有心脏病，那天上街时突然病发倒地。他的忠心狗狗一直阻止陌生人靠近小强，导致没有人帮他最终死亡。",
                    title_en="The Loyal Dog",
                    description_en="Xiaoqiang had a loyal dog. One day he walked his dog on the street, and then Xiaoqiang died. Why?",
                    standard_answer_en="Xiaoqiang had a heart condition and suddenly collapsed on the street. His loyal dog kept strangers from approaching him, so no one came to help and he died.",
                )
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
        password_hash = generate_password_hash("admin123")
        user = User.query.filter_by(username="admin").first()
        if not user:
            user = User(username="admin", password_hash=password_hash, is_admin=True)
            db.session.add(user)
        else:
            user.is_admin = True
            user.password_hash = password_hash
        db.session.commit()
    except Exception:
        pass


def migrate_puzzles_table():
    """
    方案A：为 puzzles 表补充英文列（title_en/description_en/standard_answer_en）。
    SQLite 支持 ADD COLUMN，开发环境下做轻量迁移。
    """
    try:
        engine = db.engine
        with engine.connect() as conn:
            cols = conn.exec_driver_sql("PRAGMA table_info(puzzles)").fetchall()
            existing = {c[1] for c in cols}  # name at index 1

            to_add = []
            if "title_en" not in existing:
                to_add.append(("title_en", "VARCHAR(200)"))
            if "description_en" not in existing:
                to_add.append(("description_en", "TEXT"))
            if "standard_answer_en" not in existing:
                to_add.append(("standard_answer_en", "TEXT"))

            for name, col_type in to_add:
                conn.exec_driver_sql(f"ALTER TABLE puzzles ADD COLUMN {name} {col_type}")
    except Exception:
        pass


if __name__ == '__main__':
    app = create_app()

    # 创建所有表结构
    with app.app_context():
        db.create_all()
        migrate_puzzles_table()
        seed_puzzles()
        seed_admin()

    app.run(debug=True)
