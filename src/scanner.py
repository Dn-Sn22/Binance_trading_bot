import asyncio
import json
import logging
import numpy as np
from datetime import datetime
from collections import deque

import websockets

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/scanner.log")
    ]
)
log = logging.getLogger(__name__)

SYMBOL           = config.SYMBOL.lower()
WS_MARKET_URL    = "wss://stream.binance.com:9443"
WS_URL           = f"{WS_MARKET_URL}/ws/{SYMBOL}@trade"
PRINT_EVERY      = 5
HISTORY_SIZE     = 100
ANOMALY_COOLDOWN = 10

prices       = deque(maxlen=HISTORY_SIZE)
volumes      = deque(maxlen=HISTORY_SIZE)
last_print   = 0.0
last_anomaly = 0.0


def detect_anomaly(current: float) -> tuple[bool, float, float]:
    if len(prices) < 20:
        return False, 0.0, 0.0
    arr     = np.array(prices)
    returns = np.diff(np.log(arr))
    if len(returns) < 10:
        return False, 0.0, 0.0
    mean_long     = returns.mean()
    std_long      = returns.std()
    if std_long == 0:
        return False, 0.0, 0.0
    recent_return = returns[-10:].mean()
    z             = (recent_return - mean_long) / std_long
    is_anomaly    = abs(z) > 2.0
    change_pct    = (np.exp(recent_return * 10) - 1) * 100
    return is_anomaly, z, change_pct


def print_status(price: float, volume: float, anomaly: bool, z: float, change_pct: float):
    now        = datetime.now().strftime("%H:%M:%S")
    status     = "!! АНОМАЛИЯ" if anomaly else "ок"
    mean_price = np.mean(prices) if len(prices) > 0 else price
    delta_usd  = price - mean_price
    print(
        f"[{now}] "
        f"BTC: ${price:,.2f} | "
        f"Объём: {volume:.4f} | "
        f"Z: {z:+.2f} | "
        f"Изм: {delta_usd:+.2f}$ ({change_pct:+.3f}%) | "
        f"{status}"
    )


async def process_tick(data: dict):
    global last_print, last_anomaly
    price  = float(data["p"])
    volume = float(data["q"])
    prices.append(price)
    volumes.append(volume)
    anomaly, z, change_pct = detect_anomaly(price)
    if anomaly:
        now_t = asyncio.get_event_loop().time()
        if now_t - last_anomaly >= ANOMALY_COOLDOWN:
            last_anomaly = now_t
            log.warning(f"АНОМАЛИЯ | BTC: ${price:,.2f} | Z: {z:+.2f} | Изм: {change_pct:+.3f}%")
    now = asyncio.get_event_loop().time()
    if now - last_print >= PRINT_EVERY:
        last_print = now
        print_status(price, volume, anomaly, z, change_pct)


async def main():
    log.info(f"Запуск сканера | {config.MODE} | {WS_URL}")
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                log.info("WebSocket подключён")
                async for message in ws:
                    data = json.loads(message)
                    await process_tick(data)
        except Exception as e:
            log.error(f"Ошибка соединения: {e} | Переподключение через 5 сек...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())