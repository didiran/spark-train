#!/bin/bash

echo "Waiting for Kibana..."
until curl -s -f http://localhost:5601/api/status | grep -q '"level":"available"'; do
    sleep 5
    echo -n "."
done
echo " Kibana is ready!"

# Создаем data view если его нет
echo "Checking data view..."
if ! curl -s -X GET "http://localhost:5601/api/data_views" | grep -q "pipeline-logs"; then
    echo "Creating data view..."
    curl -X POST "http://localhost:5601/api/data_views" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -d '{
            "data_view": {
                "title": "pipeline-logs-*",
                "name": "pipeline-logs",
                "timeFieldName": "@timestamp"
            }
        }'
    echo " Data view created!"
else
    echo " Data view already exists"
fi

# Импортируем дашборды
echo "Importing dashboards..."
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
    -H "kbn-xsrf: true" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@/usr/share/kibana/export/dashboards.ndjson" \
    -F "overwrite=true"

echo " Setup complete!"