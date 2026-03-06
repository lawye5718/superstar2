def normalize_balance_payload(update_data: dict) -> dict:
    """Map balance to credits if provided."""
    if "balance" in update_data:
        update_data = update_data.copy()
        update_data["credits"] = update_data.pop("balance")
    return update_data
