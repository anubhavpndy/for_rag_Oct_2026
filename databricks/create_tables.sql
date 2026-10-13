-- Replace example catalog/schema with names approved by your platform team.
CREATE TABLE IF NOT EXISTS upl_kb_dev.knowledge.documents (
  document_id STRING, source_key STRING, filename STRING, relative_path STRING, file_type STRING,
  department STRING, plant_id STRING, unit_id STRING, document_type STRING,
  detected_unit_mentions ARRAY<STRING>, version STRING, approval_status STRING,
  source_uri STRING, status STRING, content_sha256 STRING,
  metadata_warnings ARRAY<STRING>, parser_warnings ARRAY<STRING>, chunk_count BIGINT
) USING DELTA;

CREATE TABLE IF NOT EXISTS upl_kb_dev.knowledge.document_chunks (
  chunk_id STRING, document_id STRING, filename STRING, department STRING,
  plant_id STRING, unit_id STRING, file_type STRING, document_version STRING,
  source_uri STRING, approval_status STRING, chunk_text STRING, content_type STRING, section_name STRING,
  source_location STRUCT<paragraph_number: BIGINT, style: STRING, table_number: BIGINT, row_number: BIGINT, page_number: BIGINT, sheet_name: STRING, detected_header_row: BIGINT>, metadata_warnings ARRAY<STRING>
) USING DELTA;

CREATE TABLE IF NOT EXISTS upl_kb_dev.knowledge.ingestion_runs (
  run_id STRING, started_at TIMESTAMP, completed_at TIMESTAMP, status STRING,
  files_discovered BIGINT, files_processed BIGINT, chunks_created BIGINT,
  error_count BIGINT, report_uri STRING
) USING DELTA;
