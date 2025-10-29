# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import sqlite3
import datetime
from model import analyze_emotion # Import the function from model.py

# --- Configuration ---
UPLOAD_FOLDER = 'static/uploads' # Images are saved here before analysis
DATABASE_NAME = 'emotion_app_data.db' # The database file name
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super_secret_key_for_flash_messages' # Necessary for flash messages

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database Functions ---

def init_db():
    """Initializes the SQLite database with the required table."""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    # Table to store user data, image path, and analysis result
    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            image_filename TEXT NOT NULL,
            analysis_result TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized: {DATABASE_NAME}")

def insert_analysis_result(name, filename, result):
    """Inserts a new analysis record into the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO analyses (user_name, image_filename, analysis_result) VALUES (?, ?, ?)",
        (name, filename, result)
    )
    conn.commit()
    conn.close()
    
# Initialize the database when the app starts
init_db()

# --- Utility Functions ---

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 1. Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        user_name = request.form.get('name', 'Anonymous') # Get name from form

        # 2. If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        # 3. Process the file if it's valid
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create a unique filename to prevent overwriting
            unique_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            # 4. Call the model to analyze emotion
            emotion_result = analyze_emotion(filepath)
            
            # 5. Save the result to the database
            insert_analysis_result(user_name, unique_filename, emotion_result)
            
            # 6. Redirect to a results page or show result
            return redirect(url_for('results', filename=unique_filename, result=emotion_result))
            
        else:
            flash('Invalid file type. Only PNG, JPG, JPEG are allowed.', 'error')
            return redirect(request.url)

    # For GET request, show the upload form
    return render_template('index.html')

@app.route('/results')
def results():
    """Displays the result of the analysis."""
    filename = request.args.get('filename')
    result = request.args.get('result')
    
    # Construct the path for the image to display it in the HTML
    image_url = url_for('static', filename=f'uploads/{filename}') if filename else Nonerender the singular 'result.html' template (matches templates/result.html)
    return render_template('result.html', image_url=image_url, emotion=result)

@app.route('/history')
def history():
    """Displays the history of all analyses from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    c = conn.cursor()
    c.execute("SELECT * FROM analyses ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()
    return render_template('history.html', records=records)


if __name__ == '__main__':
    # You might need to change '127.0.0.1' to '0.0.0.0' for deployment
    app.run(debug=True)