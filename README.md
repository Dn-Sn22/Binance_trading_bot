# BTC Trading Bot

AI-powered торговый бот для BTC/USDT на Binance.
Построен с нуля студентом за один день как долгосрочный проект.

## Идея

Бот следит за рынком 24/7 вместо человека. Цель — предвидеть
когда BTC начнёт падать, уйти в USDT, поймать коррекцию и вернуться в плюс.
Сейчас работает в режиме paper trading на Testnet.

## Как работает

Два условия должны совпасть одновременно чтобы бот вошёл в сделку:

1. **Scanner** поймал аномалию цены (Z-score > 2.0)
2. **Research** получил сильный сигнал от новостей (confidence > 0.70)

Только тогда **Risk** считает размер позиции и **Executor** выставляет ордер.

## Архитектура
```
scanner.py   →  реал-тайм цена BTC через WebSocket
                аномалии через Z-score логдоходностей

research.py  →  новости каждые 5 минут
                CryptoPanic + CoinTelegraph RSS + Fear & Greed Index
                sentiment анализ через Claude API (bullish/bearish/neutral)

risk.py      →  6 уровней защиты капитала
                Kelly Criterion для размера позиции
                состояние сохраняется в risk_state.json

executor.py  →  лимитный ордер + стоп-лосс на Binance
                dry-run режим — реальных денег не тратит

main.py      →  оркестратор всех модулей
                три async задачи параллельно
                логирует каждую сделку в logs/trades.csv
```

## Параметры риска

| Параметр | Значение |
|----------|----------|
| Стартовый депозит | $100 |
| Размер позиции | макс 5% депозита |
| Стоп-лосс | 8% |
| Макс позиций | 3 одновременно |
| Дневной лимит потерь | 10% |
| Макс просадка | 25% |
| Cooldown между входами | 60 сек |
| Min confidence сигнала | 0.70 |

## Установка
```bash
git clone https://github.com/Dn-Sn22/Binance_trading_bot.git
cd Binance_trading_bot

conda create -n botenv python=3.11 -y
conda activate botenv
conda install pandas numpy -y
pip install -r requirements.txt

cp .env.example .env
# Заполнить .env своими ключами
```

## Запуск
```bash
conda activate botenv
cd Binance_trading_bot
python main.py
```

Остановить — `Ctrl + C`

## Переменные окружения
```
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
BINANCE_TESTNET_API_KEY=
BINANCE_TESTNET_SECRET_KEY=
TRADING_MODE=testnet
CRYPTOPANIC_API_KEY=
ANTHROPIC_API_KEY=
```

## Структура проекта
```
Binance_trading_bot/
├── main.py              # оркестратор
├── config.py            # настройки и ключи
├── requirements.txt
├── .env.example
├── src/
│   ├── scanner.py       # WebSocket + Z-score
│   ├── research.py      # новости + Claude sentiment
│   ├── risk.py          # Kelly + защита капитала
│   └── executor.py      # ордера на Binance
└── logs/
    ├── main.log
    ├── scanner.log
    ├── research.log
    └── trades.csv       # история сделок
```

## Статус модулей

| Модуль | Статус |
|--------|--------|
| scanner.py | ✅ Готов |
| research.py | ✅ Готов |
| risk.py | ✅ Готов |
| executor.py | ✅ Готов |
| main.py | ✅ Готов |
| Логика выхода из сделки | 🔄 В разработке |
| Dashboard с метриками | 🔄 В разработке |
| Backtesting | ⏳ Впереди |

## Roadmap

- [x] WebSocket сканер с Z-score логдоходностей
- [x] Research агент — CryptoPanic + RSS + Fear & Greed
- [x] Claude sentiment анализ (bullish/bearish/neutral)
- [x] Risk менеджер — Kelly Criterion + 6 защит
- [x] Executor — лимитные ордера + стоп-лосс
- [x] Оркестратор — три async задачи параллельно
- [x] Логирование сделок в trades.csv
- [ ] Логика выхода из сделки
- [ ] Dashboard — метрики в реальном времени
- [ ] Визуализация trades.csv
- [ ] Backtesting на исторических данных
- [ ] Переход на реальный спот после paper trading

## Технологии

- Python 3.11 + asyncio
- Binance WebSocket API
- Claude API (Anthropic) — sentiment анализ
- CryptoPanic API — крипто новости
- Kelly Criterion — управление капиталом
- Z-score логдоходностей — обнаружение аномалий
- Anaconda — управление окружением

## Безопасность

- `.env` никогда не попадает в репозиторий
- API ключи без права вывода средств
- `DRY_RUN = True` — реальных ордеров нет
- Всё тестируется на Testnet