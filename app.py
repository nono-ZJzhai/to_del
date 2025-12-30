from flask import Flask
from exts import db
import config
from blueprints.front import bp as front_bp
from blueprints.user import bp as user_bp
from blueprints.book import bp as book_bp
from blueprints.file import bp as file_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(front_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(book_bp, url_prefix='/book')
    app.register_blueprint(file_bp, url_prefix='/file')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)