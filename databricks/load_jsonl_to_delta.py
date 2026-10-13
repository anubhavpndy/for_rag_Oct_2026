# Run in a Databricks Python context where `spark` is available.
# Upload local JSONL outputs to an approved Volume before running this script.
# Development bootstrap only: overwrite mode replaces table contents.
CATALOG, SCHEMA, VOLUME = "upl_kb_dev", "knowledge", "source_files"
base = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/processed"
documents_df = spark.read.json(f"{base}/documents.jsonl")
chunks_df = spark.read.json(f"{base}/document_chunks.jsonl")
documents_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.{SCHEMA}.documents")
chunks_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.{SCHEMA}.document_chunks")
print(f"Loaded {documents_df.count()} documents and {chunks_df.count()} chunks.")
