# Shopping Alert

A Python-based, containerized data engineering application designed to scrape and track pricing/inventory data across different e-commerce shopping platforms. 

## 🛠 Features
- **Modular Scraping**: Easily extensible platform classes (`BasePlatform`) for different storefronts. Currently supports:
  - Runway (`shopping_platforms/runway.py`)
  - Zozotown (`shopping_platforms/zozotown.py` - uses Playwright)
- **Database Integration**: Fully managed PostgreSQL connections using `psycopg`. Data is seamlessly initialized, upserted, and structured with clean database schemas.
- **Dockerized Postgres**: Easy setup and teardown of the database environment using custom PowerShell scripts.
- **Modern Python Tooling**: Uses `uv` for lightning-fast dependency management and virtual environments.

## 🚀 Prerequisites
- Windows (PowerShell)
- **Docker Desktop** (Make sure the daemon is running to start the database)
- **Python 3.12+**

## 💻 Setup Instructions

1. **Install Dependencies & Browsers**
The project includes a unified setup script to automatically install `uv`, sync your Python dependencies, and install the Playwright browser binaries required for scraping.
```powershell
.\bin\setup.ps1
```

2. **Configure Database Environment**
Update your database passwords and configuration if needed in `bin\db.env` and `configs\db.toml`.

3. **Start the Database**
Use the included helper script to launch your local PostgreSQL 14 Docker container. 
```powershell
.\bin\run_db.ps1 start
```
*Note: Available commands are `start`, `stop`, `resume`, `terminate`, and `bounce`.*

## 🏃 Usage
Data extraction uses configuration targets stored in `configs/platforms.toml`. You can run the application directly from the root using:

```powershell
uv run run.py --platform all
```
*(Or specify a specific platform by name, such as `--platform zozotown`)*

The script will:
1. Initialize the `shopping_alert` schema and database tables if they don't exist.
2. Read the target Items or URLs from your platform config.
3. Automatically launch Playwright (or basic requests) to scrape HTML.
4. Extract, transform, and normalize the data into standard `BaseRecord` structures using Pydantic.
5. Upsert the latest inventory, price, and item specifications directly into the PostgreSQL database.

## 🗄 Database Schema
The project uses an organized relational layout under the `shopping_alert` schema:
- `platforms`: Core platform dimension tables
- `items`: General item details (Brand, Name, URL)
- `specs`: SKU-level details (Size, Color)
- `status`: Temporal fact table tracking pricing and inventory changes over time
