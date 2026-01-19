
---

# 🏥 Medical Telegram Data Warehouse

A scalable **data engineering pipeline** designed to extract, transform, and analyze **medical business data from Telegram channels** using an asynchronous scraper, a **dbt-powered PostgreSQL warehouse**, and a modular analytics architecture.

---

## 📂 Project Structure

```text
medical-telegram-warehouse/
├── data/
│   └── raw/
│       ├── telegram_messages/  # JSON partitions (YYYY-MM-DD/channel.json)
│       └── images/             # Organized photos (channel/msg_id.jpg)
├── medical_warehouse/          # dbt project directory
│   ├── models/
│   │   ├── staging/            # Task 2: Data cleaning & type casting
│   │   └── marts/              # Task 2: Star Schema (Dimensions & Facts)
│   ├── tests/                  # Custom data quality tests
│   └── dbt_project.yml         # dbt configuration
├── src/
│   ├── scraper.py              # Task 1: Asynchronous Telegram scraper
│   └── to_postgres.py          # Task 2: JSON to PostgreSQL loader
├── api/                        # Task 4: FastAPI Application (Roadmap)
│   └── main.py
├── logs/                       # Scraper activity & error logs
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🛰️ Task 1: Data Scraping & Collection (Extract)

The goal of this stage is to build a **robust extraction layer** capable of handling high-volume Telegram channels without triggering rate limits.

### 1️⃣ Asynchronous MTProto Scraper

Using the **Telethon** library, the scraper interacts directly with Telegram’s **MTProto protocol**, enabling efficient access to both messages and media.

* **Concurrency**
  Uses `asyncio` to download high-resolution images while parsing message metadata in parallel.

* **Resilience**
  Implements `FloodWaitError` handling to automatically pause and resume scraping when rate limits are encountered.

### 2️⃣ Bronze Data Lake (Raw Layer)

All extracted data is stored in its **raw form** to avoid early data loss.

* **Hive-Style Partitioning**

  ```text
  data/raw/telegram_messages/YYYY-MM-DD/channel_name.json
  ```

  Enables partition pruning for downstream analytics and transformations.

* **Media Decoupling**
  Images are stored separately using message identifiers, keeping the warehouse lightweight while enabling downstream computer-vision analysis (Task 3).

---

## 🏗️ Task 2: Data Modeling & Transformation (Transform)

Raw Telegram JSON is transformed into a **clean Star Schema** using **dbt** and **PostgreSQL**.

### 1️⃣ Staging Layer (`stg_telegram_messages`)

Acts as the data cleaning factory:

* Casts ISO date strings to proper `TIMESTAMP`
* Normalizes engagement metrics using `COALESCE`
* Creates derived boolean fields (e.g. `has_image`)
* Ensures schema consistency before dimensional modeling

### 2️⃣ Dimensional Modeling (Star Schema)

* **`fct_messages` (Fact Table)**
  Central table containing engagement metrics and foreign keys

* **`dim_channels` (Dimension)**
  Channel metadata including activity span and average engagement

* **`dim_dates` (Dimension)**
  Date spine enabling time-series analysis (weekday, weekend, quarter, etc.)

### 3️⃣ Data Quality & Validation

A **test-driven transformation** approach using dbt tests:

* **Referential Integrity**
  Ensures every message maps to a valid channel

* **Custom Business Rules**
  Prevents data corruption using rules such as:

  * No future-dated messages
  * Valid timestamp ranges

---

## 🚀 Future Roadmap

### 👁️ Task 3: Object Detection (YOLOv8)

Image analytics using **Ultralytics YOLOv8**:

* **Detection**
  Identify pills, bottles, and people in medical posts

* **Classification**

  * *Promotional*: Person + Product
  * *Product Display*: Product only

* **Goal**
  Measure how visual content type affects engagement

---

### 🌐 Task 4: Analytical API (FastAPI)

Expose the warehouse through a RESTful API.

Planned endpoints:

* `/api/reports/top-products`
* `/api/channels/{name}/activity`
* `/api/search`

Features:

* Pydantic-based request/response validation
* Read-optimized analytics queries

---

### ⚙️ Task 5: Pipeline Orchestration (Dagster)

Automate the end-to-end pipeline.

* Convert scripts into **Dagster ops**
* Schedule daily incremental runs
* Monitor pipeline health via Dagster UI

---

## 💻 How to Run

### 1️⃣ Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 2️⃣ Data Extraction (Task 1)

Create a `.env` file containing your Telegram credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
```

Run the scraper:

```bash
python src/scraper.py
```

---

### 3️⃣ Load Data to PostgreSQL (Task 2)

```bash
python src/to_postgres.py
```

---

### 4️⃣ dbt Transformations

```bash
cd medical_warehouse
dbt run
dbt test
```

View documentation:

```bash
dbt docs generate
dbt docs serve
```

---

## ✅ Project Status

