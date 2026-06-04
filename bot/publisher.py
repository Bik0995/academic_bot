import asyncio
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter, TimedOut, NetworkError

def format_opportunity_rich(opp: dict) -> str:
    title = opp.get("title", "Sans titre").strip()
    summary = opp.get("summary", "").strip()
    country = opp.get("country", "").strip()
    level = opp.get("level", "").strip()
    funding = opp.get("funding", "").strip()
    deadline = opp.get("deadline", "").strip()
    benefits = opp.get("benefits", [])

    lines = [f"🎓 {title}\n"]
    if summary:
        lines.append(f"📝 {summary}\n")
    info = []
    if country: info.append(f"🌍 {country}")
    if level: info.append(f"🎯 {level}")
    if funding: info.append(f"💰 {funding}")
    if info: lines.append(" | ".join(info) + "\n")
    if benefits:
        lines.append("✨ *Avantages :*")
        for b in benefits:
            lines.append(f"  • {b}")
        lines.append("")
    if deadline: lines.append(f"⏳ *Deadline :* {deadline}\n")
    tags = []
    if country: tags.append(f"#{country.replace(' ', '_')}")
    if level: tags.append(f"#{level.replace(' ', '_')}")
    if opp.get("source"): tags.append(f"#{opp['source']}")
    if funding and 'fully' in funding.lower(): tags.append("#Fully_Funded")
    if tags: lines.append(" ".join(tags))
    return "\n".join(lines)

async def publish_opportunity(bot, channel_id: int, opp: dict):
    plain = format_opportunity_rich(opp)
    image_url = opp.get("image_url")
    link = opp.get("link", "")
    title = opp.get("title", "")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Apply / Voir l'offre", url=link)]
    ]) if link else None

    # Tentative avec image
    if image_url:
        try:
            await bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=plain,
                reply_markup=keyboard
            )
            print(f"✅ Publié avec image : {title}")
            await asyncio.sleep(10)  # délai après succès
            return
        except (RetryAfter, TimedOut, NetworkError) as e:
            wait = getattr(e, 'retry_after', 30)
            print(f"⏳ Flood/timeout pour {title}, attente {wait}s")
            await asyncio.sleep(wait)
            # On réessaie une fois après l'attente
            try:
                await bot.send_photo(chat_id=channel_id, photo=image_url, caption=plain, reply_markup=keyboard)
                print(f"✅ Publié avec image (2e tentative) : {title}")
                await asyncio.sleep(10)
                return
            except Exception as e2:
                print(f"❌ Échec image pour {title} : {e2}")
        except Exception as e:
            print(f"❌ Erreur image pour {title} : {e}")

    # Fallback texte seul
    try:
        await bot.send_message(
            chat_id=channel_id,
            text=plain,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        print(f"✅ Publié sans image : {title}")
        await asyncio.sleep(10)
    except RetryAfter as e:
        wait = e.retry_after
        print(f"⏳ Flood control texte pour {title}, attente {wait}s")
        await asyncio.sleep(wait)
        await bot.send_message(chat_id=channel_id, text=plain, reply_markup=keyboard, disable_web_page_preview=True)
        print(f"✅ Publié (après flood) : {title}")
        await asyncio.sleep(10)
    except Exception as e:
        print(f"❌ Échec total pour {title} : {e}")