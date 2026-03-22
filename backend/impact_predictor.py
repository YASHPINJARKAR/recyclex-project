import pandas as pd

def calculate_impact(user_id: int, scrap_type: str) -> dict:
    # Impact dictionary: co2 saved per unit (e.g. kg/item)
    impact_factors = {
        "Plastic": 1.5,
        "Metal": 2.5,
        "Paper": 0.8,
        "E-Waste": 3.0
    }
    
    # In a real app we'd query the DB to get weights, here we mock it with a dummy DataFrame
    data = {
        "user_id": [user_id],
        "scrap_type": [scrap_type],
        "weight_kg": [2.0]  # Example 2kg
    }
    
    df = pd.DataFrame(data)
    
    # Calculate CO2 savings
    df["factor"] = df["scrap_type"].map(impact_factors).fillna(1.0)
    df["co2_savings"] = df["weight_kg"] * df["factor"]
    
    savings = float(df["co2_savings"].sum())
    
    return {
        "user_id": user_id,
        "co2_savings": float(f"{savings:.2f}")
    }
