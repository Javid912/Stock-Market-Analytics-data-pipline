import os
import subprocess
from datetime import datetime

def create_backup():
    """Create a backup of the PostgreSQL database"""
    try:
        # Get environment variables
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        db_name = os.getenv('POSTGRES_DB', 'postgres')
        db_host = os.getenv('POSTGRES_HOST', 'postgres')
        
        # Create backup directory if it doesn't exist
        backup_dir = '/opt/airflow/backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/backup_{timestamp}.sql"
        
        # Set PGPASSWORD environment variable
        os.environ['PGPASSWORD'] = db_password
        
        # Execute pg_dump command
        command = [
            'pg_dump',
            '-h', db_host,
            '-U', db_user,
            '-d', db_name,
            '-f', backup_file
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Backup created successfully: {backup_file}")
            return True
        else:
            print(f"Backup failed: {result.stderr}")
            raise Exception(f"Backup failed: {result.stderr}")
            
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        raise
    finally:
        # Clear PGPASSWORD environment variable
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD'] 