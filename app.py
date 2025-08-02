from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import speech_recognition as sr
import os
import time
from pydub import AudioSegment
import mysql.connector
import json
from hand_gesture_utils import verify_gesture, flatten_landmarks
from voice_utils import get_embedding, compare_embeddings

app = Flask(__name__)
app.secret_key = 'supersecretkey123'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# ---------- MySQL Database Setup ---------- #
# ✅ Load MySQL connection details from environment variables
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ MySQL Connection Error: {err}")
        return None

# ---------- Routes ---------- #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init-db')
def init_db():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            return "❌ Could not connect to the database."
        cursor = conn.cursor()
        # ✅ MySQL-compatible CREATE TABLE statement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                voice_text TEXT NOT NULL,
                gesture_array TEXT NOT NULL,
                voice_embedding TEXT NOT NULL
            )
        """)
        conn.commit()
        return "✅ Table 'users' created successfully for MySQL!"
    except Exception as e:
        return f"❌ Error initializing database: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# ---------- Register ---------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        voice_text = request.form.get('voice_text')
        gesture_array_json = request.form.get('gesture_array')

        try:
            gesture_array = json.loads(gesture_array_json)
            binary_gesture = flatten_landmarks(gesture_array)
            gesture_json_to_store = json.dumps(binary_gesture)
        except Exception as e:
            print(f"❌ Gesture processing failed: {e}")
            return "❌ Invalid gesture format"

        voice_path = f'static/voices/{username}_register.wav'
        voice_embedding = get_embedding(voice_path)
        if not voice_embedding:
            return "❌ Could not extract voice features."

        embedding_json = json.dumps(voice_embedding)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, voice_text, gesture_array, voice_embedding) VALUES (%s, %s, %s, %s)",
                (username, voice_text, gesture_json_to_store, embedding_json)
            )
            conn.commit()
        except Exception as e:
            print(f"❌ Registration DB error: {e}")
            return "❌ Failed to register user."
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# ---------- Login ---------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        voice_text = request.form.get('voice_text')
        input_array_json = request.form.get('gesture_array')

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT voice_text, gesture_array, voice_embedding FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if not result:
                return "❌ User not found"

            stored_voice, stored_array_json, stored_embedding_json = result

            if stored_voice.lower() != voice_text.lower():
                return "❌ Voice phrase mismatch"

            stored_array = json.loads(stored_array_json)
            input_array = json.loads(input_array_json)
            if not verify_gesture(input_array, stored_array):
                return "❌ Gesture pattern mismatch"

            login_path = f'static/voices/{username}_login.wav'
            login_embedding = get_embedding(login_path)
            if not login_embedding:
                return "❌ Failed to extract voice features."

            stored_embedding = json.loads(stored_embedding_json)
            if not compare_embeddings(login_embedding, stored_embedding):
                return "❌ Voice identity mismatch"

            session['user'] = username
            return redirect(url_for('dashboard'))

        except Exception as e:
            print(f"❌ Login error: {e}")
            return "❌ Login failed due to internal error."
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    return render_template('login.html')

# ---------- Dashboard ---------- #
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# ---------- Voice Upload ---------- #
@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files or 'username' not in request.form or 'mode' not in request.form:
        return jsonify(success=False, error="Invalid request")

    username = request.form['username']
    mode = request.form['mode']
    audio_file = request.files['audio']

    try:
        temp_webm_path = f"temp_{username}_{mode}.webm"
        with open(temp_webm_path, 'wb') as f:
            f.write(audio_file.read())

        time.sleep(0.2)

        temp_wav_path = f"temp_{username}_{mode}.wav"
        sound = AudioSegment.from_file(temp_webm_path, format='webm')
        sound.export(temp_wav_path, format='wav')

        save_path = f'static/voices/{username}_{mode}.wav'
        sound.export(save_path, format='wav')

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio = recognizer.record(source)
            try:
                voice_text = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                voice_text = "Unclear"
            except sr.RequestError:
                voice_text = "Error"

        for f in [temp_webm_path, temp_wav_path]:
            try:
                os.remove(f)
            except PermissionError as e:
                print(f"⚠️ Could not delete temp file (ignored): {e}")

        return jsonify(success=True, voice_text=voice_text)

    except Exception as e:
        print(f"❌ Voice processing error: {e}")
        return jsonify(success=False, error=str(e))

# ---------- Admin ---------- #
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials")
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    cursor = None
    users = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, voice_text FROM users")
        users = cursor.fetchall()
    except Exception as e:
        print(f"❌ Admin dashboard error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template("admin.html", users=users)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ---------- Run Server ---------- #
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)