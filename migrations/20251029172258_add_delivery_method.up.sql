-- Add up migration script here

CREATE TYPE delivery_method AS ENUM ('run_job', 'send_to_mailbox');

ALTER TABLE http_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE websocket_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE kafka_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE nats_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE mqtt_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE sqs_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE postgres_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;
ALTER TABLE gcp_trigger ADD COLUMN delivery_method delivery_method DEFAULT 'run_job' NOT NULL;