import os
import subprocess
from datetime import datetime
from pathlib import Path

def create_backup():
    # Get environment variables
    db_user = os.getenv('POSTGRES_USER')
    db_name = os.getenv('POSTGRES_DB')
    
    # Create backup directory if it doesn't exist
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'backup_{timestamp}.sql'
    
    # Create backup using pg_dump
    cmd = f'docker-compose exec postgres pg_dump -U {db_user} {db_name} > {backup_file}'
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f'Backup created successfully: {backup_file}')
    except subprocess.CalledProcessError as e:
        print(f'Backup failed: {e}')

if __name__ == '__main__':
    create_backup()