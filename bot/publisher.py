import asyncio
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter

def format_opportunity_rich(opp: dict) -> str:
    title = opp.get("title", "Sans titre").strip()
    summary = opp.get("summary", "").strip()
    country = opp.get("country", "").strip()
    level = opp.get("level", "").strip()
    funding = opp.get("funding", "").strip()
    deadline = opp.get("deadline", "").strip()
    benefits = opp.get("benefits", [])  # liste de chaînes

    lines = [f"🎓 {title}\n"]

    if summary:
        lines.append(f"📝 {summary}\n")

    # Bloc infos principales
    info = []
    if country:
        info.append(f"🌍 {country}")
    if level:
        info.append(f"🎯 {level}")
    if funding:
        info.append(f"💰 {funding}")
    if info:
        lines.append(" | ".join(info) + "\n")

    # Benefits
    if benefits:
        lines.append("✨ *Avantages :*")
        for b in benefits:
            lines.append(f"  • {b}")
        lines.append("")

    if deadline:
        lines.append(f"⏳ *Deadline :* {deadline}\n")

    # Hashtags (générés automatiquement à partir de la source, du pays, du niveau)
    tags = []
    if country:
        tags.append(f"#{country.replace(' ', '_')}")
    if level:
        tags.append(f"#{level.replace(' ', '_')}")
    if opp.get("source"):
        tags.append(f"#{opp['source']}")
    if funding and 'fully' in funding.lower():
        tags.append("#Fully_Funded")
    if tags:
        lines.append(" ".join(tags))

    return "\n".join(lines)

async def publish_opportunity(bot, channel_id: int, opp: dict):
    text = format_opportunity_rich(opp)
    image_url = opp.get("image_url")
    link = opp.get("link", "")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Apply / Voir l'offre", url=link)]
    ]) if link else None

    # Envoi avec photo
    if image_url:
        try:
            await bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=text,
                reply_markup=keyboard
            )
            await asyncio.sleep(6)  # délai un peu plus long pour éviter le flood
            return
        except Exception as e:
            print(f"Image invalide ou erreur : {e}")

    # Fallback texte
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=channel_id,
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            await asyncio.sleep(6)
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
                await asyncio.sleep(6)