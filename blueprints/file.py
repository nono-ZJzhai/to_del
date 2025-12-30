from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash, jsonify, send_from_directory
from models.file import FileItem, FileRating
from models.user import User
from exts import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('file', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    """获取上传文件夹路径"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

@bp.route('/list')
@bp.route('/list/<int:folder_id>')
def file_list(folder_id=None):
    """文件列表页面"""
    if not g.user:
        flash('请先登录', 'error')
        return redirect(url_for('user.login'))
    
    # 获取当前文件夹
    current_folder = None
    if folder_id:
        current_folder = FileItem.query.get(folder_id)
        if not current_folder or current_folder.type != 'folder':
            flash('文件夹不存在', 'error')
            return redirect(url_for('file.file_list'))
    
    # 获取当前文件夹下的文件和文件夹
    files = FileItem.query.filter_by(parent_id=folder_id).order_by(FileItem.type.desc(), FileItem.upload_time.desc()).all()
    
    # 获取用户对每个文件的评分状态
    file_ids = [f.id for f in files if f.type == 'file']
    user_ratings = {}
    if file_ids and g.user:
        ratings = FileRating.query.filter(
            FileRating.file_id.in_(file_ids),
            FileRating.user_id == g.user.id
        ).all()
        user_ratings = {r.file_id: r.rating_type for r in ratings}
    
    # 获取面包屑导航
    breadcrumbs = []
    if current_folder:
        parent = current_folder.parent
        while parent:
            breadcrumbs.insert(0, parent)
            parent = parent.parent
    
    return render_template('file/list.html', 
                         files=files, 
                         current_folder=current_folder,
                         breadcrumbs=breadcrumbs,
                         folder_id=folder_id,
                         user_ratings=user_ratings)

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """上传文件"""
    if not g.user:
        flash('请先登录', 'error')
        return redirect(url_for('user.login'))
    
    if request.method == 'POST':
        # 检查是否有文件
        if 'file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        parent_id = request.form.get('parent_id', type=int)
        
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # 安全文件名
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename  # 添加时间戳避免重名
            
            # 保存文件
            upload_folder = get_upload_folder()
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 创建文件记录
            file_item = FileItem(
                name=file.filename,  # 显示原始文件名
                type='file',
                file_path=filename,  # 存储实际文件名
                file_size=file_size,
                parent_id=parent_id,
                uploader_id=g.user.id
            )
            db.session.add(file_item)
            db.session.commit()
            
            flash('文件上传成功', 'success')
            return redirect(url_for('file.file_list', folder_id=parent_id))
        else:
            flash('不支持的文件类型', 'error')
            return redirect(request.url)
    
    # GET请求：显示上传表单
    parent_id = request.args.get('parent_id', type=int)
    return render_template('file/upload.html', parent_id=parent_id)

@bp.route('/create_folder', methods=['POST'])
def create_folder():
    """创建文件夹"""
    if not g.user:
        flash('请先登录', 'error')
        return redirect(url_for('user.login'))
    
    folder_name = request.form.get('folder_name', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    
    if not folder_name:
        flash('文件夹名称不能为空', 'error')
        return redirect(url_for('file.file_list', folder_id=parent_id))
    
    # 检查同一目录下是否有重名
    existing = FileItem.query.filter_by(
        name=folder_name,
        type='folder',
        parent_id=parent_id
    ).first()
    
    if existing:
        flash('该文件夹已存在', 'error')
        return redirect(url_for('file.file_list', folder_id=parent_id))
    
    # 创建文件夹记录
    folder = FileItem(
        name=folder_name,
        type='folder',
        file_path=None,
        file_size=0,
        parent_id=parent_id,
        uploader_id=g.user.id
    )
    db.session.add(folder)
    db.session.commit()
    
    flash('文件夹创建成功', 'success')
    return redirect(url_for('file.file_list', folder_id=parent_id))

@bp.route('/download/<int:file_id>')
def download_file(file_id):
    """下载文件"""
    if not g.user:
        flash('请先登录', 'error')
        return redirect(url_for('user.login'))
    
    file_item = FileItem.query.get(file_id)
    if not file_item or file_item.type != 'file':
        flash('文件不存在', 'error')
        return redirect(url_for('file.file_list'))
    
    upload_folder = get_upload_folder()
    return send_from_directory(upload_folder, file_item.file_path, as_attachment=True, download_name=file_item.name)

@bp.route('/rate/<int:file_id>/<rating_type>', methods=['POST'])
def rate_file(file_id, rating_type):
    """对文件进行评分（赞同/不赞同）"""
    if not g.user:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    if rating_type not in ['upvote', 'downvote']:
        return jsonify({'success': False, 'message': '无效的评分类型'}), 400
    
    file_item = FileItem.query.get(file_id)
    if not file_item:
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    # 检查是否已经评分
    existing_rating = FileRating.query.filter_by(
        file_id=file_id,
        user_id=g.user.id
    ).first()
    
    if existing_rating:
        # 如果评分类型相同，则取消评分（删除）
        if existing_rating.rating_type == rating_type:
            db.session.delete(existing_rating)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': '已取消评分',
                'upvotes': file_item.upvotes_count,
                'downvotes': file_item.downvotes_count,
                'user_rating': None
            })
        else:
            # 如果评分类型不同，则更新评分
            existing_rating.rating_type = rating_type
            existing_rating.rate_time = datetime.now()
    else:
        # 创建新评分
        new_rating = FileRating(
            file_id=file_id,
            user_id=g.user.id,
            rating_type=rating_type
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    # 重新查询以获取最新统计
    file_item = FileItem.query.get(file_id)
    return jsonify({
        'success': True,
        'message': '评分成功',
        'upvotes': file_item.upvotes_count,
        'downvotes': file_item.downvotes_count,
        'user_rating': rating_type
    })

@bp.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    """删除文件或文件夹"""
    if not g.user:
        flash('请先登录', 'error')
        return redirect(url_for('user.login'))
    
    file_item = FileItem.query.get(file_id)
    if not file_item:
        flash('文件不存在', 'error')
        return redirect(url_for('file.file_list'))
    
    # 检查权限：只有上传者可以删除
    if file_item.uploader_id != g.user.id:
        flash('无权删除此文件', 'error')
        return redirect(url_for('file.file_list', folder_id=file_item.parent_id))
    
    parent_id = file_item.parent_id
    
    # 如果是文件，删除物理文件
    if file_item.type == 'file':
        upload_folder = get_upload_folder()
        file_path = os.path.join(upload_folder, file_item.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # 删除数据库记录（级联删除会处理子文件和评分）
    db.session.delete(file_item)
    db.session.commit()
    
    flash('删除成功', 'success')
    return redirect(url_for('file.file_list', folder_id=parent_id))

