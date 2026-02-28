"""
01. Synchronous Scraper - Get ALL data from a URL using Firecrawl.
Fetches markdown, HTML, raw HTML, links, images, and full metadata.
"""

from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import json
from typing import Any

load_dotenv()

# Validate API key
api_key = os.getenv("FIRECRAWL_API_KEY")
if not api_key:
    raise ValueError("FIRECRAWL_API_KEY not found in .env. Add your API key from firecrawl.dev")

app = FirecrawlApp(api_key=api_key)

# URL to scrape
TARGET_URL = "https://labenditaec.com/"

# Scrape with all content formats (v2 API uses scrape(), not scrape_url)
scrape_result = app.scrape(
    TARGET_URL,
    formats=["markdown", "html", "rawHtml", "links", "images"],
)

# --- Safe access helpers ---
def safe_slice(text: str | None, max_len: int = 500) -> str:
    """Safely slice text, handle None."""
    if not text:
        return "(no content)"
    return text[:max_len] + ("..." if len(text) > max_len else "")


# --- Print all metadata ---
metadata = scrape_result.metadata if hasattr(scrape_result, "metadata") else None
meta_dict: dict[str, Any] = {}
if metadata:
    if hasattr(metadata, "model_dump"):
        meta_dict = metadata.model_dump(exclude_none=True)
    elif isinstance(metadata, dict):
        meta_dict = {k: v for k, v in metadata.items() if v is not None}
    else:
        meta_dict = dict(metadata) if metadata else {}

if meta_dict:
    print("=" * 60)
    print("METADATA")
    print("=" * 60)
    for key, value in meta_dict.items():
        if value is not None and str(value).strip():
            print(f"  {key}: {value}")
else:
    print("Metadata: (none)")

# --- Print content summaries ---
print("\n" + "=" * 60)
print("CONTENT")
print("=" * 60)

print("\n--- Markdown (first 800 chars) ---")
markdown = getattr(scrape_result, "markdown", None)
print(safe_slice(markdown, 800))

print("\n--- HTML (first 500 chars) ---")
html = getattr(scrape_result, "html", None)
print(safe_slice(html, 500))

print("\n--- Raw HTML (first 500 chars) ---")
raw_html = getattr(scrape_result, "rawHtml", None) or getattr(scrape_result, "raw_html", None)
print(safe_slice(raw_html, 500))

# --- Links ---
links = getattr(scrape_result, "links", None)
if links and isinstance(links, list):
    print(f"\n--- Links ({len(links)} found) ---")
    for i, link in enumerate(links[:20], 1):  # Show first 20
        print(f"  {i}. {link}")
    if len(links) > 20:
        print(f"  ... and {len(links) - 20} more")
else:
    print("\n--- Links: (none) ---")

# --- Images ---
images = getattr(scrape_result, "images", None)
if images and isinstance(images, list):
    print(f"\n--- Images ({len(images)} found) ---")
    for i, img in enumerate(images[:15], 1):
        print(f"  {i}. {img}")
    if len(images) > 15:
        print(f"  ... and {len(images) - 15} more")
else:
    print("\n--- Images: (none) ---")

# --- Credits used ---
credits = meta_dict.get("creditsUsed", meta_dict.get("credits_used", "N/A")) if meta_dict else "N/A"
print("\n" + "=" * 60)
print(f"Credits used: {credits}")
print("=" * 60)

# --- Save full data to JSON file ---
output_file = "scrape_output.json"
output = {
    "url": TARGET_URL,
    "metadata": meta_dict,
    "markdown": markdown,
    "html": html[:5000] if html else None,  # Truncate HTML for JSON
    "rawHtml": (raw_html or "")[:5000] if raw_html else None,
    "links": links or [],
    "images": images or [],
    "creditsUsed": credits,
}
# Ensure JSON-serializable
def make_serializable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    if hasattr(obj, "model_dump"):
        return make_serializable(obj.model_dump())
    return obj

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(make_serializable(output), f, indent=2, ensure_ascii=False)

print(f"\nFull output saved to: {output_file}")
