# Setting Up Local Development Environment for GEOLocation-Mapper

## Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Pommmmmes/GEOLocation-Mapper.git
cd GEOLocation-Mapper
```

### 2. Add venv as Source
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
- Ensure you have PostgreSQL installed and running.
- Create a new PostgreSQL database.
- Update the database configuration in the application to point to your PostgreSQL instance.

### 5. Run the Application
```bash
python app.py
```