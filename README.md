
# 🏥 Medical Telegram Data Warehouse

A scalable **data engineering & analytics pipeline** designed to extract, transform, enrich, and serve medical business data from Telegram channels using **asynchronous scraping**, **YOLOv8 computer vision**, a **dbt-powered PostgreSQL warehouse**, **FastAPI**, and **Dagster orchestration**.

---

## 📂 Project Structure

```text
medical-telegram-warehouse/
├── data/
│   └── raw/
│       ├── telegram_messages/   # JSON partitions (YYYY-MM-DD/channel.json)
│       └── images/              # Organized images (channel/msg_id.jpg)
├── medical_warehouse/           # dbt project
│   ├── models/
│   │   ├── staging/             # Task 2: Data cleaning & casting
│   │   └── marts/               # Task 2 & 3: Star schema & AI marts
│   ├── tests/                   # dbt data quality tests
│   └── dbt_project.yml
├── src/
│   ├── scraper.py               # Task 1: Async Telegram scraper
│   ├── to_postgres.py           # Task 2: Load JSON/CSV into PostgreSQL
│   └── yolo_detect.py           # Task 3: YOLOv8 object detection
├── api/                         # Task 4: FastAPI application
│   ├── main.py                  # API routes
│   ├── database.py              # SQLAlchemy engine/session
│   └── schemas.py               # Pydantic models
├── orchestration/               # Task 5: Dagster pipeline
│   └── pipeline.py              # Dagster jobs & schedules
├── logs/                        # Scraper & pipeline logs
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🛰️ Task 1: Data Scraping & Collection (Extract)

A robust extraction layer for high-volume Telegram channels.

### 1️⃣ Asynchronous MTProto Scraper

* Built with **Telethon** (MTProto protocol)
* Uses **asyncio** for concurrent message + media downloads
* Handles `FloodWaitError` gracefully to avoid bans

### 2️⃣ Bronze Data Lake (Raw Layer)

* Raw data preserved to avoid early data loss
* **Hive-style partitioning**:

  ```
  data/raw/telegram_messages/YYYY-MM-DD/channel_name.json
  ```
* Images stored separately using message IDs for CV processing

---

## 🏗️ Task 2: Data Modeling & Transformation (Transform)

Raw Telegram data is transformed into a clean **Star Schema** using **dbt + PostgreSQL**.

### 1️⃣ Staging Layer (`stg_telegram_messages`)

* Casts ISO timestamps → `TIMESTAMP`
* Normalizes engagement metrics with `COALESCE`
* Creates derived flags (e.g. `has_image`)

### 2️⃣ Dimensional Modeling

* **fct_messages** – engagement metrics & foreign keys
* **dim_channels** – channel metadata & activity spans
* **dim_dates** – date spine for time-series analytics

---

## 👁️ Task 3: AI Enrichment (YOLOv8 Object Detection)

Images are enriched with **computer vision metadata**.

### 1️⃣ Classification Logic

* **Promotional** – person + product
* **Product Display** – product only
* **Lifestyle** – people without products

### 2️⃣ Warehouse Integration

* YOLO detections stored in `detection.yolo_results`
* Joined via `fct_image_detections`
* Enables analysis of **human presence vs engagement**

---

## 🌐 Task 4: Analytical API (Serve)

A **FastAPI** service exposes warehouse insights via REST.

### 1️⃣ Key Endpoints

* `GET /api/reports/top-products` – most mentioned medical terms
* `GET /api/channels/{name}/activity` – posting trends
* `GET /api/search/messages` – keyword search
* `GET /api/reports/visual-content` – AI image analytics

### 2️⃣ Developer Experience

* **Pydantic** for strict validation
* **Swagger UI** available at `/docs`

---

## ⚙️ Task 5: Pipeline Orchestration (Automate)

The full workflow is automated using **Dagster**.

### 1️⃣ Job Dependency Graph

```
Scrape Data
   ↓
YOLO Detection
   ↓
Load to PostgreSQL
   ↓
dbt Transformations
```

### 2️⃣ Operations & Monitoring

* Daily scheduled runs
* Dagster UI for observability and debugging

---

## 💻 How to Run

### 1️⃣ Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
DATABASE_URL=postgresql://user:password@localhost:5432/warehouse
```

---

### 2️⃣ Run the Full Pipeline (Dagster)

```bash
dagster dev -f orchestration/pipeline.py
```

Access the Dagster UI:

```
http://localhost:3000
```

---

### 3️⃣ Start the API

```bash
uvicorn api.main:app --reload
```

API Docs:

```
http://127.0.0.1:8000/docs
```

---

## ✅ Project Status

| Task               | Status      |
| ------------------ | ----------- |
| Task 1 – Scraping  | ✅ Completed |
| Task 2 – Warehouse | ✅ Completed |
| Task 3 – AI (YOLO) | ✅ Completed |
| Task 4 – FastAPI   | ✅ Completed |
| Task 5 – Dagster   | ✅ Completed |

🚀 **Full Production Pipeline: Active**

