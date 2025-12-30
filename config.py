import os

class Config:
    SECRET_KEY = 'SECRET_2024_3035_SECRET'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:MySQL-000000@127.0.0.1:3306/bookmarket?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大文件大小 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')