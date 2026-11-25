from flask import Flask, request, render_template, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "snippets.db"

# --- 1. NORMALIZED RELATIONAL DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Parent Table: Programming Languages (Primary Key: lang_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS languages (
            lang_id TEXT PRIMARY KEY,
            lang_name TEXT NOT NULL,
            use_case TEXT NOT NULL
        )
    ''')
    
    # Child Table: Code Snippets (Foreign Key: lang_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            snippet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            lang_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            code_body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (lang_id) REFERENCES languages (lang_id)
        )
    ''')
    
    # Seed supported languages
    cursor.execute("SELECT COUNT(*) FROM languages")
    if cursor.fetchone()[0] == 0:
        langs = [
            ("cpp", "C++", "DSA & Game Engine Logic"),
            ("python", "Python", "Backend & AI Scripting"),
            ("csharp", "C#", "Unity Gameplay Mechanics"),
            ("sql", "SQL", "Relational Queries & Analytics"),
            ("js", "JavaScript", "Frontend DOM & Fetch API")
        ]
        cursor.executemany("INSERT INTO languages VALUES (?, ?, ?)", langs)

    # Seed 3 starter snippets so the dashboard is populated on first launch
    cursor.execute("SELECT COUNT(*) FROM snippets")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d")
        starter_snippets = [
            (
                "Binary Search (Iterative)",
                "cpp",
                "DSA",
                "int binarySearch(vector<int>& arr, int target) {\n    int low = 0, high = arr.size() - 1;\n    while (low <= high) {\n        int mid = low + (high - low) / 2;\n        if (arr[mid] == target) return mid;\n        else if (arr[mid] < target) low = mid + 1;\n        else high = mid - 1;\n    }\n    return -1;\n}",
                now
            ),
            (
                "Department Employee Count",
                "sql",
                "DBMS Interview",
                "SELECT d.dept_name, COUNT(e.emp_id) AS total_staff\nFROM departments d\nLEFT JOIN employees e ON d.dept_id = e.dept_id\nGROUP BY d.dept_id, d.dept_name;",
                now
            ),
            (
                "2D Rigidbody Jump Physics",
                "csharp",
                "Unity 2D",
                "void Update() {\n    if (Input.GetKeyDown(KeyCode.Space) && isGrounded) {\n        rb.velocity = new Vector2(rb.velocity.x, jumpForce);\n    }\n}",
                now
            )
        ]
        cursor.executemany(
            "INSERT INTO snippets (title, lang_id, tag, code_body, created_at) VALUES (?, ?, ?, ?, ?)",
            starter_snippets
        )
        
    conn.commit()
    conn.close()

# --- 2. REST API ROUTES (FULL CRUD) ---
@app.route('/')
def home():
    return render_template('index.html')

# CREATE: Save a new snippet
@app.route('/api/snippets', methods=['POST'])
def add_snippet():
    data = request.get_json()
    title = data.get('title', '').strip()
    lang_id = data.get('lang_id', 'python')
    tag = data.get('tag', 'General').strip()
    code_body = data.get('code_body', '').strip()

    if not title or not code_body:
        return jsonify({"error": "Title and Code are required."}), 400

    now = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO snippets (title, lang_id, tag, code_body, created_at) VALUES (?, ?, ?, ?, ?)",
        (title, lang_id, tag, code_body, now)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Snippet saved successfully"})

# READ + SEARCH + AGGREGATE: Fetch language stats and filtered snippets
@app.route('/api/snippets', methods=['GET'])
def get_snippets():
    search_query = request.args.get('q', '').strip()
    lang_filter = request.args.get('lang', 'all').strip()

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query 1: LEFT JOIN + GROUP BY to count snippets per language
    cursor.execute('''
        SELECT l.lang_id, l.lang_name, COUNT(s.snippet_id) AS snippet_count
        FROM languages l
        LEFT JOIN snippets s ON l.lang_id = s.lang_id
        GROUP BY l.lang_id, l.lang_name
    ''')
    stats = [dict(row) for row in cursor.fetchall()]

    # Query 2: INNER JOIN + LIKE search filter
    sql = '''
        SELECT s.snippet_id, s.title, l.lang_name, s.tag, s.code_body, s.created_at
        FROM snippets s
        INNER JOIN languages l ON s.lang_id = l.lang_id
        WHERE (s.title LIKE ? OR s.tag LIKE ? OR s.code_body LIKE ?)
    '''
    like_pattern = f"%{search_query}%"
    params = [like_pattern, like_pattern, like_pattern]

    if lang_filter != 'all':
        sql += " AND s.lang_id = ?"
        params.append(lang_filter)

    sql += " ORDER BY s.snippet_id DESC"
    cursor.execute(sql, params)
    snippets = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify({"stats": stats, "snippets": snippets})

# DELETE: Remove a snippet by ID
@app.route('/api/snippets/<int:snippet_id>', methods=['DELETE'])
def delete_snippet(snippet_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM snippets WHERE snippet_id = ?", (snippet_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Snippet deleted"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)