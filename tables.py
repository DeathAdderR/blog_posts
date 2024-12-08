
import sqlite3

class BlogTable:
    def __init__(self):
        self.connection = sqlite3.connect('blog_table.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._initialize_database()

    def _initialize_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password_hash TEXT NOT NULL,
                            email TEXT UNIQUE)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS blog_posts (
                            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE)''')
        
        self.connection.commit()

    def close_database(self):
        self.connection.close()
        print("...connection to block_table terminated...")

    def execute_query(self, query, data=None):
        try:
            if data:
                self.cursor.execute(query, data)
            else:
                self.cursor.execute(query)
    
            if query.strip().lower().startswith('select'):
                return self.cursor.fetchall()
    
            self.connection.commit()  # Ensure commit is run after insertions
            print('Commit successful!')
    
        except sqlite3.IntegrityError as e:
            print(f"SQL ERROR: IntegrityError: {e}")
        except sqlite3.OperationalError as e:
            print(f"SQL ERROR: OperationalError: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
