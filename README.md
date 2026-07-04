# Narrative Gap Detection System

An automated, asynchronous multi-stream data ingestion engine engineered to extract, clean, and unify data assets from distributed digital environments. The pipeline segments data collection into internal operational copies (Internal Reality) and external market messaging (External Perception) to construct a consolidated, schema-validated contract for downstream analysis and scoring modules.

---

## 🏗️ Architectural Overview

The system isolates data collection concerns to prevent execution bottlenecks and avoid platform firewalls, managing data lifecycle across three distinct operational zones:

1. **Ingestion Zone:** Employs a dual-track approach. Track A uses an automated breadth-first crawler built on `Requests` and `BeautifulSoup4` to map internal domain spaces up to a 15-page threshold while stripping HTML formatting noise. Track B leverages `Playwright` to launch authenticated, human-mimicking browser sessions that bypass security checkpoints to capture timeline updates.
2. **Storage Zone:** Persists raw extraction files locally within an isolated `data/` workspace, decoupling the network-heavy extraction layer from runtime dependencies.
3. **Unification Zone:** Executes a stream-merging pipeline utility that programmatically reconciles separate data payloads, enforcing consistent keys and schema boundaries before exporting the production-ready master dataset.

---

## 📂 Repository Structure

```text
narrative-gap-detection-system/
│
├── scrapers/
│   ├── __init__.py          # Packages ingestion modules for clean imports
│   ├── website_crawler.py   # Internal Reality crawling engine (BS4)
│   └── linkedin_scraper.py  # External Perception stealth scraper (Playwright)
│
├── pipeline/
│   ├── __init__.py          # Exposes core pipeline utilities
│   └── stream_merger.py     # Multi-stream data unification layer
│
├── data/                    # Local JSON data cache directory (Git Ignored)
│   └── .gitkeep
│
├── .gitignore               # Prevents tracking cache data and local credentials
├── README.md                # System documentation and deployment guide
└── requirements.txt         # Production dependency manifest


## 🚀 Deployment & Execution Guide

### 1. Environment Initialization
Clone the repository and install the framework dependencies:
```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/narrative-gap-detection-system.git](https://github.com/YOUR_GITHUB_USERNAME/narrative-gap-detection-system.git)
cd narrative-gap-detection-system
pip install -r requirements.txt
playwright install chromium
