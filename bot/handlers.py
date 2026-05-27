from telegram import Update
from telegram.ext import ContextTypes
from models.database import SessionLocal
from models.opportunity import Opportunity
from bot.publisher import format_opportunity

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *Academic Bot* à votre service !\n\n"
        "Je surveille les opportunités académiques (bourses, stages, conférences) "
        "et les publie dans le canal.\n"
        "Commandes disponibles :\n"
        "/latest : Voir les 5 dernières opportunités\n"
        "/status : Vérifier que le bot est en ligne"
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        opps = db.query(Opportunity).order_by(Opportunity.published_at.desc()).limit(5).all()
        if not opps:
            await update.message.reply_text("Aucune opportunité pour le moment.")
            return
        for opp in opps:
            msg = format_opportunity({
                "title": opp.title,
                "summary": opp.summary or "",
                "country": opp.country,
                "level": opp.level,
                "funding": opp.funding,
                "deadline": opp.deadline,
                "link": opp.link,
                "source": opp.source
            })
            await update.message.reply_text(msg, parse_mode="MarkdownV2", disable_web_page_preview=True)
    finally:
        db.close()

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot en ligne et opérationnel.")