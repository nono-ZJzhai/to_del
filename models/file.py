from exts import db
from datetime import datetime

class FileItem(db.Model):
    """文件/文件夹模型"""
    __tablename__ = 'file_item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'file' 或 'folder'
    file_path = db.Column(db.String(500))  # 文件存储路径，文件夹为空
    file_size = db.Column(db.Integer)  # 文件大小（字节），文件夹为0
    parent_id = db.Column(db.Integer, db.ForeignKey('file_item.id'), nullable=True)  # 父文件夹ID
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.now)
    
    # 关系
    uploader = db.relationship('User', backref='uploaded_files')
    parent = db.relationship('FileItem', remote_side=[id], backref='children')
    ratings = db.relationship('FileRating', backref='file_item', cascade='all, delete-orphan')
    
    @property
    def upvotes_count(self):
        """统计赞同数量"""
        return FileRating.query.filter_by(file_id=self.id, rating_type='upvote').count()
    
    @property
    def downvotes_count(self):
        """统计不赞同数量"""
        return FileRating.query.filter_by(file_id=self.id, rating_type='downvote').count()


class FileRating(db.Model):
    """文件评分模型"""
    __tablename__ = 'file_rating'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file_item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating_type = db.Column(db.String(20), nullable=False)  # 'upvote' 或 'downvote'
    rate_time = db.Column(db.DateTime, default=datetime.now)
    
    # 关系
    user = db.relationship('User', backref='file_ratings')
    
    # 唯一约束：每个用户对每个文件只能评分一次
    __table_args__ = (db.UniqueConstraint('file_id', 'user_id', name='_file_user_rating_uc'),)

