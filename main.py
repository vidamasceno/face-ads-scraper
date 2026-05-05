import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

app = FastAPI() # O Render procura exatamente esta linha

# Configuração de CORS para o Lovable conseguir acessar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
async def scrape_ads(request: ScrapeRequest):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # No Render, às vezes é necessário apontar o caminho do binário do Chrome
    # Mas vamos tentar o padrão primeiro
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(request.url)
        
        # Scroll para carregar anúncios (reduzi para ser mais rápido no servidor)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, 'html.parser')
        results = []
        
        # Busca vídeos
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                results.append({"type": "video", "url": src})
        
        # Busca imagens
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and ('fbcdn.net' in src): # Filtro comum para imagens da CDN do FB
                results.append({"type": "image", "url": src})
        
        return {"data": results}

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API de Scraping Online"}
