-- init-db/01-init.sql
-- Автоматическое создание таблиц при первом запуске PostgreSQL

-- Создание таблицы для метаданных пайплайна
CREATE TABLE IF NOT EXISTS pipeline_metadata (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100),
    run_id VARCHAR(100),
    status VARCHAR(50),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы для метрик моделей
CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    run_id VARCHAR(100),
    metric_name VARCHAR(50),
    metric_value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы для истории фич
CREATE TABLE IF NOT EXISTS feature_history (
    id SERIAL PRIMARY KEY,
    feature_group VARCHAR(100),
    version INT,
    row_count INT,
    column_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_pipeline_metadata_run_id ON pipeline_metadata(run_id);
CREATE INDEX IF NOT EXISTS idx_model_metrics_model_name ON model_metrics(model_name);
CREATE INDEX IF NOT EXISTS idx_feature_history_feature_group ON feature_history(feature_group);

-- Вывод сообщения об успешной инициализации
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
END $$;