## 📂 Repository Structure

The system isolates components cleanly across specialized logical directories to maintain a scalable ingestion architecture:

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
