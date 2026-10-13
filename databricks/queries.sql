SELECT document_id, filename, department, source_uri, source_location, chunk_text
FROM upl_kb_dev.knowledge.document_chunks
WHERE lower(chunk_text) LIKE lower('%pressure%')
LIMIT 20;

SELECT department, file_type, count(*) AS document_count
FROM upl_kb_dev.knowledge.documents
GROUP BY department, file_type
ORDER BY department, file_type;
