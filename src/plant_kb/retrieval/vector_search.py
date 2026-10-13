import os

class DatabricksVectorSearchRetriever:
    """
    Optional Databricks Vector Search adapter for a Delta Sync index with a configured
    embedding endpoint. Install `databricks-vectorsearch` and set DATABRICKS_HOST,
    DATABRICKS_TOKEN, DATABRICKS_VECTOR_ENDPOINT and DATABRICKS_VECTOR_INDEX.
    """
    def __init__(self, host=None, token=None, endpoint_name=None, index_name=None,
                 columns=None):
        self.host = (host or os.getenv("DATABRICKS_HOST", "")).rstrip("/")
        self.token = token or os.getenv("DATABRICKS_TOKEN", "")
        self.endpoint_name = endpoint_name or os.getenv("DATABRICKS_VECTOR_ENDPOINT", "")
        self.index_name = index_name or os.getenv("DATABRICKS_VECTOR_INDEX", "")
        self.columns = columns or ["chunk_id", "document_id", "filename", "department",
                                   "plant_id", "unit_id", "file_type", "source_uri",
                                   "chunk_text", "content_type", "section_name", "source_location"]
        self._index = None

    @property
    def configured(self):
        return bool(self.host and self.token and self.endpoint_name and self.index_name)

    def _get_index(self):
        if not self.configured:
            raise RuntimeError("Databricks Vector Search environment is not configured.")
        if self._index is None:
            try:
                from databricks.vector_search.client import VectorSearchClient
            except ImportError as exc:
                raise RuntimeError("Install optional dependency: pip install databricks-vectorsearch") from exc
            client = VectorSearchClient(workspace_url=self.host, personal_access_token=self.token)
            self._index = client.get_index(endpoint_name=self.endpoint_name, index_name=self.index_name)
        return self._index

    def search(self, query, top_k=8, filters=None):
        index = self._get_index()
        kwargs = {"query_text": query, "columns": self.columns, "num_results": top_k}
        # Databricks Vector Search filters use filterable column names and supported filter syntax.
        if filters:
            kwargs["filters"] = filters
        response = index.similarity_search(**kwargs)
        data = response.get("result", {}).get("data_array", [])
        manifest = response.get("manifest", {}).get("columns", [])
        names = [c.get("name") for c in manifest] if manifest else []
        rows = []
        for row in data:
            item = dict(zip(names, row)) if names else {}
            item["retrieval_method"] = "vector_search"
            rows.append(item)
        return rows
