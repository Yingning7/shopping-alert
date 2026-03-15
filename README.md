# Shopping Alert

A Python-based, containerized data engineering application designed to scrape and track pricing/inventory data across different e-commerce shopping platforms, complete with automated email alerts!

## 🛠 Features
- **Modular Scraping**: Easily extensible platform classes (`BasePlatform`) for different storefronts. Currently supports:
  - Runway (`shopping_platforms/runway.py`)
  - Zozotown (`shopping_platforms/zozotown.py` - uses Playwright)
- **Database Integration**: Fully managed PostgreSQL connections using `psycopg`. Data is seamlessly initialized, upserted, and structured with clean database schemas.
- **Automated Alerts**: Email notifications sent out proactively whenever a price drops or inventory count changes!
- **Modern Python Tooling**: Uses `uv` for lightning-fast dependency management and virtual environments.
- **Containerization**: Fully Dockerized for seamless cross-platform execution on Linux and Windows.

---

## 🚀 Prerequisites
- **Docker Desktop** / **Docker Engine** (To run the Postgres database and the application container)
- **Python 3.12+**
- `uv` Package Manager

---

## ⚙️ Configuration Setup

Before running the application, make sure your configurations are properly set in the `configs/` directory.

1. **`configs/platforms.toml`**: Define the specific items and target URLs you want the scraper to track.
2. **`configs/db.toml`**: Ensure the PostgreSQL credentials match your deployed database.
3. **`configs/email.toml`**: Configure your SMTP parameters (e.g. Gmail App Passwords) for sending price drop alerts.

---

## 💻 Running Locally (Development)

### Windows Users
1. **Initial Setup**: Run the included setup script to install dependencies and Playwright binaries:
   ```powershell
   .\bin\setup.ps1
   ```
2. **Start Database**: 
   ```powershell
   .\bin\run_db.ps1 start
   ```
3. **Run App**:
   ```powershell
   uv run python run.py --platform all
   ```

### Linux / Ubuntu Users
1. **Initial Setup**: Install `uv` and sync dependencies:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv sync
   uv run playwright install
   uv run playwright install-deps
   ```
2. **Start Database**: Use your preferred method to launch a `postgres:14` container.
3. **Run App**:
   ```bash
   uv run python run.py --platform all
   ```

*(Note: When running locally on headless Linux servers, ensure Zozotown's scraper is set to `headless=True` or use `xvfb-run`.)*

---

## 🐳 Running via Docker

You can run the entire application fully containerized using the provided `Dockerfile`! This method handles all system-level Playwright dependencies automatically.

1. **Build the image**:
   ```bash
   docker build -t shopping-alert .
   ```

2. **Run the container**:
   Ensure your database is running and accessible to the container (e.g., using `--network host` or a dedicated Docker network).
   ```bash
   docker run --rm shopping-alert
   ```
   *(By default, the Docker image triggers `uv run python run.py --platform all`)*

---

## 🧪 Testing

The project is fully covered by `pytest` utilizing `unittest.mock` to isolate database and network requests.

To run the unit tests:
```bash
uv run pytest tests/ -v
```

---

## 🗄 Database Schema
The project uses an organized relational layout under the `shopping_alert` schema:
- `platforms`: Core platform dimension tables
- `items`: General item details (Brand, Name, URL)
- `specs`: SKU-level details (Size, Color)
- `status`: Temporal fact table tracking pricing and inventory changes over time
