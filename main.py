from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from typing import List
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

app = FastAPI(
    title="WakeABC Scraper API",
    description="""
    An API for searching and retrieving product information from WakeABC.
    This API provides real-time product data including inventory levels across different stores.
    """,
    version="1.0.0",
    openapi_tags=[{
        "name": "products",
        "description": "Operations with products and inventory"
    }]
)

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search term to look for products")

    class Config:
        schema_extra = {
            "example": {
                "query": "Bourbon"
            }
        }

class InventoryData(BaseModel):
    store_address: str = Field(..., description="The physical address of the store")
    quantity: str = Field(..., description="The quantity of product available in stock")

    class Config:
        schema_extra = {
            "example": {
                "store_address": "123 Main St, Anytown, USA",
                "quantity": "5"
            }
        }

class Product(BaseModel):
    product_name: str = Field(..., description="The name of the product")
    product_price: str = Field(..., description="The current price of the product")
    product_size: str = Field(..., description="The size/volume of the product")
    plu_number: str = Field(..., description="Product Look-Up (PLU) number")
    inventory_data: List[InventoryData] = Field(..., description="Inventory levels across different stores")

    class Config:
        schema_extra = {
            "example": {
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
        }

class SearchResponse(BaseModel):
    products: List[Product] = Field(..., description="List of products matching the search criteria")

@app.get("/")
async def root():
    """
    Redirect to the API documentation page.
    """
    return RedirectResponse(url="/docs")

@app.post("/search", 
         response_model=SearchResponse,
         tags=["products"],
         summary="Search for products",
         response_description="List of products matching the search criteria")
async def search_products(search_request: SearchRequest):
    """
    Search for products in the WakeABC database.

    This endpoint scrapes the WakeABC website for product information based on the provided search term.
    It returns detailed product information including inventory levels across different stores.

    Args:
        search_request: SearchRequest object containing the query parameter

    Returns:
        A SearchResponse object containing a list of products matching the search criteria

    Raises:
        HTTPException: If the external service is unavailable or returns an error
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://wakeabc.com',
        'Connection': 'keep-alive',
        'Referer': 'https://wakeabc.com/search-results',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
    }

    data = {
        'productSearch': search_request.query,
    }

    try:
        response = requests.post('https://wakeabc.com/search-results', headers=headers, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.findAll("div", attrs={"class": "wake-product"})
    
    results = []
    for product in products:
        pro_name = product.find("h4").text.strip()
        pro_price = product.find("span", attrs={"class": "price"}).text.strip()
        pro_size = product.find("span", attrs={"class": "size"}).text.strip()
        plu_num = product.find("small").text.strip()
        
        inventory_data = []
        if product.find("div", attrs={"class": "inventory-collapse"}):
            lis = product.find("div", attrs={"class": "inventory-collapse"}).findAll("li")
            for li in lis:
                store_address = li.find("span", attrs={"class": "address"}).get_text("\n").strip()
                qty = li.find("span", attrs={"class": "quantity"}).text.replace("in stock", "").strip()
                inventory_data.append(InventoryData(store_address=store_address, quantity=qty))
        
        results.append(Product(
            product_name=pro_name,
            product_price=pro_price,
            product_size=pro_size,
            plu_number=plu_num,
            inventory_data=inventory_data
        ))
    
    return SearchResponse(products=results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)