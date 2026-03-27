# BSF-NutriFeed API 🪰♻️

**BSF-NutriFeed** is a user-driven backend system designed to optimize Black Soldier Fly (BSF) larvae production. By integrating environmental monitoring with production tracking, the platform helps farmers convert organic waste into high-quality protein and organic fertilizer (frass) efficiently.

---

## 🚀 Features
* **Batch Management:** Track the lifecycle of BSF larvae production from waste intake to harvest.
* **Environmental Monitoring:** Log temperature, humidity, and larvae density data.
* **Yield Analytics:** Record larvae weight and residue (frass) grades for quality control.
* **Role-Based Access:** Secure endpoints for Farmers and Admins using JWT (Bearer) authentication.
* **API Documentation:** Interactive Swagger UI for easy endpoint testing.

## 🛠️ Tech Stack
* **Language:** Python 3.10
* **Framework:** Flask
* **Database:** MySQL (Structured with SQLAlchemy)
* **Documentation:** Flasgger (OpenAPI/Swagger 2.0)
* **DevOps:** Docker & Docker Compose

---

## 🚀 Getting Started

This project is fully containerized using Docker. This ensures the API and MySQL database run with the same configuration regardless of your Operating System.

### Prerequisites

Before starting, ensure you have the following installed:

* **Windows:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Recommend using the WSL 2 backend).
* **Mac:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Supports both Intel and Apple Silicon/M-series chips).
* **Linux:** [Docker Engine](https://docs.docker.com/engine/install/) and the [Docker Compose Plugin](https://docs.docker.com/compose/install/).

---

### 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/bsf-nutrifeed.git](https://github.com/your-username/bsf-nutrifeed.git)
    cd bsf-nutrifeed
    ```

2.  **Configure Environment Variables**
    Create a `.env` file in the root directory and add your credentials (refer to [.env.example](./.env.example)):

3.  **Build and Launch**
    Open your terminal (Command Prompt/PowerShell on Windows, or Terminal on Mac) and run:
    ```bash
    docker compose up --build
    ```

    If you've done this before, use:
    ```bash
    docker compose up
    ```

4.  **Access the API**
    Once the logs show `ready for connections`, the API will be live at:
    * **Main URL:** `http://localhost:5050`
    * **Documentation/Status:** `http://localhost:5050/status`

---

### 🛑 Stopping the App

To stop the containers and free up system resources:
```bash
docker compose down
```

### Local Setup
  #### Prerequisites
  * Debian or Ubuntu based system
  * Python 3.10+
  * MySQL Server (if running locally)
  * Docker (Optional, for containerized setup) preferred for cross-platform use

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/bsf-nutrifeed.git](https://github.com/your-username/bsf-nutrifeed.git)
   cd bsf-nutrifeed
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python3 -m api.v0.app
   ```
5. **Access the API:**
   The API will be available at `http://localhost:5050` by default or `http:localhost:$PORT` if specified in the `.env` file


### Docker Deployment
1. **Build and start the containers**:
   ```bash
   sudo docker-compose up --build -d
   ```
2. **Access the API:**
   The containerized API runs on `http:localhost:5050` by default or `http:localhost:$PORT` if specified in the `.env` file
   [!> [!NOTE]
   > The `.env` file must be edited before building the container]

### API Documentation
Once the server is running, you can access the interactive Swagger documentation at:
`http://localhost:$PORT/apidocs/`

### ⚙️ Project Structure

```text
├── api/
│   ├── v0/
│   │   ├── views/           # API Endpoint Logic (Controllers)
│   │   │   ├── documentation/ # Swagger YAML Definitions
│   │   │   ├── __init__.py
│   │   │   ├── batches.py
│   │   │   ├── harvest_logs.py
│   │   │   ├── monitoring_logs.py
│   │   │   ├── signin.py
│   │   │   ├── users.py
│   │   │   └── wastes.py
│   │   └── app.py           # Blueprint & API Configuration
│   └── __init__.py
├── models/                  # Database Schemas (SQLAlchemy)
│   ├── engine/              # Storage abstraction layer
│   │   └── db_storage.py    # MySQL/SQLAlchemy Engine Logic
│   ├── __init__.py
│   ├── base_model.py
│   ├── batch.py
│   ├── enum.py
│   ├── harvest.py
│   ├── monitoring.py
│   ├── user.py
│   └── waste.py
├── Dockerfile               # Container Configuration
├── docker-compose.yml       # Multi-container Orchestration
├── requirements.txt         # Project Dependencies
├── README.md                # Project Documentation
```

### 👥 Authors
This project is maintained by **Urom Jehoshaphat Ogbonnia**. See the full list of contributors in [AUTHORS.md](./AUTHORS.md).
