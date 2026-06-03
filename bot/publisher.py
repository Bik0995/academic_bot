import asyncio
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter

def format_opportunity_plain(opp: dict) -> str:
    title = opp.get("title", "Sans titre")
    summary_raw = opp.get("summary", "")
    summary = summary_raw[:280] + ("..." if len(summary_raw) > 280 else "")
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
    # Le lien sera dans le bouton, pas dans le texte
    return "\n".join(lines)

async def publish_opportunity(bot, channel_id: int, opp: dict):
    plain = format_opportunity_plain(opp)
    image_url = opp.get("image_url")
    link = opp.get("link", "")

    # Créer le bouton "Voir l'offre"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Voir l'offre", url=link)]
    ]) if link else None

    # Essayer d'envoyer une photo avec légende et bouton
    if image_url:
        try:
            await bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=plain,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            return
        except Exception as e:
            print(f"Échec envoi image pour '{opp.get('title','')}': {e}")

    # Fallback texte seul avec bouton
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=channel_id,
                text=plain,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
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
                await asyncio.sleep(2)