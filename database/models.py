"""
Database models and schema definitions
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
"""

CREATE_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chunks_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

CREATE_CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    exam_mode TEXT,
    sources TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

CREATE_MCQ_TESTS_TABLE = """
CREATE TABLE IF NOT EXISTS mcq_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    num_questions INTEGER NOT NULL,
    difficulty TEXT NOT NULL,
    score INTEGER,
    total_questions INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

CREATE_MCQ_QUESTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS mcq_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    options_json TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    user_answer TEXT,
    is_correct INTEGER,
    explanation TEXT,
    FOREIGN KEY (test_id) REFERENCES mcq_tests (id) ON DELETE CASCADE
);
"""

CREATE_VIVA_TESTS_TABLE = """
CREATE TABLE IF NOT EXISTS viva_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    num_questions INTEGER NOT NULL,
    difficulty TEXT NOT NULL,
    score INTEGER,
    total_questions INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""

CREATE_VIVA_QUESTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS viva_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    expected_points TEXT,
    user_answer TEXT,
    score INTEGER,
    feedback TEXT,
    FOREIGN KEY (test_id) REFERENCES viva_tests (id) ON DELETE CASCADE
);
"""

# Indexes for better query performance
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);",
    "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_mcq_tests_user_id ON mcq_tests(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_mcq_questions_test_id ON mcq_questions(test_id);",
    "CREATE INDEX IF NOT EXISTS idx_viva_tests_user_id ON viva_tests(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_viva_questions_test_id ON viva_questions(test_id);"
]

ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_DOCUMENTS_TABLE,
    CREATE_CHAT_HISTORY_TABLE,
    CREATE_SESSIONS_TABLE,
    CREATE_MCQ_TESTS_TABLE,
    CREATE_MCQ_QUESTIONS_TABLE,
    CREATE_VIVA_TESTS_TABLE,
    CREATE_VIVA_QUESTIONS_TABLE
]
