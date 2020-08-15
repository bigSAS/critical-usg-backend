import os, pathlib
import uuid

from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename


from cusg.utils.http import ok_response, ValidationError
from cusg.utils.permissions import restricted

files_blueprint = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
UPLOAD_FOLDER = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/') + '/../files'
print('FILES UPLOAD FOLDER', UPLOAD_FOLDER)


@files_blueprint.route('/add', methods=('POST',))
@restricted(['ADMIN'])
def add_file():
    """ upload file """
    file = request.files.get('file', None)
    if not file: raise ValidationError('file is missing', 'file')
    filename, ext = tuple(file.filename.rsplit('.', 1))
    if ext.lower().strip() not in ALLOWED_EXTENSIONS:
        raise ValidationError('invalid file extension', 'file')
    filename += f'{str(uuid.uuid4())[:7].replace("-", "")}.{ext}'
    filename = secure_filename(filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return ok_response({'uploaded_filename': filename})


@files_blueprint.route('/get/<filename>', methods=('GET',))
def get_file(filename: str):
    return send_from_directory('files', filename)
