from . import db
import os

def get_image_mime_type(image_bytes):
    if not isinstance(image_bytes, (bytes, bytearray)) or not image_bytes:
        return 'image/jpeg'
    if image_bytes[:3] == b'\xff\xd8\xff':
        return 'image/jpeg'
    elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'image/png'
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return 'image/gif'
    elif len(image_bytes) > 12 and image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return 'image/webp'
    return 'image/jpeg'

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    image = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))