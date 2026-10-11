"""
Database manager for SQLite operations
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

from database.models import ALL_TABLES, CREATE_INDEXES
from config.settings import DATABASE_PATH


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Initialize database with tables and indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create tables
            for table_sql in ALL_TABLES:
                cursor.execute(table_sql)
            
            # Create indexes
            for index_sql in CREATE_INDEXES:
                cursor.execute(index_sql)
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    # User Management
    def create_user(self, username: str, email: str, password_hash: str) -> Optional[int]:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all users for admin dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, username, email, created_at, last_login, is_active FROM users ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Document Management
    def add_document(self, user_id: int, filename: str, file_path: str, 
                    file_size: int, file_type: str, chunks_count: int = 0) -> Optional[int]:
        """Add a document record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """INSERT INTO documents (user_id, filename, file_path, file_size, file_type, chunks_count)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, filename, file_path, file_size, file_type, chunks_count)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding document: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_documents(self, user_id: int) -> List[Dict]:
        """Get all documents for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM documents WHERE user_id = ? ORDER BY upload_date DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents for admin dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT d.*, u.username 
                   FROM documents d 
                   JOIN users u ON d.user_id = u.id 
                   ORDER BY d.upload_date DESC"""
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete a document"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # Chat History Management
    def add_chat_message(self, user_id: int, question: str, answer: str, 
                        exam_mode: str = None, sources: List[str] = None) -> Optional[int]:
        """Add a chat message to history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        sources_json = json.dumps(sources) if sources else None
        
        try:
            cursor.execute(
                """INSERT INTO chat_history (user_id, question, answer, exam_mode, sources)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, question, answer, exam_mode, sources_json)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding chat message: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_chat_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get chat history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT * FROM chat_history 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
            history = [dict(row) for row in cursor.fetchall()]
            
            # Parse sources JSON
            for item in history:
                if item['sources']:
                    item['sources'] = json.loads(item['sources'])
            
            return history
        finally:
            conn.close()
    
    def get_recent_chat_history(self, user_id: int, limit: int = 10) -> List[Tuple[str, str]]:
        """Get recent chat history as (question, answer) tuples"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT question, answer FROM chat_history 
                   WHERE user_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
            return [(row['question'], row['answer']) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Statistics
    def get_statistics(self) -> Dict:
        """Get system statistics for admin dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']
            
            # Active users (logged in last 7 days)
            cursor.execute(
                """SELECT COUNT(*) as count FROM users 
                   WHERE last_login >= datetime('now', '-7 days')"""
            )
            stats['active_users'] = cursor.fetchone()['count']
            
            # Total documents
            cursor.execute("SELECT COUNT(*) as count FROM documents")
            stats['total_documents'] = cursor.fetchone()['count']
            
            # Total chat messages
            cursor.execute("SELECT COUNT(*) as count FROM chat_history")
            stats['total_chats'] = cursor.fetchone()['count']
            
            # Documents uploaded today
            cursor.execute(
                """SELECT COUNT(*) as count FROM documents 
                   WHERE DATE(upload_date) = DATE('now')"""
            )
            stats['documents_today'] = cursor.fetchone()['count']
            
            # Chats today
            cursor.execute(
                """SELECT COUNT(*) as count FROM chat_history 
                   WHERE DATE(timestamp) = DATE('now')"""
            )
            stats['chats_today'] = cursor.fetchone()['count']
            
            return stats
        finally:
            conn.close()

    
    # MCQ Test Management
    def create_mcq_test(self, user_id: int, filename: str, num_questions: int, 
                       difficulty: str) -> Optional[int]:
        """Create a new MCQ test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO mcq_tests (user_id, filename, num_questions, difficulty, total_questions)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, filename, num_questions, difficulty, num_questions))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating MCQ test: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def save_mcq_question(self, test_id: int, question_number: int, 
                         question_text: str, options_json: str, 
                         correct_answer: str, explanation: str = "") -> bool:
        """Save an MCQ question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO mcq_questions 
                (test_id, question_number, question_text, options_json, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_id, question_number, question_text, options_json, correct_answer, explanation))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving MCQ question: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_user_answer(self, question_id: int, user_answer: str, 
                          is_correct: int) -> bool:
        """Update user's answer for an MCQ question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE mcq_questions 
                SET user_answer = ?, is_correct = ?
                WHERE id = ?
            """, (user_answer, is_correct, question_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating user answer: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def complete_mcq_test(self, test_id: int, score: int) -> bool:
        """Mark test as completed and save score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE mcq_tests 
                SET score = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (score, test_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error completing MCQ test: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_mcq_test(self, test_id: int) -> Optional[Dict]:
        """Get MCQ test by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM mcq_tests WHERE id = ?
            """, (test_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Error getting MCQ test: {e}")
            return None
        finally:
            conn.close()
    
    def get_mcq_questions(self, test_id: int) -> List[Dict]:
        """Get all questions for an MCQ test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM mcq_questions 
                WHERE test_id = ? 
                ORDER BY question_number
            """, (test_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting MCQ questions: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_mcq_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get MCQ test history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM mcq_tests 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting MCQ history: {e}")
            return []
        finally:
            conn.close()


    # Viva Test Management
    def create_viva_test(self, user_id: int, filename: str, num_questions: int, 
                        difficulty: str) -> Optional[int]:
        """Create a new Viva test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO viva_tests (user_id, filename, num_questions, difficulty, total_questions)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, filename, num_questions, difficulty, num_questions))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating Viva test: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def save_viva_question(self, test_id: int, question_number: int, 
                          question_text: str, expected_points: str, 
                          difficulty: str) -> bool:
        """Save a viva question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO viva_questions 
                (test_id, question_number, question_text, expected_points)
                VALUES (?, ?, ?, ?)
            """, (test_id, question_number, question_text, expected_points))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving viva question: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_viva_answer(self, question_id: int, user_answer: str, 
                          score: int, feedback: str) -> bool:
        """Update user's answer for a viva question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE viva_questions 
                SET user_answer = ?, score = ?, feedback = ?
                WHERE id = ?
            """, (user_answer, score, feedback, question_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating viva answer: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def complete_viva_test(self, test_id: int, score: int) -> bool:
        """Mark viva test as completed and save score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE viva_tests 
                SET score = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (score, test_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error completing viva test: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_viva_test(self, test_id: int) -> Optional[Dict]:
        """Get viva test by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM viva_tests WHERE id = ?
            """, (test_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Error getting viva test: {e}")
            return None
        finally:
            conn.close()
    
    def get_viva_questions(self, test_id: int) -> List[Dict]:
        """Get all questions for a viva test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM viva_questions 
                WHERE test_id = ? 
                ORDER BY question_number
            """, (test_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting viva questions: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_viva_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get viva test history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM viva_tests 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting viva history: {e}")
            return []
        finally:
            conn.close()
    
    def get_document_by_filename(self, user_id: int, filename: str) -> Optional[Dict]:
        """Check if document with filename already exists for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM documents WHERE user_id = ? AND filename = ? LIMIT 1",
                (user_id, filename)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    # Written Practice Management
    def create_written_test(self, user_id: int, filename: str, num_questions: int,
                           total_marks: float, difficulty: str) -> Optional[int]:
        """Create a new written practice test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO written_tests (user_id, filename, num_questions, total_marks, difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, filename, num_questions, total_marks, difficulty))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating written test: {e}")
            return None
        finally:
            conn.close()
    
    def save_written_question(self, test_id: int, question_number: int,
                             question_text: str, marks: float,
                             key_points_json: str) -> bool:
        """Save a written question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO written_questions 
                (test_id, question_number, question_text, marks, key_points_json)
                VALUES (?, ?, ?, ?, ?)
            """, (test_id, question_number, question_text, marks, key_points_json))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving written question: {e}")
            return False
        finally:
            conn.close()
    
    def get_written_questions(self, test_id: int) -> List[Dict]:
        """Get all questions for a written test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM written_questions
                WHERE test_id = ?
                ORDER BY question_number
            """, (test_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting written questions: {e}")
            return []
        finally:
            conn.close()
    
    def update_written_answer(self, question_id: int, user_answer: str,
                             score: float, feedback: str) -> bool:
        """Update user answer and score for a written question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE written_questions
                SET user_answer = ?, score = ?, feedback = ?
                WHERE id = ?
            """, (user_answer, score, feedback, question_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating written answer: {e}")
            return False
        finally:
            conn.close()
    
    def complete_written_test(self, test_id: int, total_score: float) -> bool:
        """Mark written test as complete with final score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE written_tests
                SET score = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (total_score, test_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error completing written test: {e}")
            return False
        finally:
            conn.close()
    
    def get_written_test(self, test_id: int) -> Optional[Dict]:
        """Get a specific written test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM written_tests WHERE id = ?", (test_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting written test: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_written_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get written practice history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM written_tests
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting written history: {e}")
            return []
        finally:
            conn.close()
