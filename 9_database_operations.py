#!/usr/bin/env python3
"""
Database Operations for DevOps - Script 9
Why: Database management is critical for application deployments
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

class DatabaseManager:
    """
    Generic database operations manager
    Why: Centralized database operations with proper error handling
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """
        Initialize database with required tables
        Why: Ensure database schema exists before operations
        """
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS deployments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            conn.commit()  # Save changes to database
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Why: Ensures connections are properly closed even if errors occur
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()  # Always close connection
    
    def record_deployment(self, app_name: str, version: str, environment: str) -> int:
        """
        Record new deployment in database
        Why: Track deployment history for rollbacks and auditing
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO deployments (app_name, version, environment) VALUES (?, ?, ?)',
                (app_name, version, environment)  # Use parameterized queries to prevent SQL injection
            )
            conn.commit()
            return cursor.lastrowid  # Return ID of inserted record
    
    def update_deployment_status(self, deployment_id: int, status: str) -> bool:
        """
        Update deployment status
        Why: Track deployment progress and failures
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                'UPDATE deployments SET status = ? WHERE id = ?',
                (status, deployment_id)
            )
            conn.commit()
            return cursor.rowcount > 0  # Return True if row was updated
    
    def get_deployment_history(self, app_name: str, limit: int = 10) -> List[Dict]:
        """
        Get deployment history for application
        Why: View deployment timeline for troubleshooting
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM deployments WHERE app_name = ? ORDER BY deployed_at DESC LIMIT ?',
                (app_name, limit)
            )
            return [dict(row) for row in cursor.fetchall()]  # Convert rows to dictionaries

def backup_database(source_db: str, backup_path: str) -> bool:
    """
    Create database backup
    Why: Protect against data loss during maintenance
    """
    try:
        import shutil
        shutil.copy2(source_db, backup_path)  # Copy with metadata
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def migrate_database_schema(db_path: str, migrations: List[str]) -> bool:
    """
    Apply database schema migrations
    Why: Update database structure during deployments
    """
    try:
        with sqlite3.connect(db_path) as conn:
            # Create migrations table if it doesn't exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Get applied migrations
            cursor = conn.execute('SELECT version FROM schema_migrations')
            applied = {row[0] for row in cursor.fetchall()}
            
            # Apply new migrations
            for i, migration_sql in enumerate(migrations):
                version = i + 1
                if version not in applied:
                    conn.execute(migration_sql)  # Execute migration
                    conn.execute(
                        'INSERT INTO schema_migrations (version) VALUES (?)',
                        (version,)
                    )
                    print(f"Applied migration {version}")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

def export_data_to_json(db_path: str, table_name: str, output_file: str) -> bool:
    """
    Export database table to JSON
    Why: Create data backups or transfer data between environments
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.execute(f'SELECT * FROM {table_name}')
            
            data = [dict(row) for row in cursor.fetchall()]
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)  # default=str handles datetime objects
            
            return True
            
    except Exception as e:
        print(f"Export failed: {e}")
        return False

def check_database_health(db_path: str) -> Dict:
    """
    Check database health and statistics
    Why: Monitor database performance and detect issues
    """
    try:
        with sqlite3.connect(db_path) as conn:
            # Get database size
            cursor = conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            
            # Get table count
            cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Test write operation
            start_time = time.time()
            conn.execute("CREATE TEMP TABLE test_write (id INTEGER)")
            conn.execute("DROP TABLE test_write")
            write_time = time.time() - start_time
            
            return {
                'healthy': True,
                'size_bytes': db_size,
                'table_count': table_count,
                'write_test_time': write_time
            }
            
    except Exception as e:
        return {
            'healthy': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Example usage
    db_manager = DatabaseManager('/tmp/devops.db')
    
    # Record a deployment
    deployment_id = db_manager.record_deployment('web-app', 'v1.2.3', 'production')
    print(f"Recorded deployment: {deployment_id}")
    
    # Update status
    db_manager.update_deployment_status(deployment_id, 'success')
    
    # Get history
    history = db_manager.get_deployment_history('web-app')
    print(f"Deployment history: {len(history)} records")
    
    print("Database operations script ready!")