-- Add down migration script here

ALTER TABLE http_trigger DROP COLUMN action_to_take;
ALTER TABLE mqtt_trigger DROP COLUMN action_to_take;
ALTER TABLE gcp_trigger DROP COLUMN action_to_take;
ALTER TABLE kafka_trigger DROP COLUMN action_to_take;
ALTER TABLE sqs_trigger DROP COLUMN action_to_take;
ALTER TABLE postgres_trigger DROP COLUMN action_to_take;
ALTER TABLE websocket_trigger DROP COLUMN action_to_take;
ALTER TABLE nats_trigger DROP COLUMN action_to_take;

DROP TYPE ACTION_TO_TAKE;