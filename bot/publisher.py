import re
from telegram.constants import ParseMode

def escape_md_v2(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def escape_link_url(url: str) -> str:
    return url.replace("\\", "\\\\").replace(")", "\\)")

def format_opportunity(opp: dict) -> str:
    raw_summary = opp.get("summary", "")
    truncated = raw_summary[:280]
    if len(raw_summary) > 280:
        truncated += "..."
    summary_esc = escape_md_v2(truncated)
    title = escape_md_v2(opp["title"])
    country = escape_md_v2(opp.get("country", "N/A"))
    level = escape_md_v2(opp.get("level", "N/A"))
    funding = escape_md_v2(opp.get("funding", "N/A"))
    deadline = escape_md_v2(opp.get("deadline", "N/A"))
    link_esc = escape_link_url(opp["link"])

    return (
        f"🎓 *{title}*\n"
        f"📌 {summary_esc}\n"
        f"🌍 {country} | 🎯 {level} | 💰 {funding}\n"
        f"⏳ {deadline}\n"
        f"🔗 [Lien officiel]({link_esc})"
    )

async def publish_opportunity(bot, channel_id: int, opp: dict):
    text = format_opportunity(opp)
    await bot.send_message(
        chat_id=channel_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )