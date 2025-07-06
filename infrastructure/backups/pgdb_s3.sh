#!/bin/bash

set -o allexport
source /var/www/ai_python_interviewer/.env
set +o allexport

set -e

CONTAINER_NAME="pgdb"
BACKUP_DATE=$(date +%Y-%m-%d)
BACKUP_FILENAME="$BACKUP_DATE.dump"
CONTAINER_BACKUP_PATH="/var/lib/postgresql/data/$BACKUP_FILENAME"
HOST_CONTAINER_VOLUME_PATH="/var/lib/docker/volumes/ai_python_interviewer_pgdata/_data/$BACKUP_FILENAME"
TMP_PATH="/tmp/$BACKUP_FILENAME"
S3_BUCKET_PATH="s3://ai-python-interviewer/pgdb_backups/"
NOW=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$NOW] Creating database backup.."
docker exec -e POSTGRES_PASSWORD="$DB_PASSWORD" "$CONTAINER_NAME" \
  pg_dump -U "$DB_USER" -d "$DB_NAME" \
  -Fc --no-owner --no-acl \
  -f "$CONTAINER_BACKUP_PATH"

echo "[$NOW] Move dump to temporary dir.."
sudo mv "$HOST_CONTAINER_VOLUME_PATH" "$TMP_PATH"

echo "[$NOW] Loading dump to s3-bucket.."
aws s3 --endpoint-url=https://storage.yandexcloud.net cp "$TMP_PATH" "$S3_BUCKET_PATH"

echo "[$NOW] Removing dump from temporary dir.."
sudo rm -rf "$TMP_PATH"

echo "[$NOW] ✅ Бэкап завершён успешно: $S3_BUCKET_PATH$BACKUP_FILENAME"
