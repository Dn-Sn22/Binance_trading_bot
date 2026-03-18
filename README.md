# Binance Trading Bot

AI-powered торговый бот для BTC/USDT на Binance.
Строится поэтапно — от сканера до полного пайплайна с управлением рисками.

## Статус разработки

| Модуль | Статус | Описание |
|--------|--------|----------|
| `config.py` |  Готов | Переключение testnet/live |
| `scanner.py` |  Готов | WebSocket + Z-score аномалии |
| `research.py` |  В разработке | Новости + sentiment через Claude |
| `risk.py` |  Впереди | Kelly Criterion, VaR, drawdown |
| `executor.py` |  Впереди | Выставление ордеров на Binance |

## Архитектура
```
scanner.py → research.py → risk.py → executor.py
   ↓              ↓            ↓           ↓
Цена BTC      Новости       Размер      Ордер на
Z-score       Sentiment     позиции     Binance
аномалии      Claude API    Kelly       Testnet
```

## Установка
```bash
# Клонировать репозиторий
git clone https://github.com/Dn-Sn22/Binance_trading_bot.git
cd Binance_trading_bot

# Создать окружение
conda create -n botenv python=3.11 -y
conda activate botenv
conda install pandas numpy -y
pip install -r requirements.txt

# Настроить ключи
cp .env.example .env
# Заполнить .env своими ключами Binance
```

## Запуск сканера
```bash
conda activate botenv
cd Binance_trading_bot
python src/scanner.py
```

## Переменные окружения
```
BINANCE_API_KEY=           # Live API ключ
BINANCE_SECRET_KEY=        # Live Secret ключ
BINANCE_TESTNET_API_KEY=   # Testnet API ключ
BINANCE_TESTNET_SECRET_KEY= # Testnet Secret ключ
TRADING_MODE=testnet       # testnet или live
```

## Технологии

- Python 3.11
- Binance WebSocket API — живой поток цен
- Z-score — статистическое обнаружение аномалий
- Claude API — анализ новостей и sentiment
- Kelly Criterion — математический расчёт размера позиции
- Anaconda — управление окружением

## Безопасность

- `.env` файл никогда не попадает в репозиторий
- API ключи без права вывода средств
- Всё тестируется на Testnet перед реальными деньгами

## Roadmap

- [x] Базовая структура проекта
- [x] Конфигурация testnet/live
- [x] WebSocket сканер с Z-score
- [ ] Research модуль — новости + Claude sentiment
- [ ] Risk модуль — Kelly, VaR, drawdown защита
- [ ] Executor — лимитные ордера на Binance
- [ ] Dashboard — метрики и логи в реальном времени
- [ ] Paper trading 2+ недели
```