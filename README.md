# MBOX to CSV Web Converter

A simple web application that converts MBOX email archive files to CSV format.

## Features

- 📧 Convert MBOX files to CSV format
- 🌐 Easy-to-use web interface with drag & drop support
- 🔒 Secure file processing (files are not stored permanently)
- ⚡ Fast conversion and instant download
- 🐳 Docker support for easy deployment

## Extracted Fields

The converter extracts the following fields from emails:
- **From**: Sender email address
- **To**: Recipient email address
- **Cc**: Carbon copy recipients
- **Subject**: Email subject
- **Date**: Email date and time
- **Body**: Email body content (plain text)

## Quick Start with Docker

The easiest way to run the application is using Docker Compose:

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set a secure SECRET_KEY

3. Start the application:
```bash
docker compose up
```

Then open your browser and navigate to `http://localhost:5000`

## Manual Installation

If you prefer to run without Docker:

1. Install Python 3.11 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and go to `http://localhost:5000`

## Usage

1. Open the web interface in your browser
2. Click the upload area or drag and drop your `.mbox` file
3. Click "Convert to CSV"
4. The converted CSV file will automatically download

## Requirements

- Python 3.11+
- Flask 3.0.0
- Docker and Docker Compose (for containerized deployment)

## File Size Limit

Maximum file size: 100MB

## Credits

This project was inspired by:
- [jarrodparkes/mbox-to-csv](https://github.com/jarrodparkes/mbox-to-csv)
- [akstuhl/mboxtocsv](https://github.com/akstuhl/mboxtocsv)

## License

MIT
