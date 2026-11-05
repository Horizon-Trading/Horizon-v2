import math


def finite(value) -> bool:
    return not isinstance(value,bool) and isinstance(value,(float,int)) and math.isfinite(value)


def performance(history: dict | None) -> dict:
    result={"total_return":None,"max_drawdown":None,"equity_curve":[],"period":"1M"}
    if not isinstance(history,dict):
        return result
    timestamps=history.get("timestamp") or []
    equities=history.get("equity") or []
    pnl=history.get("profit_loss_pct") or []
    result["equity_curve"]=[{"timestamp":time,"equity":equity} for time,equity in zip(timestamps,equities)
                            if finite(time) and finite(equity) and equity>=0]
    # Use the provider's P&L series rather than treating deposits as trading gains.
    if not finite(history.get("base_value")) or history["base_value"]<=0 or not pnl or len(pnl)!=len(timestamps):
        return result
    if not all(finite(value) and value>=-1 for value in pnl):
        return result
    result["total_return"]=pnl[-1]
    peak=1.0
    drawdown=0.0
    for value in pnl:
        level=1+value
        peak=max(peak,level)
        drawdown=max(drawdown,(peak-level)/peak)
    result["max_drawdown"]=drawdown
    return result
