import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKUP_DIR_DB = os.getenv("BACKUP_DIR_DB")
EXTERNAL_DB_HOST = os.getenv("EXTERNAL_DB_HOST")
EXTERNAL_DB_NAME = os.getenv("EXTERNAL_DB_NAME")
EXTERNAL_DB_USER = os.getenv("EXTERNAL_DB_USER")
EXTERNAL_DB_PASSWORD = os.getenv("EXTERNAL_DB_PASSWORD")
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", 2))

def log_with_timestamp(message):
    """Imprime uma mensagem com o timestamp atual."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def backup_external_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_backup_file = f"{BACKUP_DIR_DB}/external_postgres_backup_{timestamp}.sql"

    os.makedirs(BACKUP_DIR_DB, exist_ok=True)

    log_with_timestamp(f"Iniciando backup do banco de dados externo...")
    
    result = os.system(f"PGPASSWORD={EXTERNAL_DB_PASSWORD} pg_dump -h {EXTERNAL_DB_HOST} -U {EXTERNAL_DB_USER} {EXTERNAL_DB_NAME} > {db_backup_file} 2> {db_backup_file}.err")

    if result == 0:
        log_with_timestamp(f"Backup do banco de dados externo concluído e salvo em {db_backup_file}")
        os.remove(f"{db_backup_file}.err")
    else:
        log_with_timestamp(f"Falha ao realizar o backup do banco de dados. Veja o arquivo de erro: {db_backup_file}.err")

    manage_backups()

def manage_backups():
    db_backups = sorted(
        [f for f in os.listdir(BACKUP_DIR_DB) if f.startswith("external_postgres_backup") and f.endswith(".sql")]
    )
    if len(db_backups) > MAX_BACKUPS:
        for old_backup in db_backups[:-MAX_BACKUPS]:
            os.remove(os.path.join(BACKUP_DIR_DB, old_backup))
            log_with_timestamp(f"Backup antigo de banco de dados removido: {old_backup}")

if __name__ == "__main__":
    while True:
        backup_external_database()
        time.sleep(60)
