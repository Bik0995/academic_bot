import asyncio
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter

def format_opportunity_plain(opp: dict) -> str:
    title = opp.get("title", "Sans titre")
    summary_raw = opp.get("summary", "")
    summary = summary_raw[:300] + ("..." if len(summary_raw) > 300 else "")
    country = opp.get("country", "")
    level = opp.get("level", "")
    funding = opp.get("funding", "")
    deadline = opp.get("deadline", "")

    lines = [f"🎓 {title}"]
    if summary:
        lines.append(f"📌 {summary}")
    if country or level or funding:
        parts = [p for p in [country, level, funding] if p]
        lines.append("🌍 " + " | ".join(parts))
    if deadline:
        lines.append(f"⏳ {deadline}")
    return "\n".join(lines)

async def publish_opportunity(bot, channel_id: int, opp: dict):
    plain = format_opportunity_plain(opp)
    image_url = opp.get("image_url")
    link = opp.get("link", "")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Voir l'offre complète", url=link)]
    ]) if link else None

    # Essayer d'envoyer une photo
    if image_url:
        try:
            await bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=plain,
                reply_markup=keyboard
            )
            await asyncio.sleep(5)  # délai pour éviter le flood
            return
        except Exception as e:
            print(f"Image invalide ou erreur : {e}")

    # Fallback texte seul
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=channel_id,
                text=plain,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            await asyncio.sleep(5)  # délai après chaque envoi
            return
        except RetryAfter as e:
            wait = e.retry_after
            print(f"Flood control, attente {wait}s")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"Erreur envoi : {e}")
            traceback.print_exc()
            if attempt == max_retries - 1:
                print("Abandon après 3 tentatives")
            else:
                await asyncio.sleep(5)