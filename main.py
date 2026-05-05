import os
import re
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    required_libraries = ['beautifulsoup4', 'requests', 'selenium', 'webdriver-manager']
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            print(f"Instalando {library}...")
            install(library)

check_and_install_dependencies()

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def download_file(url, folder_path):
    local_filename = url.split('/')[-1].split('?')[0]
    file_path = os.path.join(folder_path, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def scrape_facebook_ads_library(url, download_folder):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    scroll_pause_time = 3
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    page_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    video_tags = soup.find_all('video', class_=True)
    img_tags = soup.find_all('img')
    
    video_urls = []
    for video in video_tags:
        video_src = video.get('src')
        if video_src and '.mp4' in video_src:
            video_urls.append(video_src)
    
    image_urls = []
    for img in img_tags:
        img_src = img.get('src')
        if img_src and ('.jpg' in img_src or '.png' in img_src):
            image_urls.append(img_src)
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    for video_url in video_urls:
        download_file(video_url, download_folder)
    
    for img_url in image_urls:
        download_file(img_url, download_folder)
    
    return len(video_urls), len(image_urls)

if __name__ == "__main__":
    url_input = input("Digite a URL da página do Facebook Ads Library: ")
    folder_input = input("Digite o caminho da pasta onde os arquivos serão salvos: ")
    
    try:
        video_count, image_count = scrape_facebook_ads_library(url_input, folder_input)
        print(f"Download completado com sucesso! {video_count} vídeos e {image_count} imagens foram baixados.")
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
