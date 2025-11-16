from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
import json
import base64 

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Routes ---

@app.route('/')
def index():
    """
    Renders the MemoTape landing page (index.html).
    """
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
    location = request.form.get('location', 'Unknown Location')
    date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    story = request.form.get('story', 'No story provided.')
    bg_color = request.form.get('background-color', '#10B981')
    
    uploaded_files = request.files.getlist('media-files')
    file_metadata = []
    
    for file in uploaded_files:
        if file.filename and file.content_type.startswith('image/'):
            try:
                file_data = file.read()
                
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                
                file_metadata.append({
                    'name': file.filename,
                    'mime_type': file.content_type,
                    'data': encoded_data, 
                })
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                
    safe_location = location.replace(' ', '_').lower()
    file_prefix = f"{safe_location}_{date_str}"
    filename = f"{file_prefix}.memo"
    
    memo_content = {
        'title': f"MemoTape: {location} on {date_str}",
        'location': location,
        'date': date_str,
        'background_color': bg_color,
        'story': story,
        'media_files': file_metadata
    }

    try:
        directory = os.getcwd()
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w') as f:
            f.write(json.dumps(memo_content, indent=4, separators=(',', ': ')))
        
        print(f"Successfully generated MemoTape file: {filename}")
        
        return send_from_directory(
            directory,
            filename,
            as_attachment=True,
            mimetype='application/octet-stream' 
        )
        
    except Exception as e:
        print(f"Error creating file: {e}")
        return "<h1>Error generating MemoTape.</h1>"

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=False, host="0.0.0.0", port="5000")