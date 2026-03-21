import logging
import os
import asyncio

log = logging.getLogger(__name__)

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Graceful degradation — If the token is not set, just remain silent
def telegram_enabled() -> bool:
    return bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)


async def send_message(text: str):
    if not telegram_enabled():
        log.info("Telegram isn't configured — skipping notifications")
        return

    try:
        from telegram import Bot
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="HTML"
        )
        log.info("Telegram notification sent")
    except Exception as e:
        log.error(f"Telegram error: {e}")


async def notify_signal(
    signal: str,
    price: float,
    stop_loss: float,
    z_score: float,
    confidence: float,
    fear_greed_value: int,
    fear_greed_label: str
):
    """Уведомление о входе в сделку."""
    direction = "BULLISH 📈" if signal == "bullish" else "BEARISH 📉"

    text = (
        f"Господин, ваш слуга обнаружил благоприятную возможность.\n\n"
        
        f"📊 BTC/USDT — {direction}\n"
        f"💰 Цена входа: ${price:,.2f}\n"
        f"Стоп-лосс: ${stop_loss:,.2f}\n"
        f"Z-score: {z_score:+.2f}\n"
        f"Уверенность: {confidence}\n"
        f"Fear & Greed: {fear_greed_value} ({fear_greed_label})\n\n"
        f"Как и предусмотрено вашей мудростью, позиция открыта.\n"
        f"Браво, господин. Ваш план безупречен."
    )
    await send_message(text)


async def notify_cryptopanic_disabled():
    """Уведомление об отключении CryptoPanic."""
    text = (
        f"Господин, один из источников разведки временно недоступен.\n"
        f"Назарик продолжает операцию с оставшимися ресурсами."
    )
    await send_message(text)


async def notify_startup(mode: str, balance: float):
    """Уведомление о запуске бота."""
    text = (
        f"🔱 Назарик пробудился и готов служить господину.\n\n"
        f" Режим: {mode.upper()}\n"
        f" Баланс: ${balance:.2f}\n\n"
        f"Слежение за рынком начато. Ваш слуга бдит."
    )
    await send_message(text)