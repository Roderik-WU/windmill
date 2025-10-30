-- Add up migration script here
CREATE TYPE ACTION_TO_TAKE AS ENUM('run_job', 'send_to_mailbox');


ALTER TABLE http_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE mqtt_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE gcp_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE kafka_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE sqs_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE postgres_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE websocket_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
ALTER TABLE nats_trigger ADD COLUMN action_to_take ACTION_TO_TAKE DEFAULT 'run_job'::ACTION_TO_TAKE NOT NULL;
