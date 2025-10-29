-- Add down migration script here

ALTER TABLE http_trigger DROP COLUMN delivery_method;
ALTER TABLE websocket_trigger DROP COLUMN delivery_method;
ALTER TABLE kafka_trigger DROP COLUMN delivery_method;
ALTER TABLE nats_trigger DROP COLUMN delivery_method;
ALTER TABLE mqtt_trigger DROP COLUMN delivery_method;
ALTER TABLE sqs_trigger DROP COLUMN delivery_method;
ALTER TABLE postgres_trigger DROP COLUMN delivery_method;
ALTER TABLE gcp_trigger DROP COLUMN delivery_method;

DROP TYPE delivery_method;