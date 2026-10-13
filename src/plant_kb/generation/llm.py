import os
SYSTEM_PROMPT = (
 "You are a plant-document retrieval assistant. Answer only from supplied source passages. "
 "Cite factual claims with source labels. If sources do not answer, say so. "
 "Do not invent operating limits, procedure steps, approvals, or safety instructions. "
 "For safety-critical actions, tell the user to verify the current approved procedure."
)
class OpenAICompatibleLLM:
    """Optional adapter; use only an endpoint approved for the data classification."""
    def __init__(self, base_url=None, api_key=None, model=None):
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "")
        if not (self.base_url and self.api_key and self.model):
            raise RuntimeError("Set LLM_BASE_URL, LLM_API_KEY and LLM_MODEL for an approved endpoint.")
    def answer(self, query, passages):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install optional dependency with: pip install openai") from exc
        sources = []
        for i, p in enumerate(passages, 1):
            sources.append(f"[S{i}] file={p.get('filename')} department={p.get('department')} "
                           f"location={p.get('source_location')}\n{p.get('chunk_text', '')}")
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(model=self.model, temperature=0,
            messages=[{"role":"system","content":SYSTEM_PROMPT},
                      {"role":"user","content":f"Question: {query}\n\nSources:\n" + "\n\n".join(sources)}])
        return response.choices[0].message.content or "No answer returned."


def hypothetical_document(self, query):
    # This generated passage is a retrieval aid only, never a source of truth.
    client = __import__("openai").OpenAI(api_key=self.api_key, base_url=self.base_url)
    response = client.chat.completions.create(
        model=self.model, temperature=0,
        messages=[
            {"role": "system", "content": "Write a short hypothetical technical passage that might answer the user's plant-document question. Do not invent precise limits, numeric values, or safety instructions. This text is only for retrieval, not a factual answer."},
            {"role": "user", "content": query}
        ])
    return response.choices[0].message.content or ""
