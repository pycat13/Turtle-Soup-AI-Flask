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
                    title_zh="海龟汤",
                    description_zh="一个男人走进餐馆点了一碗海龟汤，喝了一口后突然痛哭并自杀。为什么？",
                    standard_answer_zh="他曾在海难中靠“海龟汤”活命，但那其实是同伴用人肉冒充的；如今喝到真正的海龟汤，才意识到当年的真相，崩溃自尽。",
                    title_en="The Sea Turtle Soup",
                    description_en="A man orders sea turtle soup. After one sip, he cries and later takes his own life. Why?",
                    standard_answer_en="He once survived a shipwreck eating 'turtle soup' that was actually human flesh; tasting real turtle soup reveals the truth and he collapses."
                ),
                Puzzle(
                    title_zh="破碎的木头",
                    description_zh="一个男人死在田野里，旁边有一个包裹。为什么？",
                    standard_answer_zh="他跳伞失败坠亡，旁边的包裹是装伞的木箱（或伞包）碎片。",
                    title_en="The Broken Wood",
                    description_en="A man lies dead in a field. Next to him is a package. Why?",
                    standard_answer_en="He died in a parachute accident; the package/box nearby was related to the failed chute."
                ),
                Puzzle(
                    title_zh="电梯里的矮个子",
                    description_zh="一个矮个子每天坐电梯到10楼就走楼梯，只有下雨天才坐到顶楼。为什么？",
                    standard_answer_zh="他够不着高楼层按钮；下雨天带伞能用伞尖按到更高楼层。",
                    title_en="Elevator Man",
                    description_en="A short man takes the elevator to the 10th floor and walks the rest. Only on rainy days he goes higher. Why?",
                    standard_answer_en="He can't reach the higher buttons; on rainy days he uses his umbrella to press them."
                ),
                Puzzle(
                    title_zh="那通电话",
                    description_zh="一个男人给妻子打电话，挂断后立刻报警。为什么？",
                    standard_answer_zh="他听到妻子从家里的座机接起，而妻子本应在外地，怀疑家中出事（或有人冒充）。",
                    title_en="The Phone Call",
                    description_en="A man calls his wife and then immediately calls the police. Why?",
                    standard_answer_en="He hears her answer from the home phone even though she should be away, so he suspects danger at home."
                ),
                Puzzle(
                    title_zh="沙漠与水",
                    description_zh="两个人走进沙漠，一个带水，一个带枪，只有一个走出来。为什么？",
                    standard_answer_zh="他们约定如果撑不下去就由带枪的人结束痛苦；最后枪杀同伴后自己活着走出。",
                    title_en="Desert and Water",
                    description_en="Two men enter the desert. One brings water, one brings a gun. Only one returns. Why?",
                    standard_answer_en="They agreed the gun was for a mercy killing if they ran out of water; he used it and survived."
                ),
                Puzzle(
                    title_zh="蒙眼的人",
                    description_zh="一个男人被蒙着眼睛死在自家后院。为什么？",
                    standard_answer_zh="他参与了类似“行刑队”的游戏或训练，被蒙眼后发生意外中弹身亡。",
                    title_en="The Blindfold",
                    description_en="A man is found blindfolded, dead in his backyard. Why?",
                    standard_answer_en="He was involved in a firing-squad style game/training; blindfolded, he was accidentally shot."
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
        engine = db.get_engine()
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
