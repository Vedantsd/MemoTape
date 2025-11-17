from flask import Flask, render_template, request, send_file
import os
from datetime import datetime
from PIL import Image
import io
import json
import base64
import uuid

app = Flask(__name__)

# Temporary upload directory (Vercel allows /tmp)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create_memotape_form():
    return render_template('create_memotape.html')

@app.route('/read')
def read_memotape_form():
    return render_template('read_memotape.html')

@app.route('/story')
def display_memotape_story():
    return render_template('story_display.html')

@app.route('/create_memo', methods=['POST'])
def create_memo():
    # Get form values
    location = request.form.get('location', 'Unknown Location')
    date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    story = request.form.get('story', 'No story provided.')
    bg_color = request.form.get('background-color', '#10B981')

    uploaded_files = request.files.getlist('media-files')
    file_metadata = []

    MAX_SIZE = 400 * 1024
    MAX_DIMENSION = 1600

    # Process uploaded images and encode as base64
    for file in uploaded_files:
        if file.filename and file.content_type.startswith('image/'):
            try:

                img = Image.open(file.stream) 
                img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

                buffer = io.BytesIO()

                if img.format == "JPEG":
                    img.save(buffer, format="JPEG", optimize=True, quality=75)
                else:
                    img.save(buffer, format=img.format, optimize=True)

                data = buffer.getvalue()

                size_mb = len(data) 
                if size_mb > MAX_SIZE:
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", optimize=True, quality=50)
                    data = buffer.getvalue()

                encoded = base64.b64encode(data).decode("utf-8")

                file_metadata.append({
                    'name': file.filename,
                    'mime_type': file.content_type,
                    'data': encoded
                })
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")

    safe_location = location.replace(' ', '_').lower()
    file_prefix = f"{safe_location}_{date_str}"

    # Use a random suffix to avoid filename collisions
    filename = f"{file_prefix}_{uuid.uuid4().hex[:6]}.memo"

    # Build the memo file content
    memo_content = {
        'title': f"MemoTape: {location} on {date_str}",
        'location': location,
        'date': date_str,
        'background_color': bg_color,
        'story': story,
        'media_files': file_metadata
    }

    # Save to /tmp (Vercel allows this)
    file_path = os.path.join('/tmp', filename)
    try:
        with open(file_path, 'w') as f:
            json.dump(memo_content, f, indent=4)
    except Exception as e:
        print("Error creating memo:", e)
        return "<h1>Error generating MemoTape.</h1>"

    # Send the temporary file
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

# Vercel handler
if __name__ == "__main__":
    app.run(debug=False, port=5000)