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
    direction = "BULLISH" if signal == "bullish" else "BEARISH"

    text = (
        f"Господин, ваш слуга обнаружил благоприятную возможность.\n\n"
        
        f"📊 BTC/USDT — {direction}\n"
        f"Цена входа: ${price:,.2f}\n"
        f"Стоп-лосс: ${stop_loss:,.2f}\n"
        f"Z-score: {z_score:+.2f}\n"
        f"Уверенность: {confidence}\n"
        f"Fear & Greed: {fear_greed_value} ({fear_greed_label})\n\n"
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
    
    
async def notify_position_closed(
    signal: str,
    entry_price: float,
    exit_price: float,
    pnl: float,
    pct: float,
    reason: str,
    order_id: str
):
   
   
    """Уведомление о закрытии позиции."""
    direction = "BULLISH" if signal == "bullish" else "BEARISH"
    
    text = (
        f"Позиция закрыта\n\n"
        f" {direction}\n"
        f"Вход: ${entry_price:,.2f}\n"
        f"Выход: ${exit_price:,.2f}\n"
        f"PnL: {pct:+.2f}% (${pnl:+.4f})\n"
        f" Причина: {'Тейк-профит' if 'TP' in reason else ('Стоп-лосс' if 'SL' in reason else ('Таймаут 12ч' if 'Time limit' in reason else 'Реверс сигнала'))}\n"
        f"ID: {order_id}\n\n"
        f"Как и предусмотрено вашей мудростью, позиция закрыта."
    )
    await send_message(text)

async def notify_shutdown(balance: float, open_positions: int, total_trades: int):
    """Notification on bot shutdown (Ctrl+C)."""
    text = (
        f"Остановка работы бота (KeyboardInterrupt).\n\n"
        f"Баланс: ${balance:.2f}\n"
        f"Открытые позиции: {open_positions}\n"
        f"Всего сделок: {total_trades}"
    )
    await send_message(text)
