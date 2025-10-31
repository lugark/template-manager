# 🚀 Quick Start Guide

## Using uv (Recommended)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run the Application
```bash
uv run python run.py
```

### 3. Access the Web Interface
Open your browser and go to: http://localhost:8080

## Using Poetry (Alternative)

### 1. Install Dependencies
```bash
poetry install
```

### 2. Run the Application
```bash
poetry run python run.py
```

## Using Docker

### 1. Build and Run
```bash
docker compose up -d --build
```

### 2. Access the Web Interface
Open your browser and go to: http://localhost:8080

## Adding Files

1. Place your lasercut templates in the `data/` directory
2. Supported formats: ZIP, SVG, PDF, PNG, JPG, JPEG
3. Click "Scan Files" in the web interface to process them
4. Add tags to organize your files

## Features

- 📁 **Automatic File Scanning**: Scans the `data/` directory for supported files
- 🖼️ **Thumbnail Generation**: Creates thumbnails for images, PDFs, and SVGs
- 🏷️ **Tag Management**: Add and remove tags to organize your files
- 🔍 **Search & Filter**: Search by filename or filter by tags
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Development

### Run Tests
```bash
uv run python test_app.py
```

### Project Structure
```
template-manager/
├── app/
│   ├── main.py          # Flask application
│   ├── models.py        # Database models
│   ├── scanner.py       # File scanner
│   ├── templates/
│   │   └── index.html   # Web interface
│   ├── static/
│   │   ├── style.css    # Custom styles
│   │   └── thumbnails/  # Generated thumbnails
│   └── db/
│       └── data.sqlite  # SQLite database
├── data/                # Place your files here
├── run.py              # Application runner
├── test_app.py         # Test suite
└── pyproject.toml      # uv project configuration
```
