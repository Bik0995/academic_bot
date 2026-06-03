import re
import asyncio
import traceback
from telegram.constants import ParseMode
from telegram.error import RetryAfter

def escape_md_v2(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def escape_link_url(url: str) -> str:
    return url.replace("\\", "\\\\").replace(")", "\\)")

def format_opportunity_plain(opp: dict) -> str:
    title = opp.get("title", "Sans titre")
    summary_raw = opp.get("summary", "")
    summary = summary_raw[:280] + ("..." if len(summary_raw) > 280 else "")
    country = opp.get("country", "")
    level = opp.get("level", "")
    funding = opp.get("funding", "")
    deadline = opp.get("deadline", "")
    link = opp.get("link", "")

    lines = [f"🎓 {title}"]
    if summary:
        lines.append(f"📌 {summary}")
    if country or level or funding:
        parts = [p for p in [country, level, funding] if p]
        lines.append("🌍 " + " | ".join(parts))
    if deadline:
        lines.append(f"⏳ {deadline}")
    lines.append(f"🔗 {link}")
    return "\n".join(lines)

async def publish_opportunity(bot, channel_id: int, opp: dict):
    plain = format_opportunity_plain(opp)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=channel_id,
                text=plain,
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