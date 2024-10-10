# WakeABC Scraper API

A FastAPI-based web scraper for WakeABC product information. This API allows you to search products and retrieve detailed information including inventory data across different stores.

## Features

- REST API endpoints for product searches
- Automatic API documentation (Swagger UI and ReDoc)
- Detailed product information including:
  - Product name
  - Price
  - Size
  - PLU number
  - Real-time inventory data across different stores
- Input validation using Pydantic models
- Error handling for external service failures

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ankit130/wakeabc
cd wakeabc
```

2. Create a virtual environment:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
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

2. Access the API:
   - Main documentation: `http://localhost:8000/docs`
   - Alternative documentation: `http://localhost:8000/redoc`
   - The root URL (`http://localhost:8000`) automatically redirects to the documentation

## API Endpoints

### 1. GET /
- Redirects to the API documentation
- No parameters required

### 2. POST /search
Search for products by query term.

**Request Body:**
```json
{
    "query": "string"
}
```

**Example Request:**
```bash
# Using curl
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "Bourbon"}'

# Using Python requests
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={"query": "Bourbon"}
)
print(response.json())
```

**Response:**
```json
{
    "products": [
        {
            "product_name": "Buffalo Trace Bourbon",
            "product_price": "$29.99",
            "product_size": "750ml",
            "plu_number": "12345",
            "inventory_data": [
                {
                    "store_address": "123 Main St, Anytown, USA",
                    "quantity": "5"
                }
            ]
        }
    ]
}
```

## Error Handling

The API includes proper error handling for:
- Failed requests to WakeABC (500 error)
- Invalid input data (422 error)
- Request validation errors (400 error)

Example error response:
```json
{
    "detail": "Failed to fetch data: Connection error"
}
```

## Development

### Project Structure
```
wakeabc-scraper/
├── main.py           # Main FastAPI application
├── requirements.txt  # Python dependencies
├── README.md        # Documentation
└── venv/            # Virtual environment (not in repo)
```

### Models
The API uses Pydantic models for request/response validation:

- `SearchRequest`: Validates the search query
- `Product`: Represents a single product with all its details
- `InventoryData`: Represents inventory information for a store
- `SearchResponse`: Wraps the list of products in the response

