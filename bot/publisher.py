import re
import logging
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

def escape_md_v2(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def escape_link_url(url: str) -> str:
    return url.replace("\\", "\\\\").replace(")", "\\)")

def format_opportunity(opp: dict) -> str:
    title = escape_md_v2(opp.get("title", "Sans titre"))
    summary_raw = opp.get("summary", "")
    summary = escape_md_v2(summary_raw[:280] + ("..." if len(summary_raw) > 280 else ""))
    country = escape_md_v2(opp.get("country", "N/A"))
    level = escape_md_v2(opp.get("level", "N/A"))
    funding = escape_md_v2(opp.get("funding", "N/A"))
    deadline = escape_md_v2(opp.get("deadline", "N/A"))
    link_esc = escape_link_url(opp.get("link", ""))

    return (
        f"🎓 *{title}*\n"
        f"📌 {summary}\n"
        f"🌍 {country} | 🎯 {level} | 💰 {funding}\n"
        f"⏳ {deadline}\n"
        f"🔗 [Lien officiel]({link_esc})"
    )

async def publish_opportunity(bot, channel_id: int, opp: dict):
    # Essaie d'abord avec MarkdownV2
    try:
        text = format_opportunity(opp)
        await bot.send_message(
            chat_id=channel_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    except Exception:
        # Si échec, envoi en texte brut sans mise en forme
        try:
            plain = f"{opp['title']}\n\n{opp.get('summary','')}\n\n{opp.get('country','')} | {opp.get('level','')} | {opp.get('funding','')}\nDeadline: {opp.get('deadline','')}\n{opp['link']}"
            await bot.send_message(
                chat_id=channel_id,
                text=plain,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Échec total de l'envoi : {e}")