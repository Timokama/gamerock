import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app,Response, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .image import Images
from .user import User
import os
import base64
from PIL import Image
import io

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('home.html', name = current_user.name, contact = current_user.contact, email = current_user.email)

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
    
    return render_template('profile.html', name = current_user.name, contact = current_user.contact, email = current_user.email, image_list=image_list)

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
    # img = Images.query.filter_by(user=user).first_or_404()
    if request.method == 'POST':
        file = request.files['image']
        newFile=Images(
        name=file.filename,
        image=file.read(),
        user = user
        )

        # img.name = newFile.name
        # img.image = newFile.image
        
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