import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

WEBHOOK_URL = "https://discord.com/api/webhooks/1502018575970603164/oTnFrqc0fPDfa8nxFMnotpleBfgJ0R2ny9H-6EkB5UupHfPkNsTLBDrh3lVOWRuaQYKz"


def get_fuel_prices():
    url = "https://www.autocentrum.pl/paliwa/ceny-paliw/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    prices = soup.find_all("span", class_="price-value")

    try:
        pb95 = prices[0].text.strip()
        pb98 = prices[1].text.strip()
        on = prices[2].text.strip()
        lpg = prices[3].text.strip()
    except:
        pb95 = "brak"
        pb98 = "brak"
        on = "brak"
        lpg = "brak"

    return {
        "PB95": pb95,
        "PB98": pb98,
        "ON": on,
        "LPG": lpg
    }


def get_promotions():
    promos = []

    try:
        r = requests.get(
            "https://news.google.com/rss/search?q=promocja+paliwo+orlen+bp+shell",
            headers={"User-Agent": "Mozilla/5.0"}
        )

        text = r.text.lower()

        if "orlen" in text:
            promos.append("⛽ Orlen — możliwe promocje w aplikacji Vitay")

        if "bp" in text:
            promos.append("⛽ BP — sprawdź weekendowe rabaty")

        if "shell" in text:
            promos.append("⛽ Shell — możliwe zniżki w aplikacji ClubSmart")

        if "auchan" in text:
            promos.append("⛽ Auchan — możliwe tańsze paliwo na wybranych stacjach")

    except:
        promos.append("Nie udało się pobrać promocji")

    if len(promos) == 0:
        promos.append("Brak aktualnych promocji")

    return promos


def send_to_discord():
    prices = get_fuel_prices()
    promos = get_promotions()

    today = datetime.now().strftime("%d.%m.%Y")

    promo_text = "\n".join(promos)

    embed = {
        "title": f"⛽ Ceny paliw — Pomorskie ({today})",
        "description": (
            f"🚗 **PB95:** {prices['PB95']} zł\n"
            f"🏎️ **PB98:** {prices['PB98']} zł\n"
            f"🚛 **ON:** {prices['ON']} zł\n"
            f"🔥 **LPG:** {prices['LPG']} zł\n\n"
            f"🔥 **PROMOCJE:**\n{promo_text}"
        ),
        "color": 16753920
    }

    requests.post(WEBHOOK_URL, json={
        "embeds": [embed]
    })

    print("Wysłano ceny paliw")


scheduler = BlockingScheduler(timezone=pytz.timezone("Europe/Warsaw"))

scheduler.add_job(send_to_discord, 'cron', hour=6, minute=0)

print("Bot działa...")

send_to_discord()

scheduler.start()
