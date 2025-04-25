#!/bin/bash
# Run the manga connector manager

# Set default values
CONNECTORS_PATH="/data/hakuneko/src/web/mjs/connectors"
DB_HOST="localhost"
DB_PORT=5432
DB_NAME="manga_connectors"
DB_USER="postgres"
DB_PASSWORD="postgres"
THREADS=10
TIMEOUT=15
OUTPUT_FILE="/data/connector_report.txt"

# Run the connector manager
python /data/manga_connector_manager.py \
  --path "$CONNECTORS_PATH" \
  --threads "$THREADS" \
  --timeout "$TIMEOUT" \
  --output "$OUTPUT_FILE" \
  --db-host "$DB_HOST" \
  --db-port "$DB_PORT" \
  --db-name "$DB_NAME" \
  --db-user "$DB_USER" \
  --db-password "$DB_PASSWORD"

echo "Connector manager completed"
