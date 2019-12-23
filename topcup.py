#!/usr/bin/env python

import os
import sys
import imghdr

from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, \
                  send_file, url_for
from werkzeug import secure_filename

from PIL import Image

topcup = Flask(__name__)

script_path = os.path.dirname(os.path.abspath(__file__))

# Add script path to system path
if script_path not in sys.path:
   sys.path.insert(0, script_path)


# Application setting
# --------------------------------------------------

# Secret session key for passing flash message
topcup.secret_key = 'secret text for topcup program'

# Disable template cache
topcup.config['TEMPLATES_AUTO_RELOAD'] = True

# Disable response cache
@topcup.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, "\
                                        "public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


### TODO: Configurations

# Set the file size limit
topcup.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Location for uploading files. Make this configurable later.
upload_path = os.path.join(script_path, 'uploads')
try:
  if not os.path.exists(upload_path):
    os.makedirs(upload_path, 0o755)
except Exception as e:
  print("Error: %s\n" % e)
  raise

upload_img_path = os.path.join(upload_path, 'img')
try:
  if not os.path.exists(upload_img_path):
    os.makedirs(upload_img_path, 0o755)
except Exception as e:
  print("Error: %s\n" % e)
  raise

# Set the acceptable image file extension
img_extensions = [ 'gif', 'jpeg', 'png', 'tiff' ]


# --------------------------------------------------

@topcup.route('/')
@topcup.route('/index')
def index():
  return render_template('index.html')


@topcup.route('/upload-image', methods=["POST"])
def upload_image():
  if request.method == 'POST':
    if request.files:
      image = request.files['imgfile']

      if image.filename == '':
        flash('Please specify image to upload', 'danger')
      else:
        # Check if image type is supported
        img_test = image.read(1024)
        image.seek(0)
        if imghdr.what('', img_test) not in img_extensions:
          flash('Image type not supported (only supports: ' + \
                ', '.join(img_extensions) + ')', 'danger')
        else:
          filename = secure_filename(image.filename)
          try:
            # Filename for uploaded image
            # We use timestamp to make filename unique
            target_filename = datetime.today().strftime('%y%m%d-%H%M%S')

            # Get file extension as uploaded
            fext = os.path.splitext(filename)[1][1:].lower()

            # Combined filename
            target_filename = target_filename + '.' + fext

            image.save(os.path.join(upload_img_path, target_filename))
            flash('Image saved as: ' + target_filename, 'success')

          except IOError as e:
            flash('Cannot save image. Please try again later', 'warning')

  return redirect(url_for('index'))


@topcup.route('/gallery')
def gallery():
  # Read all files in the upload directory
  all_images = []
  img_files  = next(os.walk(upload_img_path))[2]

  for img in img_files:
    full_img_file = os.path.join(upload_img_path, img)
    img_ptr       = Image.open(full_img_file)

    all_images.append({ 'filename'  : img,
                        'filesize'  : os.path.getsize(full_img_file),
                        'width'     : img_ptr.size[0],
                        'height'    : img_ptr.size[1]
                     })

  sorted_images = sorted(all_images, key=lambda k: k['filename'])
  return render_template('gallery.html', images=sorted_images)


if __name__ == "__main__":
    topcup.run(debug=True)

