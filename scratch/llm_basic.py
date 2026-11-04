from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
MODEL = "claude-sonnet-5-5"

def get_text(resp) -> str:
    """Join all text blocks, ignoring thinking and other block types."""
    return "".join(b.text for b in resp.content if b.type == "text")

resp = client.messages.create(
    model=MODEL,
    max_tokens=300,
    system="You are a helpful assistant. Answer in a sentence",
    messages=[{"role": "user", "content": "customers in Canada?"}],
)
print([b.type for b in resp.content])  # shows which block types came back
print(get_text(resp))
print(resp.usage)  # input_tokens, output_tokens