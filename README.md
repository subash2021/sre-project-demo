# Trading System Observability Platform

```mermaid
   graph TD
    %% --- THEME DEFINITIONS ---
    %% Define styles for nodes
    style D fill:#5d2d7a,color:#fff,stroke:#999,stroke-width:2px
    style C fill:#006400,color:#fff,stroke:#999,stroke-width:2px
    style E fill:#00008B,color:#fff,stroke:#999,stroke-width:2px
    style G fill:#CC5500,color:#fff,stroke:#999,stroke-width:2px
    style H fill:#008080,color:#fff,stroke:#999,stroke-width:2px
    style B fill:#555,color:#fff,stroke:#999,stroke-width:2px
    
    %% Define style for the arrows/links
    linkStyle default stroke:#ccc,stroke-width:1px


    %% --- DIAGRAM STRUCTURE ---
    subgraph "SRE / Operator (Your Laptop)"
        A[SRE User] -- Runs --> B["Operational CLI\n(Python Tool)"];
        A -- Views & Interacts --> C["Grafana Dashboard\nlocalhost:3000"];
        A -- Triggers Trade/Chaos --> D[Trading App];
    end

    subgraph "Docker Environment (docker-compose)"
        
        subgraph "Application & Database"
            D -- "1a. Writes Record" --> E[PostgreSQL DB];
            B -- Queries --> E;
        end

        subgraph "Logging Stack"
            D -- "1b. Writes Log File" --> F[Promtail];
            F -- "2a. Pushes Logs" --> G[Loki];
        end

        subgraph "Metrics Stack"
            D -- "1c. Exposes /metrics" --> H[Prometheus];
            H -- "2b. Scrapes Metrics" --> D;
        end

        subgraph "Unified Visualization"
            C -- "3a. Queries Logs (LogQL)" --> G;
            C -- "3b. Queries Metrics (PromQL)" --> H;
        end

    end
```

**Objective:** This project is a lite application built to demonstrate core Site Reliability Engineering (SRE) principles and technical abilities relevant to the Trading Operations role at GTS.

It simulates a simple trading application and wraps it in a modern observability stack, focusing on the tools mentioned in the job description: **Prometheus, Grafana, Loki, Python, SQL, and Docker.**

---

### Core Features

*   **Mock Trading Application:** A Python service that simulates processing trades, generating logs, metrics, and database records.
*   **Full Observability Stack:**
    *   **Metrics:** Custom application metrics exported to **Prometheus**.
    *   **Logs:** Structured logs aggregated by **Loki** via **Promtail**.
    *   **Dashboards:** A unified **Grafana** dashboard for visualizing metrics and logs side-by-side.
*   **Operational Tooling:** A Python-based CLI tool for operators to query the system without direct database access.
*   **Chaos Engineering Ready:** The system includes a "chaos mode" to simulate outages, proving the effectiveness of the monitoring and alerting setup.

---

### Live Demo (Screenshots)

**1. The Main Grafana Dashboard**
*(Insert a screenshot of your beautiful Grafana dashboard here)*

**2. Investigating an Outage with Chaos Mode**
*(Insert a screenshot or GIF showing the dashboard during chaos mode, with high failure rates)*

**3. The Operator CLI Tool in Action**
*(Insert a screenshot of your terminal showing the output of `python operator_tool.py find_trade --id 10`)*

---

### Tech Stack

*   **Application:** Python, psycopg2-binary
*   **Metrics:** Prometheus
*   **Logging:** Loki, Promtail
*   **Visualization:** Grafana
*   **Database:** PostgreSQL
*   **Orchestration:** Docker, Docker Compose

---

### How to Run

The entire stack is containerized and can be run with a single command.

**Prerequisites:**
*   Docker
*   Docker Compose

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/subash2021/sre-project-demo.git
    cd trading-sre-project
    ```

2.  **Launch the stack:**
    ```bash
    docker-compose up --build -d
    ```

3.  **Access the services:**
    *   **Grafana Dashboard:** `http://localhost:3000` (Login: admin/admin)
    *   **Prometheus UI:** `http://localhost:9090`
    *   **Loki (API):** `http://localhost:3100`

4.  **Use the Operator Tool:**
    ```bash
    # Make sure your Python venv is active or install dependencies
    # pip install psycopg2-binary tabulate

    # Find a trade by ID
    python operator_tool.py find_trade --id 25

    # Investigate recent "failures"
    python operator_tool.py investigate_failures --limit 3
    ```

5.  **Trigger Chaos Mode (Optional):**
    ```bash
    # To enable chaos mode:
    docker-compose exec simulator touch chaos.flag

    # To disable chaos mode:
    docker-compose exec simulator rm chaos.flag
    ```
---
