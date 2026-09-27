import pandas as pd
import numpy as np


# ============================================================
# MINI SANDBOX AI
# CLIMATE-RESILIENT INTERVENTION ENGINE
# ============================================================


# ------------------------------------------------------------
# Utility function
# ------------------------------------------------------------

def normalize_series(series):
    """
    Converts a numeric column into a 0-100 scale.
    Higher original value = higher score.
    """

    series = pd.to_numeric(series, errors="coerce")

    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(50.0, index=series.index)

    if maximum == minimum:
        return pd.Series(50.0, index=series.index)

    return ((series - minimum) / (maximum - minimum)) * 100


def inverse_score(series):
    """
    Higher original value = lower risk.
    Converts it to a 0-100 risk scale.
    """

    return 100 - normalize_series(series)


# ============================================================
# CREATE BASELINE CLIMATE SCORES
# ============================================================

def create_baseline_scores(df):

    data = df.copy()

    # --------------------------------------------------------
    # FLOOD RISK
    # --------------------------------------------------------

    flood_severity = normalize_series(
        data["flood_max_local_severity_score"]
    )

    flood_area = normalize_series(
        data["flood_avg_area_flooded_percent"]
    )

    flood_depth = normalize_series(
        data["flood_max_water_depth_m"]
    )

    flood_events = normalize_series(
        data["flood_events_count_2015_2023"]
    )

    rainfall = normalize_series(
        data["max_daily_rainfall_mm_2015_2023"]
    )

    drainage_problem = inverse_score(
        data["drainage_condition_score"]
    )

    flood_score = (
        flood_severity * 0.25
        + flood_area * 0.20
        + flood_depth * 0.20
        + flood_events * 0.10
        + rainfall * 0.15
        + drainage_problem * 0.10
    )

    data["sandbox_flood_score"] = flood_score.clip(0, 100)


    # --------------------------------------------------------
    # HEAT RISK
    # --------------------------------------------------------

    temperature = normalize_series(
        data["avg_max_temp_c"]
    )

    heatwave = normalize_series(
        data["heatwave_days_per_year"]
    )

    population_density = normalize_series(
        data["population_density_per_sqkm"]
    )

    low_green_cover = inverse_score(
        data["green_cover_percent"]
    )

    low_ndvi = inverse_score(
        data["ndvi_avg"]
    )

    heat_score = (
        temperature * 0.30
        + heatwave * 0.25
        + population_density * 0.20
        + low_green_cover * 0.15
        + low_ndvi * 0.10
    )

    data["sandbox_heat_score"] = heat_score.clip(0, 100)


    # --------------------------------------------------------
    # WATER SCARCITY
    # --------------------------------------------------------

    rainfall_low = inverse_score(
        data["annual_rainfall_mm"]
    )

    groundwater = normalize_series(
        data["groundwater_depth_m"]
    )

    water_demand = normalize_series(
        data["water_demand_lpcd"]
    )

    supply = pd.to_numeric(
        data["water_supply_lpcd"],
        errors="coerce"
    )

    demand = pd.to_numeric(
        data["water_demand_lpcd"],
        errors="coerce"
    )

    supply_demand_ratio = supply / demand.replace(0, np.nan)

    supply_gap = inverse_score(
        supply_demand_ratio
    )

    water_score = (
        rainfall_low * 0.20
        + groundwater * 0.30
        + water_demand * 0.20
        + supply_gap * 0.30
    )

    data["sandbox_water_score"] = water_score.clip(0, 100)


    # --------------------------------------------------------
    # SUSTAINABILITY
    # Higher = better
    # --------------------------------------------------------

    green = normalize_series(
        data["green_cover_percent"]
    )

    ndvi = normalize_series(
        data["ndvi_avg"]
    )

    drainage = normalize_series(
        data["drainage_condition_score"]
    )

    water_balance = normalize_series(
        supply_demand_ratio
    )

    sustainability = (
        green * 0.30
        + ndvi * 0.20
        + drainage * 0.25
        + water_balance * 0.25
    )

    data["sandbox_sustainability_score"] = (
        sustainability.clip(0, 100)
    )


    # --------------------------------------------------------
    # CLIMATE VULNERABILITY
    # --------------------------------------------------------

    data["sandbox_vulnerability_score"] = (
        (
            data["sandbox_flood_score"]
            + data["sandbox_heat_score"]
            + data["sandbox_water_score"]
        ) / 3
    ).clip(0, 100)


    return data


# ============================================================
# INTERVENTION SIMULATION
# ============================================================

def simulate_intervention(ward, interventions):

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    flood_score = float(
        ward["sandbox_flood_score"]
    )

    heat_score = float(
        ward["sandbox_heat_score"]
    )

    water_score = float(
        ward["sandbox_water_score"]
    )

    vulnerability_score = float(
        ward["sandbox_vulnerability_score"]
    )

    sustainability_score = float(
        ward["sandbox_sustainability_score"]
    )


    # --------------------------------------------------------
    # INTERVENTION ASSUMPTIONS
    #
    # These are simulation assumptions for the prototype.
    # They are NOT engineering guarantees.
    # --------------------------------------------------------

    intervention_effects = {

        "Rainwater Harvesting": {
            "flood": 10,
            "heat": 2,
            "water": 25,
            "sustainability": 12,
            "cost": 15
        },

        "Drainage Improvement": {
            "flood": 25,
            "heat": 0,
            "water": 5,
            "sustainability": 10,
            "cost": 50
        },

        "Tree Plantation": {
            "flood": 8,
            "heat": 20,
            "water": 5,
            "sustainability": 15,
            "cost": 20
        },

        "Green Roofs": {
            "flood": 6,
            "heat": 15,
            "water": 4,
            "sustainability": 12,
            "cost": 30
        },

        "Permeable Surfaces": {
            "flood": 15,
            "heat": 5,
            "water": 8,
            "sustainability": 10,
            "cost": 35
        },

        "Rain Gardens": {
            "flood": 12,
            "heat": 6,
            "water": 10,
            "sustainability": 11,
            "cost": 25
        }
    }


    # --------------------------------------------------------
    # Calculate intervention effects
    # --------------------------------------------------------

    flood_reduction = 0
    heat_reduction = 0
    water_reduction = 0
    sustainability_gain = 0
    total_cost = 0


    for intervention in interventions:

        if intervention in intervention_effects:

            effect = intervention_effects[intervention]

            flood_reduction += effect["flood"]
            heat_reduction += effect["heat"]
            water_reduction += effect["water"]
            sustainability_gain += effect["sustainability"]
            total_cost += effect["cost"]


    # Prevent unrealistic combined effects

    flood_reduction = min(
        flood_reduction,
        70
    )

    heat_reduction = min(
        heat_reduction,
        70
    )

    water_reduction = min(
        water_reduction,
        70
    )

    sustainability_gain = min(
        sustainability_gain,
        50
    )


    # --------------------------------------------------------
    # AFTER SIMULATION
    # --------------------------------------------------------

    after_flood = max(
        0,
        flood_score * (
            1 - flood_reduction / 100
        )
    )

    after_heat = max(
        0,
        heat_score * (
            1 - heat_reduction / 100
        )
    )

    after_water = max(
        0,
        water_score * (
            1 - water_reduction / 100
        )
    )

    after_sustainability = min(
        100,
        sustainability_score
        + sustainability_gain
    )


    after_vulnerability = (
        after_flood
        + after_heat
        + after_water
    ) / 3


    # --------------------------------------------------------
    # RETURN RESULTS
    # --------------------------------------------------------

    return {

        "selected_interventions": interventions,

        "before": {
            "flood": round(flood_score, 2),
            "heat": round(heat_score, 2),
            "water": round(water_score, 2),
            "vulnerability": round(
                vulnerability_score,
                2
            ),
            "sustainability": round(
                sustainability_score,
                2
            )
        },

        "after": {
            "flood": round(
                after_flood,
                2
            ),
            "heat": round(
                after_heat,
                2
            ),
            "water": round(
                after_water,
                2
            ),
            "vulnerability": round(
                after_vulnerability,
                2
            ),
            "sustainability": round(
                after_sustainability,
                2
            )
        },

        "impact": {

            "flood_reduction_percent":
                round(
                    flood_reduction,
                    2
                ),

            "heat_reduction_percent":
                round(
                    heat_reduction,
                    2
                ),

            "water_reduction_percent":
                round(
                    water_reduction,
                    2
                ),

            "sustainability_gain":
                round(
                    sustainability_gain,
                    2
                )
        },

        "estimated_cost_lakhs":
            round(
                total_cost,
                2
            )
    }


# ============================================================
# TEST THE ENGINE
# ============================================================

if __name__ == "__main__":

    print("\n====================================")
    print("MINI SANDBOX AI")
    print("INTERVENTION ENGINE TEST")
    print("====================================")

    # Load current master dataset
    df = pd.read_csv(
        "chennai_ward_master_dataset.csv"
    )

    print("\nDataset loaded successfully.")

    print(
        "Total wards:",
        len(df)
    )

    # Create baseline scores
    df = create_baseline_scores(df)

    print(
        "Baseline climate scores created."
    )

    # Select first ward
    ward = df.iloc[0]

    print(
        "\nSelected Ward:",
        ward["ward_name_en"]
    )

    # Test interventions
    selected = [
        "Rainwater Harvesting",
        "Tree Plantation",
        "Drainage Improvement"
    ]

    result = simulate_intervention(
        ward,
        selected
    )

    print("\n------------------------------------")
    print("SELECTED INTERVENTIONS")
    print("------------------------------------")

    for item in selected:
        print("-", item)

    print("\n------------------------------------")
    print("BEFORE")
    print("------------------------------------")

    print(
        "Flood Risk:",
        result["before"]["flood"]
    )

    print(
        "Heat Risk:",
        result["before"]["heat"]
    )

    print(
        "Water Scarcity:",
        result["before"]["water"]
    )

    print(
        "Vulnerability:",
        result["before"]["vulnerability"]
    )

    print(
        "Sustainability:",
        result["before"]["sustainability"]
    )

    print("\n------------------------------------")
    print("AFTER SIMULATION")
    print("------------------------------------")

    print(
        "Flood Risk:",
        result["after"]["flood"]
    )

    print(
        "Heat Risk:",
        result["after"]["heat"]
    )

    print(
        "Water Scarcity:",
        result["after"]["water"]
    )

    print(
        "Vulnerability:",
        result["after"]["vulnerability"]
    )

    print(
        "Sustainability:",
        result["after"]["sustainability"]
    )

    print("\n------------------------------------")
    print("SIMULATION IMPACT")
    print("------------------------------------")

    print(
        "Flood reduction:",
        result["impact"]["flood_reduction_percent"],
        "%"
    )

    print(
        "Heat reduction:",
        result["impact"]["heat_reduction_percent"],
        "%"
    )

    print(
        "Water reduction:",
        result["impact"]["water_reduction_percent"],
        "%"
    )

    print(
        "Sustainability gain:",
        result["impact"]["sustainability_gain"]
    )

    print(
        "Estimated cost:",
        "₹",
        result["estimated_cost_lakhs"],
        "Lakhs"
    )

    print("\n====================================")
    print("TEST COMPLETED")
    print("====================================")