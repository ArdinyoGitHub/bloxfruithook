import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TARGET_URL = "https://fruityblox.com/stock"

# Senin istediğin test ve gerçek değerler
SEARCH_KEYWORDS = ["mythical", "magma", "flame", "kitsune", "leopard", "yeti", "dragon", "portal", "buddha"]

def check_stock():
    with sync_playwright() as p:
        # Görünmez tarayıcıyı başlat
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Siteye giriliyor...")
        page.goto(TARGET_URL)
        
        # Meyvelerin yüklendiği alanı bekle (Loading animasyonunun gitmesini bekle)
        # Sitede meyve isimleri genellikle büyük harfle yazılır (MAGMA, FLAME)
        try:
            page.wait_for_selector("text=Normal", timeout=20000)
            # Sayfanın tamamen yüklenmesi için 5 saniye daha bekle
            page.wait_for_timeout(5000)
            
            # Sayfadaki tüm metni çek
            content = page.content().lower()
            
            found = []
            for word in SEARCH_KEYWORDS:
                if word in content:
                    found.append(word.capitalize())
            
            if found:
                print(f"Buldum: {found}")
                send_discord_alert(found)
            else:
                print("Aranan meyveler şu an stokta yok.")
                
        except Exception as e:
            print(f"Hata: Sayfa yüklenemedi veya meyveler bulunamadı. {e}")
        
        browser.close()

def send_discord_alert(fruits):
    fruit_list = ", ".join(fruits)
    data = {
        "content": f"🚨 **STOK ALARMI!** 🚨\n\nŞu meyveler bulundu: **{fruit_list}**\n\nKontrol et: {TARGET_URL}",
        "username": "Blox Ajanı"
    }
    requests.post(WEBHOOK_URL, json=data)

if __name__ == "__main__":
    if WEBHOOK_URL:
        check_stock()
    else:
        print("Webhook URL eksik!")
