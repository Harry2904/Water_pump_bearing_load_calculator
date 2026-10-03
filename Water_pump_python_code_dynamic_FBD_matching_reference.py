import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

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

        belt_tension_factor = st.number_input(
            "V-Belt Tension Factor (K_b)",
            value=1.5,
            min_value=0.0,
            step=0.1,
            help=(
                "User-defined factor used to account for the V-belt tension "
                "effect on the hub load."
            )
        )

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
    if (n_hub <= 0 or d_hub <= 0 or d_impeller <= 0 or l_2 <= 0
            or l_1 < 0 or l_3 < 0 or belt_tension_factor < 0):
        st.error(
            "🚨 **Validation Error:** RPM, diameters, and L2 must be greater than 0. L1/L3 cannot be negative.")
    else:
        # --- CORE MATHEMATICAL CALCULATIONS (Your exact engine) ---
        t_hub = (p_hub * 60 * 1000) / (2 * math.pi * n_hub)
        t_impeller = (p_impeller * 60 * 1000) / (2 * math.pi * n_hub)

        f_hub = (2 * t_hub * 1000) / d_hub
        f_hub_act = f_hub * belt_tension_factor
        f_impeller = (2 * t_impeller * 1000) / d_impeller

        r_a = (f_hub_act * (l_1 + l_2) - f_impeller * l_3) / l_2
        r_b = f_hub_act + f_impeller - r_a

        r_a_half = r_a / 2
        r_b_half = r_b / 2

        # --- UI LAYOUT FOR RESULTS ---
        st.success("✅ Analysis Complete.")

        # Segmenting outputs using tabs for multi-dimensional analysis
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Performance Metrics", "📈 Reaction Charts", "📐 Free Body Diagram", "📝 Governing Equations"])

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
                "Radial Load (N)": [(r_a), (r_a_half), (r_b), (r_b_half)]
            })
            st.bar_chart(data=chart_data, x="Bearing Location",
                         y="Radial Load (N)", color="#1E3A8A")

        with tab3:
            st.subheader(
                "📐 Static Equilibrium Loading Diagram — Water Pump Shaft")

            st.markdown(
                "This dynamic FBD follows the shaft arrangement provided for the pump: "
                "the V-belt/hub load acts downward at the left, the impeller resisting "
                "load acts downward at the right, and the bearing reactions act at "
                "Bearings A and B."
            )

            # -------------------------------------------------------------
            # Dynamic FBD
            # d1 = hub load to Bearing A
            # d2 = Bearing A to Bearing B
            # d3 = Bearing B to impeller load
            # -------------------------------------------------------------
            x_hub = 0.0
            x_a = l_1
            x_b = l_1 + l_2
            x_imp = l_1 + l_2 + l_3
            x_span = max(x_imp, 1.0)

            fig, ax = plt.subplots(figsize=(13, 6.8))

            # Shaft body
            shaft_y = 0.0
            shaft_h = 0.18
            ax.add_patch(
                plt.Rectangle(
                    (x_hub, shaft_y - shaft_h / 2),
                    x_span,
                    shaft_h,
                    fill=False,
                    linewidth=2.2
                )
            )

            # Shaft centerline
            ax.plot(
                [x_hub, x_imp],
                [shaft_y, shaft_y],
                linestyle="--",
                linewidth=1.0
            )

            # Hub / pulley representation
            hub_radius = 0.42
            ax.add_patch(
                plt.Rectangle(
                    (x_hub - 0.12 * x_span / 20, -hub_radius),
                    max(0.12 * x_span / 20, 0.12),
                    2 * hub_radius,
                    fill=False,
                    linewidth=2.0
                )
            )

            # Bearing symbols
            def draw_bearing(x, label, subtitle):
                bearing_w = max(0.045 * x_span, 2.5)
                bearing_h = 0.70

                # dashed bearing housing
                ax.add_patch(
                    plt.Rectangle(
                        (x - bearing_w / 2, -bearing_h / 2),
                        bearing_w,
                        bearing_h,
                        fill=False,
                        linestyle="--",
                        linewidth=1.2
                    )
                )

                # bearing support blocks
                ax.add_patch(
                    plt.Rectangle(
                        (x - bearing_w * 0.34, -0.31),
                        bearing_w * 0.68,
                        0.10,
                        fill=False,
                        linewidth=1.3
                    )
                )
                ax.add_patch(
                    plt.Rectangle(
                        (x - bearing_w * 0.34, 0.21),
                        bearing_w * 0.68,
                        0.10,
                        fill=False,
                        linewidth=1.3
                    )
                )

                # bearing circles
                ax.scatter(
                    [x], [0.22], s=260, facecolors="white",
                    edgecolors="black", linewidths=1.5, zorder=5
                )
                ax.scatter(
                    [x], [-0.22], s=260, facecolors="white",
                    edgecolors="black", linewidths=1.5, zorder=5
                )

                ax.text(
                    x, 0.78, label,
                    ha="center", va="bottom",
                    fontsize=11, fontweight="bold"
                )
                ax.text(
                    x, 0.63, subtitle,
                    ha="center", va="bottom",
                    fontsize=9
                )

            draw_bearing(x_a, "Bearing A", "(Fixed)")
            draw_bearing(x_b, "Bearing B", "(Floating)")

            # Impeller representation
            imp_w = max(0.035 * x_span, 2.0)
            imp_h = 1.0
            ax.add_patch(
                plt.Rectangle(
                    (x_imp - imp_w / 2, -imp_h / 2),
                    imp_w,
                    imp_h,
                    fill=False,
                    linewidth=2.0
                )
            )
            ax.plot(
                [x_imp + imp_w / 2, x_imp + imp_w /
                    2 + max(0.025*x_span, 1.5)],
                [0, 0],
                linewidth=2.0
            )

            # Force arrows
            top_force_y = 1.65
            arrow_base_y = 1.48

            # Hub / V-belt force
            ax.annotate(
                "",
                xy=(x_hub, 0.30),
                xytext=(x_hub, top_force_y),
                arrowprops=dict(arrowstyle="-|>", linewidth=3.0)
            )
            ax.text(
                x_hub, top_force_y + 0.12,
                r"$F_{\mathrm{drive}}$",
                ha="center", va="bottom",
                fontsize=13, fontweight="bold"
            )
            ax.text(
                x_hub, top_force_y - 0.28,
                f"(V-belt / hub load = {f_hub_act:.2f} N)",
                ha="center", va="top", fontsize=9
            )

            # Impeller resisting force
            ax.annotate(
                "",
                xy=(x_imp, 0.30),
                xytext=(x_imp, top_force_y),
                arrowprops=dict(arrowstyle="-|>", linewidth=3.0)
            )
            ax.text(
                x_imp, top_force_y + 0.12,
                r"$F_{\mathrm{resist}}$",
                ha="center", va="bottom",
                fontsize=13, fontweight="bold"
            )
            ax.text(
                x_imp, top_force_y - 0.28,
                f"(Impeller load = {f_impeller:.2f} N)",
                ha="center", va="top", fontsize=9
            )

            # Bearing reactions. Direction follows the sign of the reaction.
            def draw_reaction(x, value, name):
                if value >= 0:
                    y0, y1 = -1.05, -0.25
                else:
                    y0, y1 = -0.25, -1.05

                ax.annotate(
                    "",
                    xy=(x, y1),
                    xytext=(x, y0),
                    arrowprops=dict(arrowstyle="-|>", linewidth=3.0)
                )

                ax.text(
                    x, -1.25,
                    rf"${name}$",
                    ha="center", va="top",
                    fontsize=13, fontweight="bold"
                )
                ax.text(
                    x, -1.48,
                    f"(Vertical reaction = {value:.2f} N)",
                    ha="center", va="top", fontsize=9
                )

            draw_reaction(x_a, r_a, "R_A")
            draw_reaction(x_b, r_b, "R_B")

            # Dimension lines
            dim_y1 = -1.85
            dim_y2 = -2.15

            def dimension_line(x1, x2, label, y):
                ax.annotate(
                    "",
                    xy=(x2, y),
                    xytext=(x1, y),
                    arrowprops=dict(arrowstyle="<->", linewidth=1.5)
                )
                ax.text(
                    (x1 + x2) / 2,
                    y - 0.10,
                    label,
                    ha="center", va="top",
                    fontsize=10
                )

            dimension_line(
                x_hub, x_a, rf"$d_1 = {l_1:.2f}\ \mathrm{{mm}}$", dim_y1)
            dimension_line(
                x_a, x_b, rf"$d_2 = {l_2:.2f}\ \mathrm{{mm}}$", dim_y2)
            dimension_line(
                x_b, x_imp, rf"$d_3 = {l_3:.2f}\ \mathrm{{mm}}$", dim_y1)

            # Section diameter information
            ax.text(
                x_hub + max(0.04*x_span, 1.5),
                0.38,
                rf"$\varnothing\ {d_hub:.1f}\ \mathrm{{mm}}$ Hub",
                ha="left", va="bottom", fontsize=10
            )
            ax.text(
                x_imp + max(0.04*x_span, 1.5),
                0.38,
                rf"$\varnothing\ {d_impeller:.1f}\ \mathrm{{mm}}$ Impeller",
                ha="left", va="bottom", fontsize=10
            )

            # Centerline label
            ax.text(
                x_span / 2,
                0.28,
                "Shaft Centerline",
                ha="center", va="bottom",
                fontsize=10
            )

            # Factor note
            ax.text(
                x_span / 2, -2.42,
                rf"$K_b = {belt_tension_factor:.2f}$  |  "
                r"$F_{\mathrm{hub,act}} = K_b F_{\mathrm{hub}}$",
                ha="center", va="top",
                fontsize=11
            )

            # Plot limits / styling
            ax.set_xlim(-0.08 * x_span, 1.08 * x_span)
            ax.set_ylim(-2.85, 2.20)
            ax.axis("off")

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            st.markdown("### 🔎 FBD Load Summary")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("V-Belt Factor K_b", f"{belt_tension_factor:.2f}")
            with c2:
                st.metric("Drive / Hub Load", f"{f_hub_act:.2f} N")
            with c3:
                st.metric("Bearing A Reaction", f"{r_a:.2f} N")
            with c4:
                st.metric("Bearing B Reaction", f"{r_b:.2f} N")

            st.info(
                "The V-belt tension factor is entered by the user and is applied "
                "to the hub load because the hub is subjected to the V-belt loading."
            )

        with tab4:
            st.subheader("📝 Reference System Equations")
            st.markdown(
                "Your calculator utilizes the following fundamental physics implementations:")
            st.latex(r"T = \frac{P \times 60 \times 1000}{2 \pi n}")
            st.latex(r"F = \frac{2 \times T \times 1000}{d}")
            st.latex(r"F_{hub,act} = K_b F_{hub}")
            st.latex(
                r"R_A = \frac{F_{hub,act}(L_1 + L_2) - F_{impeller}(L_3)}{L_2}")
            st.latex(r"R_B = F_{hub,act} + F_{impeller} - R_A")

else:
    # Welcoming placeholder state before execution
    st.info("👈 Configure your operating parameters in the sidebar panel and click **Run Engineering Calculations**.")
