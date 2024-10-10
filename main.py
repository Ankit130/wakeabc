from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

app = FastAPI(title="WakeABC Scraper API", 
             description="API for scraping product information from WakeABC")

class InventoryData(BaseModel):
    store_address: str
    quantity: str

class Product(BaseModel):
    product_name: str
    product_price: str
    product_size: str
    plu_number: str
    inventory_data: List[InventoryData]

class SearchResponse(BaseModel):
    products: List[Product]

@app.post("/search", response_model=SearchResponse)
async def search_products(query: str):
    cookies = {
        '_ga_WQZZR5YKCY': 'GS1.1.1728553989.2.1.1728554072.0.0.0',
        '_ga': 'GA1.1.942739358.1728206527',
        '_gauges_unique_month': '1',
        '_gauges_unique_year': '1',
        '_gauges_unique': '1',
        '_gauges_unique_hour': '1',
        '_gauges_unique_day': '1',
    }

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
        'productSearch': query,
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
