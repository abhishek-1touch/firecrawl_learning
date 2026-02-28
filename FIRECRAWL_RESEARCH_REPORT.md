# Firecrawl Research & POC Report

**Author:** Abhishek Kumar  
**Role:** Software Engineer (3+ years exp)  
**Date:** February 2026  
**Scope:** Basic learning modules 01–11, proof-of-concept validation, multi-site testing

---

## 1. Executive Summary

This report documents a hands-on evaluation of Firecrawl as a web scraping and data extraction platform. Over the course of this POC, I ran 11 basic learning scripts (01–11), tested against 4+ websites, and combined Firecrawl with an LLM to produce structured summaries. The goal was to assess whether Firecrawl is suitable for production use in content pipelines, research automation, and LLM-ready data preparation.

**Bottom line:** Firecrawl delivers on its promise. It handles JS-heavy sites, returns clean markdown, supports structured extraction via schemas, and integrates well with search and crawl workflows. The main tradeoff is cost (credit-based) and API rate limits for high-volume use.

---

## 2. What is Firecrawl?

Firecrawl is a hosted API that turns web pages into structured data. Instead of running your own headless browser or writing custom parsers, you send a URL and get back markdown, HTML, links, images, and optionally AI-extracted JSON.

**Core value:**
- Converts any URL → clean markdown (ideal for RAG, fine-tuning, summarization)
- Handles dynamic content (SPAs, JS-rendered pages)
- Supports crawling (multi-page), search (web search + scrape), and extraction (LLM + schema)
- Manages proxies, caching, and anti-bot handling

**Pricing model:** Credit-based. 1 credit per scrape; extras for JSON extraction, PDF parsing, enhanced proxy.

**Dashboard:** firecrawl.dev — API key, usage, credits, job status.

---

## 3. POC Overview: Files 01–11

| File | Purpose | What I Tested |
|-----|---------|---------------|
| **01_sync_scraper.py** | Single URL scrape, all formats | labenditaec.com — markdown, html, rawHtml, links, images |
| **02_async_scraper.py** | Batch scrape, async + polling | docs.firecrawl.dev |
| **03_scrape_with_params.py** | JSON extraction with Pydantic schema | vercel.com/docs — company info (SSO, pricing, etc.) |
| **04_crawl.py** | Full site crawl, sync | docs.crewai.com (limit 10) |
| **05_async_crawl.py** | Async crawl + status polling | docs.crewai.com (limit 5) |
| **06_llmstext.py** | Generate llms.txt for a site | docs.crewai.com |
| **07_map.py** | Discover all URLs on a site | docs.crewai.com |
| **08_extract.py** | Multi-URL extract + LLM summary | CrewAI Weaviate/Qdrant docs → GPT-4 summary |
| **09_extract_async.py** | Async extract job | firecrawl.dev, docs.firecrawl.dev |
| **10_search.py** | Web search + scrape results | "context engineering" (5 results, last 24h) |
| **11_fire_agent.py** | Agent-based scrape (FIRE-1) | crewai.com, crewai.dev, ycombinator companies |

---

## 4. Architecture: How Firecrawl Fits In

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR APPLICATION                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    firecrawl-py (Python SDK)                      │
│  scrape() | crawl() | search() | extract() | map() | agent()      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Firecrawl API (api.firecrawl.dev)               │
│  /v2/scrape | /v2/crawl | /v2/search | /v2/extract | ...         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │  Scraper  │   │  Crawler   │   │  LLM      │
            │  (Puppeteer│   │  (BFS/DFS) │   │  Extract  │
            │  /Playwright)│   │            │   │  (OpenAI) │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                            Target Websites
```

**Flow:**
1. App calls Firecrawl SDK with URL(s) and options.
2. Firecrawl runs browser/crawler on their infra.
3. Response: Document (markdown, html, metadata, links, images).
4. Optional: Extract with schema → structured JSON.
5. Optional: Pass to your LLM for summarization or RAG.

---

## 5. Websites Tested & Data Captured

### 5.1 labenditaec.com (01_sync_scraper)

- **Type:** News/sports site (Ecuadorian football)
- **Output:** 47 links, 34 images, full markdown, metadata (title, description, og_*, twitter_*, etc.)
- **Credits:** 1
- **Notes:** JS-heavy; Firecrawl handled it. Some iframes/ads blocked by extension in raw HTML, but main content was clean.

### 5.2 vercel.com/docs (03_scrape_with_params)

- **Type:** Docs site
- **Output:** JSON via Pydantic schema — company_name, is_open_source, supports_sso, has_enterprise_plan, contact_email, documentation_url, pricing_url, popular_frameworks, etc.
- **Notes:** Schema-based extraction works well for structured product info.

### 5.3 docs.crewai.com (04, 05, 06, 07, 08)

- **Crawl (04):** 10 pages, markdown + html → `crawl_result.json`
- **Async crawl (05):** 5 pages, `onlyMainContent=True`
- **llms.txt (06):** Full-text site representation for LLMs
- **Map (07):** URL discovery, subdomains
- **Extract (08):** Weaviate + Qdrant tool docs → GPT-4 ordered summary → `summary.md`

### 5.4 docs.firecrawl.dev, firecrawl.dev (02, 09)

- **Batch scrape (02):** docs.firecrawl.dev
- **Async extract (09):** Company mission + features from firecrawl.dev and docs

### 5.5 Web search (10)

- **Query:** "context engineering"
- **Limit:** 5, `tbs="qdr:d"` (last 24h)
- **Output:** Title, URL, description, markdown snippet, links per result

### 5.6 Agent scrape (11)

- **Sites:** crewai.com, crewai.dev, ycombinator.com/companies
- **Agent:** FIRE-1, prompt to navigate product listings
- **Notes:** Agent can click, scroll, wait — useful for pagination and dynamic UIs.

---

## 6. Dashboard & Scraped Data

From the Firecrawl dashboard (firecrawl.dev):

- **API key** — used in `.env` as `FIRECRAWL_API_KEY`
- **Credits** — consumed per scrape (1 base + extras for JSON, PDF, etc.)
- **Jobs** — async crawl/extract/batch status
- **Usage** — request counts, errors

**Sample output structure (scrape_output.json from 01):**

```json
{
  "url": "https://labenditaec.com/",
  "metadata": {
    "title": "Labendita - El Hub del Fútbol Ecuatoriano",
    "description": "...",
    "language": "es, es",
    "keywords": "fútbol ecuatoriano, Liga Pro, ...",
    "og_title": "...",
    "og_image": "...",
    "status_code": 200,
    "credits_used": 1
  },
  "markdown": "...",
  "links": ["...", "..."],
  "images": ["...", "..."]
}
```

---

## 7. LLM Integration (08_extract + summary.md)

**Pipeline:**
1. Firecrawl `extract()` on 2 CrewAI docs URLs (Weaviate + Qdrant tools).
2. Prompt: "Get information and code examples from the provided URLs."
3. Schema: `ExtractList` with `information` and `code_example` per item.
4. Raw extract passed to OpenAI GPT-4.
5. GPT-4 prompt: "Order and summarize as markdown, include code examples."
6. Output: `summary.md` — installation, setup, usage, parameters, examples.

**Result:** A single markdown doc combining both tools, ready for internal docs or RAG.

---

## 8. Key Learnings

| Area | Finding |
|------|---------|
| **Sync vs async** | Sync is fine for 1–2 URLs. For batches or crawls, use async + polling. |
| **Formats** | markdown + links + images cover most use cases. rawHtml when you need exact DOM. |
| **JSON extraction** | Pydantic schema + `json_options` works well. Costs more credits. |
| **Crawl limits** | `limit` param controls page count. `onlyMainContent` reduces noise. |
| **Search** | Good for "find then scrape" flows. `tbs` for recency. |
| **Agent** | FIRE-1 agent handles clicks/scroll. Useful for paginated or interactive pages. |
| **llms.txt** | Standard format for LLM consumption. Good for site-level ingestion. |
| **Map** | Fast way to get all URLs before crawling. |

---

## 9. What Works Well

- **Reliability:** Handles JS-heavy sites without custom setup.
- **Output quality:** Markdown is clean and usable for RAG.
- **Schema extraction:** Pydantic + JSON mode gives predictable structured data.
- **Search + scrape:** Single call to search and get content.
- **Python SDK:** Simple API, good for quick scripts and production pipelines.

---

## 10. Limitations & Considerations

- **Cost:** Credit-based; high volume can get expensive.
- **Rate limits:** Need to respect API limits for large crawls.
- **Agent:** FIRE-1 is powerful but slower and more expensive than plain scrape.
- **API versioning:** v1 (`scrape_url`, `crawl_url`) vs v2 (`scrape`, `crawl`) — SDK abstracts some of this but worth noting.

---

## 11. Conclusion

Firecrawl is a solid choice for teams that need:

- Fast prototyping of scraping pipelines
- LLM-ready content (markdown, llms.txt)
- Structured extraction without building custom parsers
- Search + scrape in one step

The 01–11 scripts cover the main capabilities: single scrape, batch, crawl, map, extract, search, and agent. Combining extract with an LLM (as in 08) shows a practical pattern for research and documentation automation.

**Recommendation:** Use Firecrawl for internal tools, research pipelines, and content ingestion. For very high volume or cost-sensitive workloads, evaluate self-hosted alternatives (Playwright, Crawl4AI) alongside Firecrawl.

---

## Appendix A: File Summary

| File | Main API | Output |
|------|----------|--------|
| 01 | `app.scrape()` | Console + scrape_output.json |
| 02 | `app.async_batch_scrape_urls()` + `check_batch_scrape_status()` | Markdown from first result |
| 03 | `app.scrape_url()` + JsonConfig | `llm_extraction_result.json` |
| 04 | `app.crawl_url()` | crawl_result.json |
| 05 | `app.async_crawl_url()` + `check_crawl_status()` | JSON dump |
| 06 | `app.generate_llms_text()` | llms.txt content |
| 07 | `app.map_url()` | Links list |
| 08 | `app.extract()` + OpenAI | summary.md |
| 09 | `app.async_extract()` + `get_extract_status()` | `job_status.data` |
| 10 | `app.search()` | Search results |
| 11 | `app.batch_scrape_urls()` + AgentOptions | Scraped docs |

---

## Appendix B: Environment Setup

```bash
cd firecrawl_learning
python3 -m venv venv
source venv/bin/activate
pip install firecrawl-py python-dotenv
```

`.env`:
```
FIRECRAWL_API_KEY=fc-your-key
OPENAI_API_KEY=sk-your-key   # For 08_extract
```

---

*Report generated from hands-on POC. All code and outputs are in this repository.*
