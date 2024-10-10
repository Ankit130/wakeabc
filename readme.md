# WakeABC Scraper API

A FastAPI-based web scraper for WakeABC product information.

## Features

- Search products by query term
- Retrieve detailed product information including:
  - Product name
  - Price
  - Size
  - PLU number
  - Inventory data across different stores

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ankit130/wakeabc
cd wakeabc
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation at `http://localhost:8000/docs`

3. Make API requests:
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "Bourbon"}'
```

## API Endpoints

### POST /search

Search for products by query term.

**Request Body:**
```json
{
    "query": "string"
}
```

**Response:**
```json
{
    "products": [
        {
            "product_name": "string",
            "product_price": "string",
            "product_size": "string",
            "plu_number": "string",
            "inventory_data": [
                {
                    "store_address": "string",
                    "quantity": "string"
                }
            ]
        }
    ]
}
```

## Error Handling

The API includes proper error handling for:
- Failed requests to WakeABC
- Invalid input data
- Server errors


