Narrative Gap Detection System

An automated, multi-stream data ingestion engine engineered to extract, clean, and unify structured organization payloads from separate digital environments. The pipeline splits ingestion into tracking internal company web copies (Internal Reality) and founder/company market messaging (External Perception) to construct a consolidated data model for downstream calculation modules.

Project Architecture

narrative-gap-detection-system/
│
├── scrapers/
│   ├── __init__.py
│   ├── website_crawler.py       # Requests/BeautifulSoup4 internal crawler
│   └── linkedin_scraper.py      # Playwright browser-stealth external scraper
│
├── pipeline/
│   ├── __init__.py
│   └── stream_merger.py         # Data unification and schema mapping layer
│
├── data/                        # Local directory for JSON caches (Git ignored)
│   └── .gitkeep
│
├── .gitignore
├── README.md
└── requirements.txt