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

    lines = [f"🎓 {title}\n"]

    if summary:
        lines.append(f"📌 {summary}\n")

    # Bloc d'infos avec icônes distinctes
    info_parts = []
    if country:
        info_parts.append(f"🌍 {country}")
    if level:
        info_parts.append(f"🎯 {level}")
    if funding:
        info_parts.append(f"💰 {funding}")
    if info_parts:
        lines.append(" | ".join(info_parts))

    if deadline:
        lines.append(f"\n⏳ Deadline: {deadline}")

    return "\n".join(lines)

async def publish_opportunity(bot, channel_id: int, opp: dict):
    plain = format_opportunity_plain(opp)
    image_url = opp.get("image_url")
    link = opp.get("link", "")

    # Bouton élégant
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Voir l'offre complète", url=link)]
    ]) if link else None

    # Tentative d'envoi avec photo
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
            print(f"Image invalide ou erreur : {e}")

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