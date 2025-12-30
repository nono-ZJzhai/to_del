import click
from flask import Flask
from exts import db
from models.user import User
from models.book import Book
import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    db.init_app(app)
    return app

@click.command()
@click.option('--drop', is_flag=True, help='删除并重建数据库')
def initdb(drop):
    drop = True
    app = create_app()
    with app.app_context():
        if drop:
            click.confirm('此操作将删除所有数据，确定继续？', abort=True)
            db.drop_all()
        db.create_all()
        click.echo('数据库初始化完成')

if __name__ == '__main__':
    initdb()