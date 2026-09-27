import streamlit as st
import pandas as pd

from intervention_engine import (
    create_baseline_scores,
    simulate_intervention
)

# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------

st.set_page_config(
    page_title="Mini Sandbox AI",
    page_icon=None,
    layout="wide"
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("chennai_ward_master_dataset.csv")
    df = create_baseline_scores(df)
    return df


df = load_data()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.title("Mini Sandbox AI")

    st.caption("Climate-resilient decision support for Chennai wards")

    st.divider()

    st.subheader("Select Ward")

    # Create clear ward names
    ward_options = {}

    for _, row in df.iterrows():

        label = (
            f"{row['ward_name_en']} "
            f"— Ward {int(row['ward_number'])}"
        )

        ward_options[label] = row["ward_number"]

    selected_label = st.selectbox(
        "Ward",
        list(ward_options.keys()),
        label_visibility="collapsed"
    )

    selected_ward_number = ward_options[selected_label]

    ward = df[
        df["ward_number"] == selected_ward_number
    ].iloc[0]

    st.divider()

    st.subheader("Intervention Scenario")

    interventions = [
        "Rainwater Harvesting",
        "Drainage Improvement",
        "Tree Plantation",
        "Green Roofs",
        "Permeable Surfaces",
        "Rain Gardens"
    ]

    selected_interventions = []

    for intervention in interventions:

        checked = st.checkbox(intervention)

        if checked:
            selected_interventions.append(intervention)

    st.divider()

    st.caption(
        "Simulation results are project-level scenario estimates."
    )


# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------

st.title("Mini Sandbox AI")

st.caption(
    "Climate-resilient intervention simulation for Chennai wards"
)

st.divider()


# ---------------------------------------------------------
# WARD INFORMATION
# ---------------------------------------------------------

st.header(ward["ward_name_en"])

st.caption(
    f"Ward {int(ward['ward_number'])}  |  "
    f"Zone: {ward['zone_name_en']}  |  "
    f"Region: {ward['region_en']}"
)

st.info(
    f"Population: {int(ward['population']):,}   |   "
    f"Area: {ward['area_sqkm']:.2f} km²   |   "
    f"Coastal Zone: {ward['is_coastal_zone']}"
)


# ---------------------------------------------------------
# RISK PROFILE
# ---------------------------------------------------------

st.header("Current Climate Risk")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Flood Risk",
        f"{ward['sandbox_flood_score']:.1f}"
    )

with c2:
    st.metric(
        "Heat Risk",
        f"{ward['sandbox_heat_score']:.1f}"
    )

with c3:
    st.metric(
        "Water Scarcity",
        f"{ward['sandbox_water_score']:.1f}"
    )

with c4:
    st.metric(
        "Climate Vulnerability",
        f"{ward['sandbox_vulnerability_score']:.1f}"
    )

with c5:
    st.metric(
        "Sustainability",
        f"{ward['sandbox_sustainability_score']:.1f}"
    )


# ---------------------------------------------------------
# WARD PROFILE
# ---------------------------------------------------------

st.header("Ward Environmental Profile")

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.metric(
        "Annual Rainfall",
        f"{ward['annual_rainfall_mm']:.0f} mm"
    )

with p2:
    st.metric(
        "Green Cover",
        f"{ward['green_cover_percent']:.1f}%"
    )

with p3:
    st.metric(
        "Drainage Condition",
        f"{ward['drainage_condition_score']:.1f}/100"
    )

with p4:
    st.metric(
        "Groundwater Depth",
        f"{ward['groundwater_depth_m']:.1f} m"
    )


p5, p6, p7, p8 = st.columns(4)

with p5:
    st.metric(
        "Elevation",
        f"{ward['elevation_m']:.1f} m"
    )

with p6:
    st.metric(
        "Population Density",
        f"{ward['population_density_per_sqkm']:,.0f}/km²"
    )

with p7:
    st.metric(
        "Water Supply",
        f"{ward['water_supply_lpcd']:.0f} LPCD"
    )

with p8:
    st.metric(
        "Water Demand",
        f"{ward['water_demand_lpcd']:.0f} LPCD"
    )


# ---------------------------------------------------------
# FLOOD INFORMATION
# ---------------------------------------------------------

st.header("Flood Exposure")

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.metric(
        "Flood Events",
        int(ward["flood_events_count_2015_2023"])
    )

with f2:
    st.metric(
        "Maximum Water Depth",
        f"{ward['flood_max_water_depth_m']:.2f} m"
    )

with f3:
    st.metric(
        "Area Flooded",
        f"{ward['flood_avg_area_flooded_percent']:.1f}%"
    )

with f4:
    st.metric(
        "Households Affected",
        f"{int(ward['flood_total_households_affected']):,}"
    )


# ---------------------------------------------------------
# INTERVENTION SANDBOX
# ---------------------------------------------------------

st.header("Climate Intervention Sandbox")

st.write(
    "Select one or more interventions from the sidebar "
    "and run a scenario for the selected ward."
)

if len(selected_interventions) == 0:

    st.warning(
        "No intervention selected. Select at least one intervention "
        "from the sidebar."
    )

else:

    st.write("Selected interventions:")

    for item in selected_interventions:
        st.write(f"- {item}")

    if st.button(
        "Run Simulation",
        type="primary",
        use_container_width=True
    ):

        result = simulate_intervention(
            ward,
            selected_interventions
        )

        before = result["before"]
        after = result["after"]
        impact = result["impact"]

        st.success("Simulation completed successfully.")

        # -------------------------------------------------
        # BEFORE / AFTER
        # -------------------------------------------------

        st.subheader("Before vs Simulated Scenario")

        r1, r2 = st.columns(2)

        with r1:

            st.markdown("### Current Situation")

            st.metric(
                "Flood Risk",
                f"{before['flood']:.1f}"
            )

            st.metric(
                "Heat Risk",
                f"{before['heat']:.1f}"
            )

            st.metric(
                "Water Scarcity",
                f"{before['water']:.1f}"
            )

            st.metric(
                "Vulnerability",
                f"{before['vulnerability']:.1f}"
            )

            st.metric(
                "Sustainability",
                f"{before['sustainability']:.1f}"
            )

        with r2:

            st.markdown("### Simulated Situation")

            st.metric(
                "Flood Risk",
                f"{after['flood']:.1f}",
                f"{after['flood'] - before['flood']:.1f}"
            )

            st.metric(
                "Heat Risk",
                f"{after['heat']:.1f}",
                f"{after['heat'] - before['heat']:.1f}"
            )

            st.metric(
                "Water Scarcity",
                f"{after['water']:.1f}",
                f"{after['water'] - before['water']:.1f}"
            )

            st.metric(
                "Vulnerability",
                f"{after['vulnerability']:.1f}",
                f"{after['vulnerability'] - before['vulnerability']:.1f}"
            )

            st.metric(
                "Sustainability",
                f"{after['sustainability']:.1f}",
                f"{after['sustainability'] - before['sustainability']:.1f}"
            )


        # -------------------------------------------------
        # IMPACT
        # -------------------------------------------------

        st.subheader("Scenario Impact")

        i1, i2, i3, i4, i5 = st.columns(5)

        with i1:
            st.metric(
                "Flood Reduction",
                f"{impact['flood_reduction_percent']:.1f}%"
            )

        with i2:
            st.metric(
                "Heat Reduction",
                f"{impact['heat_reduction_percent']:.1f}%"
            )

        with i3:
            st.metric(
                "Water Reduction",
                f"{impact['water_reduction_percent']:.1f}%"
            )

        with i4:
            st.metric(
                "Sustainability Gain",
                f"+{impact['sustainability_gain']:.1f}"
            )

        with i5:
            st.metric(
                "Estimated Cost",
                f"₹{result['estimated_cost_lakhs']:.1f} L"
            )


        # -------------------------------------------------
        # CHART
        # -------------------------------------------------

        st.subheader("Current vs Simulated")

        chart_data = pd.DataFrame(
            {
                "Current": [
                    before["flood"],
                    before["heat"],
                    before["water"],
                    before["vulnerability"],
                    before["sustainability"]
                ],
                "Simulated": [
                    after["flood"],
                    after["heat"],
                    after["water"],
                    after["vulnerability"],
                    after["sustainability"]
                ]
            },
            index=[
                "Flood",
                "Heat",
                "Water",
                "Vulnerability",
                "Sustainability"
            ]
        )

        st.bar_chart(chart_data)

        st.caption(
            "Note: Intervention impacts are prototype simulation "
            "assumptions for decision-support demonstration, not "
            "official engineering predictions."
        )


# ---------------------------------------------------------
# PROJECT NOTE
# ---------------------------------------------------------

st.divider()

st.caption(
    "Mini Sandbox AI | Chennai Climate-Resilience Decision Support"
)