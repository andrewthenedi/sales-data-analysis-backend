# Sales Data Analysis Dashboard - Backend

This repository contains the backend Flask API powering the Sales Data Analysis Dashboard. It provides endpoints for data retrieval, filtering, download, upload, and data locking to enhance data integrity.

## Features

- **Secure Data Retrieval:** Fetches sales data from an SQLite database, applying filters based on city, district, time range, and quantity thresholds.
- **Data Transformation:** Processes raw data into a ready-to-visualize format (e.g., pandas DataFrame).
- **Excel Export:** Generates and serves downloadable Excel spreadsheets containing filtered sales data.
- **Data Upload:** Handles file uploads, validates data, and updates the database accordingly.
- **Data Locking:** Safeguards data quality by enabling data locking for critical metrics.

## Technologies

- **Flask:** Python web framework.
- **pandas:** Data manipulation and analysis library.
- **SQLite3:** Embedded database for easy setup and portability.
- **SQLAlchemy:** Database abstraction for interactions with SQLite.

## Getting Started

### Prerequisites

- Python 3.7 or later
- pip (Python package installer)
