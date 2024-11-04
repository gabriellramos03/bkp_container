import docker
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKUP_DIR = os.getenv("BACKUP_DIR")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
WORDPRESS_VOLUME = os.getenv("WORDPRESS_VOLUME")
DB_CONTAINER_NAME = os.getenv("DB_CONTAINER_NAME")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", 2))

def log_with_timestamp(message):
    """Imprime uma mensagem com o timestamp atual."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def backup_container():
    client = docker.from_env()
    container = client.containers.get(CONTAINER_NAME)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    container_backup_file = f"{BACKUP_DIR}/wordpress_container_backup_{timestamp}.tar"
    volume_backup_file = f"{BACKUP_DIR}/wordpress_volume_backup_{timestamp}.tar.gz"
    db_backup_file = f"{BACKUP_DIR}/mysql_backup_{timestamp}.sql"

    os.makedirs(BACKUP_DIR, exist_ok=True)

    log_with_timestamp(f"Iniciando backup do container {CONTAINER_NAME}...")
    with open(container_backup_file, 'wb') as f:
        for chunk in container.export():
            f.write(chunk)
    log_with_timestamp(f"Backup do container concluído e salvo em {container_backup_file}")

    log_with_timestamp(f"Iniciando backup do volume {WORDPRESS_VOLUME}...")
    os.system(f"docker run --rm -v {WORDPRESS_VOLUME}:/volume -v {BACKUP_DIR}:/backup alpine sh -c 'tar czf /backup/wordpress_volume_backup_{timestamp}.tar.gz -C /volume .'")
    log_with_timestamp(f"Backup do volume concluído e salvo em {volume_backup_file}")

    manage_backups()

# def backup_database(db_backup_file):  # Comentado para não realizar o backup do banco de dados
#     log_with_timestamp(f"Iniciando backup do banco de dados...")
#     os.system(f"docker exec {DB_CONTAINER_NAME} mysqldump -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} > {db_backup_file}")
#     log_with_timestamp(f"Backup do banco de dados concluído e salvo em {db_backup_file}")

def manage_backups():
    container_backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("wordpress_container_backup") and f.endswith(".tar")]
    )
    if len(container_backups) > MAX_BACKUPS:
        for old_backup in container_backups[:-MAX_BACKUPS]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))
            log_with_timestamp(f"Backup antigo de container removido: {old_backup}")

    volume_backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("wordpress_volume_backup") and f.endswith(".tar.gz")]
    )
    if len(volume_backups) > MAX_BACKUPS:
        for old_backup in volume_backups[:-MAX_BACKUPS]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))
            log_with_timestamp(f"Backup antigo de volume removido: {old_backup}")

    db_backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("mysql_backup") and f.endswith(".sql")]
    )
    if len(db_backups) > MAX_BACKUPS:
        for old_backup in db_backups[:-MAX_BACKUPS]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))
            log_with_timestamp(f"Backup antigo de banco de dados removido: {old_backup}")

if __name__ == "__main__":
    while True:
        backup_container()
        time.sleep(60)
