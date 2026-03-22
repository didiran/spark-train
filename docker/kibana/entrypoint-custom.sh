#!/bin/bash

# Ждем Elasticsearch
echo "Waiting for Elasticsearch..."
until curl -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"green\|yellow"'; do
    sleep 5
done
echo "Elasticsearch is ready!"

# Запускаем Kibana в фоне
/usr/local/bin/kibana-docker &

# Ждем пока Kibana станет доступна
echo "Waiting for Kibana..."
until curl -s http://localhost:5601/api/status | grep -q '"level":"available"'; do
    sleep 5
done
echo "Kibana is ready!"

# Импортируем data view если он еще не создан
echo "Checking if data view exists..."
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
    echo "Data view created!"
else
    echo "Data view already exists"
fi

# Ждем завершения
wait