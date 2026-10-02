import streamlit as st
import math
import pandas as pd

# 1. Configure page settings for a clean engineering theme
st.set_page_config(
    page_title="Pump Bearing Load Calculator",
    page_icon="⚙️",
    layout="wide"
)

# Custom styling for metrics to make them stand out
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #1E3A8A; }
    [data-testid="stMetricLabel"] { font-size: 14px; font-weight: 600; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

# 2. Main Title and App Context
st.title("⚙️ Pump Component & Bearing Load Calculator")
st.markdown("Use this utility to evaluate torque distributions, tangential component loads, and resultant bearing reactions.")

# 3. Sidebar Layout for clean Parameter Input
with st.sidebar:
    st.header("📥 Input Parameters")

    # Using expanders to keep the sidebar neat and grouped
    with st.sidebar.expander("⚡ Power & Speed", expanded=True):
        p_hub = st.number_input(
            "Torsional Power (Hub) [kW]", value=7.5, step=0.1)
        p_impeller = st.number_input(
            "Torsional Power (Impeller) [kW]", value=5.0, step=0.1)
        n_hub = st.number_input(
            "Rotational Speed [rpm]", value=4320.0, step=10.0)

    with st.sidebar.expander("📐 Geometry & Diameters", expanded=True):
        d_hub = st.number_input(
            "Hub Outer Diameter [mm]", value=45.0, step=1.0)
        d_impeller = st.number_input(
            "Impeller Outer Diameter [mm]", value=139.0, step=1.0)

    with st.sidebar.expander("📏 Shaft Distances", expanded=True):
        l_1 = st.number_input("L1 (Hub to Brg A) [mm]", value=30.11, step=0.1)
        l_2 = st.number_input("L2 (Brg A to Brg B) [mm]", value=62.0, step=0.1)
        l_3 = st.number_input(
            "L3 (Impeller to Brg B) [mm]", value=88.5, step=0.1)

    # Centered primary action button
    calculate_btn = st.button(
        "Run Engineering Calculations", type="primary", use_container_width=True)

# 4. Calculation Execution and Result Display Area
if calculate_btn:
    # Your robust safety check validation
    if n_hub <= 0 or d_hub <= 0 or d_impeller <= 0 or l_2 <= 0:
        st.error(
            "🚨 **Validation Error:** Rotational Speed, Diameters, and Distance L2 must be greater than 0.")
    else:
        # --- CORE MATHEMATICAL CALCULATIONS (Your exact engine) ---
        t_hub = (p_hub * 60 * 1000) / (2 * math.pi * n_hub)
        t_impeller = (p_impeller * 60 * 1000) / (2 * math.pi * n_hub)

        f_hub = (2 * t_hub * 1000) / d_hub
        f_hub_act = f_hub * 1.5
        f_impeller = (2 * t_impeller * 1000) / d_impeller

        r_a = (f_hub_act * (l_1 + l_2) - f_impeller * l_3) / l_2
        r_b = f_hub_act + f_impeller - r_a

        r_a_half = r_a / 2
        r_b_half = r_b / 2

        # --- UI LAYOUT FOR RESULTS ---
        st.success("✅ Analysis Complete.")

        # Segmenting outputs using tabs for multi-dimensional analysis
        tab1, tab2, tab3 = st.tabs(
            ["📊 Performance Metrics", "📈 Reaction Charts", "📝 Governing Equations"])

        with tab1:
            # Segment 1: Torques and Component Forces
            st.subheader("⚡ Torques & Component Forces")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(label="Hub Torque (T_hub)", value=f"{t_hub:.4f} N·m")
                st.metric(label="Impeller Torque (T_impeller)",
                          value=f"{t_impeller:.4f} N·m")
            with c2:
                st.metric(label="Hub Tangential Load (F_hub)",
                          value=f"{f_hub:.2f} N")
                st.metric(label="Actual Hub Load (F_hub_act)",
                          value=f"{f_hub_act:.2f} N")
            with c3:
                st.metric(label="Impeller Tangential Load (F_impeller)",
                          value=f"{f_impeller:.2f} N")

            st.divider()

            # Segment 2: Bearing Reactions
            st.subheader("⚙️ Bearing Reaction Forces")
            c4, c5 = st.columns(2)
            with c4:
                st.info("**Bearing A Assembly**")
                st.metric(label="Total Radial Load (R_A)",
                          value=f"{r_a:.4f} N")
                st.metric(label="Load Per Bearing (R_A / 2)",
                          value=f"{r_a_half:.4f} N")
            with c5:
                st.info("**Bearing B Assembly**")
                st.metric(label="Total Radial Load (R_B)",
                          value=f"{r_b:.4f} N")
                st.metric(label="Load Per Bearing (R_B / 2)",
                          value=f"{r_b_half:.4f} N")

        with tab2:
            st.subheader("📈 Bearing Load Comparison")
            # Quick visual chart to let the engineer compare forces immediately
            chart_data = pd.DataFrame({
                "Bearing Location": ["Bearing A (Total)", "Bearing A (Per Brg)", "Bearing B (Total)", "Bearing B (Per Brg)"],
                "Radial Load (N)": [abs(r_a), abs(r_a_half), abs(r_b), abs(r_b_half)]
            })
            st.bar_chart(data=chart_data, x="Bearing Location",
                         y="Radial Load (N)", color="#1E3A8A")

        with tab3:
            st.subheader("📝 Reference System Equations")
            st.markdown(
                "Your calculator utilizes the following fundamental physics implementations:")
            st.latex(r"T = \frac{P \times 60 \times 1000}{2 \pi n}")
            st.latex(r"F = \frac{2 \times T \times 1000}{d}")
            st.latex(
                r"R_A = \frac{F_{hub\_act}(L_1 + L_2) - F_{impeller}(L_3)}{L_2}")

else:
    # Welcoming placeholder state before execution
    st.info("👈 Configure your operating parameters in the sidebar panel and click **Run Engineering Calculations**.")
