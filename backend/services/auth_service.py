from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.session import GameSession
from models.score import Score
from utils.db import db


class AuthService:
    """
    用户注册 / 登录 服务层
    """

    @staticmethod
    def register(username: str, password: str):
        if not username or not password:
            return None, "missing_params"

        exists = User.query.filter_by(username=username).first()
        if exists:
            return None, "user_exists"

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login(username: str, password: str):
        if not username or not password:
            return None, "missing_params"

        user = User.query.filter_by(username=username).first()
        if not user:
            return None, "invalid_credentials"

        if not check_password_hash(user.password_hash, password):
            return None, "invalid_credentials"

        return user, None

    @staticmethod
    def get_user_by_id(user_id: int):
        return User.query.get(user_id)

    @staticmethod
    def list_users():
        return User.query.order_by(User.id.desc()).all()

    @staticmethod
    def set_admin(user_id: int, is_admin: bool):
        user = User.query.get(user_id)
        if not user:
            return None, "not_found"

        if user.username == "admin" and not is_admin:
            return None, "cannot_modify_super_admin"

        if not is_admin and user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                return None, "cannot_remove_last_admin"

        user.is_admin = bool(is_admin)
        db.session.commit()
        return user, None

    @staticmethod
    def delete_user(user_id: int, requester_user_id: int):
        user = User.query.get(user_id)
        if not user:
            return "not_found"

        if user.username == "admin":
            return "cannot_modify_super_admin"

        if user.id == requester_user_id:
            return "cannot_delete_self"

        if user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                return "cannot_delete_last_admin"

        # 清理关联数据，避免排行榜 join 失败或产生孤儿记录
        Score.query.filter_by(user_id=user.id).delete(synchronize_session=False)
        GameSession.query.filter_by(user_id=user.id).delete(synchronize_session=False)

        db.session.delete(user)
        db.session.commit()
        return None
