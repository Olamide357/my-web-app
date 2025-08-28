from decimal import Decimal

def calculate_fee(amount: Decimal) -> Decimal:
    """Any amount less than 10,000 deducts 50; otherwise 1.5% capped at 2,000."""
    if amount < 10000:
        return Decimal("50.00")
    fee = amount * Decimal("0.015")
    return min(fee, Decimal("2000")).quantize(Decimal("1.00"))
