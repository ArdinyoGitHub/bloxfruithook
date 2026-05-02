import os
import requests
from bs4 import BeautifulSoup

# GitHub Secrets üzerinden gelecek olan Webhook URL
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
TARGET_URL = "https://fruityblox.com/stock"

def check_stock():
    # Tarayıcı taklidi (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sayfadaki tüm metni alıp küçük harfe çeviriyoruz
        page_text = soup.text.lower()
        
        # "mythical" kelimesini kontrol ediyoruz
        if "mythical" in page_text:
            print("Mythical meyve bulundu! Bildirim gönderiliyor...")
            send_discord_alert()
        else:
            print("Şu an Mythical meyve stokta yok.")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

def send_discord_alert():
    # Mesaj içeriği ve bot ayarları
    data = {
        "content": "🚨 **Mythical Meyve Alarmı!** 🚨\nFruityBlox stoklarına Mythical bir meyve düştü! Hemen kontrol et: https://fruityblox.com/stock",
        "username": "BloxStock Ajanı",
        "avatar_url": "https://i.imgur.com/AfFp7pu.png"
    }
    
    requests.post(WEBHOOK_URL, json=data)

if __name__ == "__main__":
    if WEBHOOK_URL:
        check_stock()
    else:
        print("HATA: DISCORD_WEBHOOK ortam değişkeni bulunamadı.")