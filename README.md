# Shopping Alert

A robust, Python-based data engineering application designed to track pricing, inventory, and stock statuses across different e-commerce platforms. The application stores historical data in a PostgreSQL database and automatically sends out email alerts when significant changes are detected.

---

## 🛠 Features

- **Multi-Platform Support**: Built with an extensible `BasePlatform` class.
  - **Runway** (`shopping_platforms/runway.py`): Scrapes item details, sizes, colors, and stock using `requests` and `BeautifulSoup`.
  - **Zozotown** (`shopping_platforms/zozotown.py`): Leverages `playwright` to accurately extract dynamic data.
- **Robust Database Integration**: Uses `psycopg` and `pandas` for seamless data ingestion. The database structure clearly separates item dimensions (brands, names, colors, sizes) from factual status snapshots (prices, inventory counts).
- **Smart Automated Alerts**: Evaluates temporal changes locally. If a product's price drops, a variant goes back in-stock, or its remaining inventory count drops, it fires off an HTML-formatted alert via Gmail's SMTP.
- **Modern Python Ecosystem**: Managed entirely by `uv` for lightning-fast backend virtual environments and dependency management.
- **Containerization & Dev Scripts**: Includes a `Dockerfile` for execution anywhere, and PowerShell helper scripts in `bin/` to instantly spin up database containers for local development.

---

## 🚀 Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** Package Manager
- **Docker Desktop** / **Docker Engine** (For the PostgreSQL database and/or running the whole app)
- A Gmail account with an App Password (for email alerts)

---

## ⚙️ Configuration Setup

Before running the application, populate the `.toml` files inside the `configs/` directory:

1. **`configs/platforms.toml`**  
   Define the specific item identifiers or URLs you want the scraper to track.
   ```toml
   [runway]
   # Runway platform expects 10-digit item IDs
   run_args = [
       "0725627802",
       "0226204003",
   ]

   [zozotown]
   # Zozotown platform expects full item URLs
   run_args = [
       "https://zozo.jp/shop/dazzlin/goods/100200995/",
   ]
   ```

2. **`configs/db.toml`**  
   Your PostgreSQL connection credentials.
   ```toml
   [postgres]
   host = "localhost"
   port = 5432
   dbname = "postgres"
   user = "postgres"
   password = "your_password_here"
   ```

3. **`configs/email.toml`**  
   Your Gmail App credentials for the `smtplib` sender.
   ```toml
   [gmail]
   email_address = "your_email@gmail.com"
   app_password = "your_16_char_app_password"
   smtp_server = "smtp.gmail.com"
   smtp_port = 465
   ```

---

## 💻 Running Locally (Development)

### Windows Users

1. **Initial Setup**: Run the included setup script to sync `uv` dependencies and install Playwright browser binaries.
   ```powershell
   .\bin\setup.ps1
   ```
2. **Start Database Container**: We provide a PowerShell script to easily manage a local `postgres:14` Docker container. Feel free to define custom ports/passwords in `bin/db.env`.
   ```powershell
   # Starts a fresh postgres DB on port 5432
   .\bin\run_db.ps1 start
   ```
   *(Other commands include: `stop`, `resume`, `terminate`, `bounce`)*
3. **Execute the Application**:  
   Run the overarching `run.py` script. You can specify a single platform or run them all.
   ```powershell
   uv run python run.py --platform all
   # OR: uv run python run.py --platform runway
   ```

### Linux / Ubuntu Users

1. **Initial Setup**: Install `uv`, sync the environment, and install Playwright.
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv sync
   uv run playwright install chromium
   uv run playwright install-deps
   ```
2. **Start Database**: Use your preferred method to launch a PostgreSQL instance pointing to the credentials in your `db.toml`.
3. **Execute the Application**:
   ```bash
   uv run python run.py --platform all
   ```

---

## 🐳 Running via Docker

You can run the entire application fully containerized using the provided `Dockerfile`! This method is highly recommended for production as it automatically handles all system-level Playwright dependencies.

1. **Build the image**:
   ```bash
   docker build -t shopping-alert .
   ```

2. **Run the container**:
   Ensure your database is running and accessible to the network.
   ```bash
   docker run --rm shopping-alert
   ```
   *(By default, the `CMD` triggers `uv run python run.py --platform all`)*

---

## 🧪 Testing

The project is fully covered by `pytest` utilizing `unittest.mock` to isolate database and network requests. Configurations for `pytest` are centralized in `pyproject.toml`.

To run the full unit test suite:
```bash
uv run pytest tests/ -v
```

---

## 🗄 Database Schema Details

The application automatically initializes schemas on startup under the `shopping_alert` schema if they don't exist:

- **`platforms`**: A dimension table storing the active platforms.
- **`items`**: Stores item-level descriptions (Platform ID, Item ID, Name, Brand, URL, Currency).
- **`specs`**: Stores SKU-level variations (Color, Size).
- **`status`**: A temporal fact-table tracking the snapshot of a SKU. Logs the Original Price, Current Price, Inventory Count, In-Stock boolean, and an `asof` UTC timestamp for every scrape event.
