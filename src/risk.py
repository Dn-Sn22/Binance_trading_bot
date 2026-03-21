import logging
import json
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

log = logging.getLogger(__name__)

KELLY_FRACTION   = 0.25
MAX_POSITION_PCT = 0.05
MAX_POSITIONS    = 10
MIN_CONFIDENCE   = 0.70
DAILY_LOSS_LIMIT = 0.10
MAX_DRAWDOWN     = 0.25
STOP_LOSS_PCT    = 0.08

STATE_FILE = Path("risk_state.json")


@dataclass
class RiskState:
    balance:        float
    peak_balance:   float
    daily_start:    float
    daily_date:     str
    open_positions: int   = 0
    daily_loss:     float = 0.0
    total_trades:   int   = 0
    blocked:        bool  = False


@dataclass
class RiskDecision:
    allowed:       bool
    reason:        str
    position_size: float
    stop_loss:     float
    kelly_pct:     float


def load_state() -> RiskState:
    """Loads a state from a file or creates a new one."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            log.info(f"State loaded | Balance: ${data['balance']:.2f}")
            return RiskState(**data)
        except Exception as e:
            log.error(f"Error loading state: {e} — creating new")

    log.info("New state | Balance: $100.00")
    return RiskState(
        balance=100.0,
        peak_balance=100.0,
        daily_start=100.0,
        daily_date=date.today().isoformat()
    )


def save_state(state: RiskState):
    """Saves the state to a file."""
    try:
        data = asdict(state)
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Error saving state: {e}")


def unblock_bot(state: RiskState) -> bool:
    """Unblock the bot manually if you have recovered 50% of the drawdown."""
    if state.blocked:
        peak = state.peak_balance
        if state.balance > peak * 0.5:
            state.blocked = False
            log.info("Bot unblocked")
            save_state(state)
            return True
        else:
            log.warning(
                f"Unlocking is not possible | "
                f"Balance ${state.balance:.2f} < 50% peak ${peak * 0.5:.2f}"
            )
            return False
    return True


def kelly_position_size(
    balance: float,
    win_rate: float,
    avg_win: float,
    avg_loss: float
) -> float:
    """Calculates position size using the Kelly formula."""
    if avg_loss == 0:
        return 0.0

    p = win_rate
    q = 1 - win_rate
    b = avg_win / avg_loss

    kelly_full     = max(0.0, (p * b - q) / b)
    kelly_fraction = min(kelly_full * KELLY_FRACTION, MAX_POSITION_PCT)
    position_usd   = balance * kelly_fraction

    return round(position_usd, 2)


def check_risk(
    state: RiskState,
    signal: str,
    confidence: float,
    current_price: float,
    win_rate: float = config.WIN_RATE,
    avg_win: float  = config.AVG_WIN,
    avg_loss: float = config.AVG_LOSS
) -> RiskDecision:
    """Main risk check function."""

    # Update daily limits if it's a new day
    today = date.today().isoformat()
    if state.daily_date != today:
        state.daily_date  = today
        state.daily_start = state.balance
        state.daily_loss  = 0.0
        log.info(f"New Day - Limit Reset | Balance: ${state.balance:.2f}")

    def deny(reason: str) -> RiskDecision:
        return RiskDecision(
            allowed=False, reason=reason,
            position_size=0.0, stop_loss=0.0, kelly_pct=0.0
        )

    if state.blocked:
        return deny("Bot is blocked")

    if signal == "neutral":
        return deny("Signal neutral - no entry")

    if confidence < MIN_CONFIDENCE:
        return deny(f"Confidence {confidence:.2f} below threshold {MIN_CONFIDENCE}")

    if state.open_positions >= MAX_POSITIONS:
        return deny(f"Open positions {state.open_positions} - maximum")

    daily_loss_pct = state.daily_loss / state.daily_start if state.daily_start > 0 else 0
    if daily_loss_pct >= DAILY_LOSS_LIMIT:
        return deny(f"Daily limit {daily_loss_pct*100:.1f}% — stop")

    drawdown = (state.peak_balance - state.balance) / state.peak_balance
    if drawdown >= MAX_DRAWDOWN:
        state.blocked = True
        save_state(state)
        return deny(f"Drawdown {drawdown*100:.1f}% — bot blocked")

    position_size = kelly_position_size(state.balance, win_rate, avg_win, avg_loss)
    if position_size < 1.0:
        return deny(f"Position size ${position_size:.2f} is too small")

    stop_loss_price = (
        current_price * (1 - STOP_LOSS_PCT) if signal == "bullish"
        else current_price * (1 + STOP_LOSS_PCT)
    )
    kelly_pct = (position_size / state.balance) * 100

    log.info(
        f"Risk OK | {signal} | "
        f"Size: ${position_size:.2f} ({kelly_pct:.1f}%) | "
        f"Stop: ${stop_loss_price:,.2f}"
    )

    return RiskDecision(
        allowed=True,
        reason="All checks have been passed",
        position_size=position_size,
        stop_loss=round(stop_loss_price, 2),
        kelly_pct=round(kelly_pct, 2)
    )


def update_state_after_trade(state: RiskState, pnl: float) -> RiskState:
    """Updates the status after a deal is closed."""
    state.balance        += pnl
    state.total_trades   += 1
    state.open_positions  = max(0, state.open_positions - 1)

    if pnl < 0:
        state.daily_loss += abs(pnl)

    if state.balance > state.peak_balance:
        state.peak_balance = state.balance

    save_state(state)

    log.info(
        f"The deal is closed | PnL: {pnl:+.2f}$ | "
        f"Balance: ${state.balance:.2f} | "
        f"Drawdown: {((state.peak_balance - state.balance) / state.peak_balance)*100:.1f}%"
    )
    return state


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    state = load_state()

    print("\n--- Test risk.py ---")

    decision = check_risk(state, "bullish", 0.85, 74000.0)
    print(f"Test 1 (bullish 0.85): {decision.allowed} | {decision.reason} | ${decision.position_size}")

    decision = check_risk(state, "bullish", 0.50, 74000.0)
    print(f"Test 2 (conf 0.50):    {decision.allowed} | {decision.reason}")

    decision = check_risk(state, "neutral", 0.90, 74000.0)
    print(f"Test 3 (neutral):      {decision.allowed} | {decision.reason}")

    state.daily_loss = 11.0
    decision = check_risk(state, "bullish", 0.85, 74000.0)
    print(f"Test 4 (daily loss):   {decision.allowed} | {decision.reason}")