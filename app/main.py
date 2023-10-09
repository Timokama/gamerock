import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app,Response, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .image import Images
from .user import User
import os
import base64
import io

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('home.html', name = current_user.username, contact = current_user.phone_num, email = current_user.role.name)

@main.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    img = user.image
    if not img:
        return redirect(url_for('main.upload_file'))
    
    # img=Images.query.filter_by(id = 1).order_by(Images.id.desc()).first_or_404()
    image_list = []
    # read image data from db back to form a rendable in html
    for img in img:
        image = base64.b64encode(img.image).decode('ascii')
        image_list.append(image)
    
    return render_template('profile.html', name = current_user.username, contact = current_user.phone_num, email = current_user.role, image_list=image_list, img = img)

upload_folder = os.path.join('static')

def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """
    filename = current_app.config['UPLOAD_FOLDER'] 

    return filename

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    user = User.query.get_or_404(current_user.id)
   
    if request.method == 'POST':
        file = request.files['image']
        newFile=Images(
        name=file.filename,
        image=file.read(),
        user = user
        )        
        db.session.add(newFile)
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template('other.html')

@main.route('/image')
def get_images():
    images = db.session.query(Images).all()
    image_list = []
    # read image data from db back to form a rendable in html
    for img in images:
        image = base64.b64encode(img.image).decode('ascii')
        image_list.append(image)
    return render_template('image.html', image_list=image_list)

# @main.route('/download')
# def download():
#     file_data = Images.query.filter_by(id=1).first()

#     return send_file(io.BytesIO(file_data.image),
# attachment_filename='user.jpg',as_attachment=True) 

@main.route('/<int:img_id>/new_upload', methods=['GET', 'POST'])
def uploadNew(img_id):
    user = User.query.get_or_404(current_user.id)
    image = Images.query.get_or_404(img_id)
    if request.method == 'POST':
        file = request.files['image']
        # newFile=Images(
        # name=file.filename,
        # image=file.read()
        # )
        image.name = file.filename
        image.image = file.read()

        db.session.add(image)
        db.session.commit()
        return redirect(url_for('main.profile'))
    return render_template('other.html')