# CRM + Sales Warehouse: End-to-End Data Platform

[![CRM Warehouse CI](https://github.com/shaan-alpha/CRM-Sales-Warehouse/actions/workflows/ci.yml/badge.svg)](https://github.com/shaan-alpha/CRM-Sales-Warehouse/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![dbt](https://img.shields.io/badge/dbt-1.10.0-orange.svg)](https://www.getdbt.com/)
[![Airflow](https://img.shields.io/badge/Airflow-Astro-red.svg)](https://www.astronomer.io/)

[![GitHub Stars](https://img.shields.io/github/stars/Shaan-alpha/CRM-Sales-Warehouse?style=for-the-badge&color=ffd700)](https://github.com/Shaan-alpha/CRM-Sales-Warehouse/stargazers)
[![GitHub Sponsor](https://img.shields.io/badge/Sponsor-Pink?style=for-the-badge&logo=githubsponsors&logoColor=white&color=ea4aaa)](https://github.com/sponsors/Shaan-alpha)

> [!NOTE]

A modern, production-grade data engineering project featuring a full ETL/ELT pipeline for the **Maven Analytics CRM + Sales** dataset. This platform extracts raw operational data, transforms it into a robust star schema using **dbt**, and delivers actionable insights through a 5-page **Power BI** executive dashboard.

---

## 🚀 Key Highlights

- **Automated Orchestration**: End-to-end pipeline managed by **Apache Airflow (Astronomer)**.
- **Modular Modeling**: The warehouse star schema is built by versioned SQL in `sql/transformations/`, with an in-progress **dbt Core** layer (`crm_warehouse_dbt/` — currently `stg_accounts` + `dim_accounts`) running downstream in the same DAG.
- **Star Schema Architecture**: Optimized for analytical performance with conformed dimensions and clear fact grain.
- **Enterprise Visualization**: 5-page interactive Power BI report covering executive KPIs, agent performance, and pipeline health.
- **Data Quality Framework**: Multi-stage validation including dbt tests, custom SQL checks, and schema enforcement.
- **Containerized Infrastructure**: Fully portable environment using **Docker** and **Astro CLI**.

---

## 🏗️ Architecture & Monitoring

The pipeline follows a **Medallion-style** approach modified for a Warehouse:
1.  **Staging**: Raw data loaded into Postgres as-is from Parquet snapshots.
2.  **Warehouse**: Versioned SQL in `sql/transformations/` creates a cleaned, typed, modeled star schema in `warehouse`; a dbt Core layer runs downstream.
3.  **Reporting**: Power BI consumes the `warehouse.*` schema for optimal report performance.

### 🔄 Pipeline Workflow
```mermaid
flowchart TD
    subgraph Ingestion ["📤 Ingestion & Storage"]
        Raw["Raw Data (Maven Analytics CSVs)"]
        Parquet[("📦 Parquet Snapshots\n(Immutable Raw Lake)")]
    end

    subgraph Staging ["🐘 PostgreSQL Staging"]
        PGStaging[("staging.*\n(Raw 1:1 Mirrors)")]
    end

    subgraph Transformation ["⚡ dbt Core Transformations"]
        DBTModels[("warehouse.dim_* & fact_sales\n(Star Schema)")]
        DBTTests{"🔍 dbt Validation\n(Schema & Data Tests)"}
    end

    subgraph Quality ["🛡️ Quality & Governance"]
        Checks["quality_checks.py\n(Parity & Integrity Suite)"]
    end

    subgraph BI ["📊 Business Intelligence"]
        PBI["Microsoft Power BI\n(5-Page Executive Report)"]
    end

    Raw -->|"extract.py"| Parquet
    Parquet -->|"load_staging.py"| PGStaging
    PGStaging -->|"sql/transformations/"| DBTModels
    DBTModels -->|"dbt run + dbt test"| DBTTests
    DBTTests -->|"Pass"| Checks
    Checks -->|"Validated"| PBI

    subgraph Orchestration ["⚙️ Apache Airflow (Astro CLI)"]
        Airflow["Task & DAG Orchestration"]
    end

    Airflow -.-> Raw
    Airflow -.-> PGStaging
    Airflow -.-> DBTModels

    style Raw fill:#e53935,stroke:#333,stroke-width:2px,color:#fff
    style Parquet fill:#fb8c00,stroke:#333,stroke-width:2px,color:#fff
    style PGStaging fill:#1e88e5,stroke:#333,stroke-width:2px,color:#fff
    style DBTModels fill:#43a047,stroke:#333,stroke-width:2px,color:#fff
    style DBTTests fill:#8e24aa,stroke:#333,stroke-width:2px,color:#fff
    style Checks fill:#00acc1,stroke:#333,stroke-width:2px,color:#fff
    style PBI fill:#fbc02d,stroke:#333,stroke-width:2px,color:#000
    style Airflow fill:#37474f,stroke:#ffd54f,stroke-width:2px,color:#fff
```

### 🖥️ Infrastructure Overview
The project is fully containerized, providing a consistent environment for all services including PostgreSQL, Airflow, and pgAdmin.

| Service | Monitoring Tool | Status |
| :--- | :--- | :--- |
| **Airflow** | [Astro UI](http://localhost:8080) | ✅ Active |
| **Database** | [SQLTools / pgAdmin](http://localhost:5050) | ✅ Active |
| **Containers** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | ✅ Active |

#### Pipeline Success in Airflow
![Airflow DAG Success](docs/screenshots/10-airflow-dag-success.png)
*Visualizing the successful execution of the end-to-end extraction and transformation pipeline.*

#### Infrastructure Stack in Docker
![Docker Desktop Dashboard](docs/screenshots/09-docker-desktop-full.png)
*The full containerized stack including scheduler, worker, and database services.*

![Docker Containers List](docs/screenshots/08-docker-containers.png)
*Detailed view of the active service containers.*

---

## 📊 Business Intelligence Dashboard

The final output is a high-impact, 5-page executive report.

### 1. Executive Overview
Won revenue, win rate, average deal size, and at-risk pipeline at a glance. Monthly trend and full pipeline funnel side by side.
![Executive Overview](docs/screenshots/01-executive-overview.png)

### 2. Agent Performance
Detailed breakdown of sales agent efficiency and manager-level performance.
![Agent Performance](docs/screenshots/02-agent-performance.png)

### 3. Pipeline Analysis
Visualizing sales stages, stall rates, and conversion funnels to identify bottlenecks.
![Pipeline Analysis](docs/screenshots/03-pipeline-analysis.png)

### 4. Product Deep Dive & Regional Analysis
Analysis of product performance and geographic revenue distribution.
![Product Deep Dive](docs/screenshots/04-product-deep-dive.png)
![Regional Analysis](docs/screenshots/05-regional-analysis.png)

---

## 🛠️ Tech Stack & Database Design

### 🗄️ Data Warehouse Schema
The database is structured using a star schema for optimal query performance. Dimensions `warehouse.dim_account`, `warehouse.dim_product`, `warehouse.dim_sales_agent` and `warehouse.dim_date` support the central `warehouse.fact_sales`.

![SQLTools Database View](docs/screenshots/07-sql-tools-schema.png)
*Exploration of the `analytics` schema and dimension tables within VS Code SQLTools.*

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Orchestration** | [Apache Airflow](https://airflow.apache.org/) | Pipeline scheduling and management via **Astro CLI**. |
| **Transformation** | [dbt Core](https://www.getdbt.com/) | SQL modeling, testing, and documentation for the warehouse. |
| **ETL / Scripting** | [Python 3.11](https://www.python.org/) | `pandas`, `SQLAlchemy`, `PyArrow` for high-performance processing. |
| **Database** | [PostgreSQL 16](https://www.postgresql.org/) | Containerized warehouse with staging and analytical schemas. |
| **Infrastructure** | [Docker](https://www.docker.com/) | Containerization for consistent dev/prod environments. |
| **Visualization** | [Power BI](https://powerbi.microsoft.com/) | Advanced DAX modeling and interactive dashboard design. |

---

## ⚙️ Local Setup

### 1. Prerequisites
- Docker & Docker Compose
- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli)
- Python 3.11+

### 2. Infrastructure Initialization
Run the following to spin up the entire data platform:
```bash
astro dev start
```

### 3. Configuration
Copy the environment template and configure your local credentials:
```bash
cp .env.example .env
```

### 4. Manual Execution (Optional)
If you wish to run components individually:
```bash
# Run dbt transformations
cd crm_warehouse_dbt
dbt run

# Run quality checks
python etl/quality_checks.py
```

---

## 🧪 Data Quality & Testing

We enforce high data standards at every step:
- **dbt Tests**: Primary keys, relationships, and accepted values.
- **Custom Checks**:
    - **Parity**: Row count matching between staging and warehouse.
    - **Freshness**: Ensuring data is up-to-date.
    - **Referential Integrity**: Fact rows must resolve to valid dimensions.
- **Python Quality**: **Ruff** for linting and **Pytest** for transformation logic.

---

## 📜 License & Acknowledgements

- **Data Source**: [Maven Analytics: CRM + Sales](https://mavenanalytics.io/data-playground)
- **License**: [MIT](LICENSE)

---
*Built with ❤️ by Shaan*
