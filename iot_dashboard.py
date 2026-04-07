"""
IoT Simulyasiya Dashboard — Streamlit
DHT22 Temperatur & Rütubət Monitorinq Sistemi
Əşyaların İnterneti Laboratoriya İşi

İstifadə: streamlit run iot_dashboard.py
"""

import streamlit as st
import random
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ── Konfiqurasiya ──────────────────────────────────────────────
TEMP_THRESHOLD = 35.0
HUMIDITY_THRESHOLD = 80.0

st.set_page_config(
    page_title="IoT Simulyasiya Dashboard",
    page_icon="🌡️",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
    .stApp { background-color: #0B0E14; }
    .main-title { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; color: #E8ECF1; }
    .main-title span { color: #2E86C1; }
    .subtitle { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #5A6577; }
    .metric-card {
        background: #111620; border: 1px solid #1E2530; border-radius: 10px;
        padding: 16px; text-align: center;
    }
    .metric-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #5A6577; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; }
    .led-on {
        width: 80px; height: 80px; border-radius: 50%; margin: 10px auto;
        background: #ff4444; box-shadow: 0 0 25px #ff4444, 0 0 50px #ff444466;
        display: flex; align-items: center; justify-content: center;
        font-family: 'JetBrains Mono', monospace; font-weight: 700; color: white; font-size: 16px;
    }
    .led-off {
        width: 80px; height: 80px; border-radius: 50%; margin: 10px auto;
        background: #2A3040; display: flex; align-items: center; justify-content: center;
        font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #5A6577; font-size: 16px;
    }
    .step-box {
        background: #111620; border: 1px solid #1E2530; border-radius: 8px;
        padding: 10px 14px; text-align: center;
    }
    .step-active { border-color: #2E86C1; background: #2E86C122; }
    .step-label { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .step-desc { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #5A6577; margin-top: 4px; }
    .log-box {
        background: #0B0E14; border: 1px solid #1E2530; border-radius: 6px;
        padding: 10px; font-family: 'JetBrains Mono', monospace; font-size: 11px;
        color: #5A6577; max-height: 200px; overflow-y: auto;
    }
    .log-alert { color: #E67E22; }
    div[data-testid="stMetric"] { background: #111620; border: 1px solid #1E2530; border-radius: 10px; padding: 12px; }
    div[data-testid="stMetric"] label { color: #5A6577 !important; font-family: 'JetBrains Mono', monospace !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #E8ECF1 !important; font-family: 'JetBrains Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "running" not in st.session_state:
    st.session_state.running = False
if "step_index" not in st.session_state:
    st.session_state.step_index = -1

# ── Sensor funksiyaları ────────────────────────────────────────
def read_sensor():
    return {
        "temperature": round(random.uniform(20.0, 45.0), 2),
        "humidity": round(random.uniform(30.0, 95.0), 2),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }

def apply_filter(reading, history):
    window = history[-5:]
    avg_temp = round(sum(r["temperature"] for r in window) / len(window), 2) if window else reading["temperature"]
    avg_hum = round(sum(r["humidity"] for r in window) / len(window), 2) if window else reading["humidity"]
    alerts = []
    if reading["temperature"] > TEMP_THRESHOLD:
        alerts.append(f"Temp {reading['temperature']}°C > {TEMP_THRESHOLD}°C")
    if reading["humidity"] > HUMIDITY_THRESHOLD:
        alerts.append(f"Rütubət {reading['humidity']}% > {HUMIDITY_THRESHOLD}%")
    return {
        **reading,
        "avg_temp": avg_temp,
        "avg_hum": avg_hum,
        "alerts": alerts,
        "led_on": len(alerts) > 0,
    }

def run_one_cycle():
    """Pipeline-ın bir tam dövranı."""
    reading = read_sensor()
    st.session_state.history.append(reading)
    processed = apply_filter(reading, st.session_state.history)
    log = f"[{processed['timestamp']}] T:{processed['temperature']}°C H:{processed['humidity']}% LED:{'ON' if processed['led_on'] else 'OFF'}"
    if processed["alerts"]:
        log += " ⚠ " + ", ".join(processed["alerts"])
    st.session_state.logs.append(log)
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]
    return processed

# ── Header ─────────────────────────────────────────────────────
st.markdown('<div class="main-title"><span>IoT</span> Simulyasiya Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">DHT22 Temperatur & Rütubət Monitorinq Sistemi — Əşyaların İnterneti Laboratoriya İşi</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Pipeline Addımları ─────────────────────────────────────────
STEPS = [
    ("Read", "Sensor məlumatını oxu", "#C0392B"),
    ("Apply", "Filtrasiya və hədd məntiqi", "#27AE60"),
    ("Send", "Dashboard-a göndər", "#2E86C1"),
    ("Trigger", "Aktuator (LED) idarəsi", "#E67E22"),
    ("Document", "Nəticəni sənədləşdir", "#8E44AD"),
]

step_cols = st.columns(5)
for i, (label, desc, color) in enumerate(STEPS):
    with step_cols[i]:
        is_active = st.session_state.step_index == i
        cls = "step-box step-active" if is_active else "step-box"
        st.markdown(f"""
        <div class="{cls}">
            <div class="step-label" style="color:{color};">{label}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── İdarə Paneli ──────────────────────────────────────────────
ctrl_cols = st.columns([1, 1, 1, 3])

with ctrl_cols[0]:
    num_readings = st.selectbox("Oxunuş sayı", [10, 20, 30, 50], index=1)

with ctrl_cols[1]:
    delay = st.selectbox("Sürət (san)", [0.3, 0.5, 1.0, 2.0], index=1)

with ctrl_cols[2]:
    st.markdown("<br>", unsafe_allow_html=True)
    reset = st.button("🔄 Sıfırla", use_container_width=True)
    if reset:
        st.session_state.history = []
        st.session_state.logs = []
        st.session_state.running = False
        st.session_state.step_index = -1
        st.rerun()

with ctrl_cols[3]:
    st.markdown("<br>", unsafe_allow_html=True)
    start = st.button("▶  Simulyasiyanı Başlat", type="primary", use_container_width=True)

# ── Simulyasiya İcrası ─────────────────────────────────────────
results = []
chart_placeholder = st.empty()
metrics_placeholder = st.empty()
log_placeholder = st.empty()

if start:
    st.session_state.history = []
    st.session_state.logs = []

    for cycle in range(num_readings):
        # Animate pipeline steps
        for si in range(5):
            st.session_state.step_index = si
            time.sleep(delay / 6)

        processed = run_one_cycle()
        results.append(processed)
        st.session_state.step_index = -1

        # Build dataframe
        df = pd.DataFrame([{
            "Oxunuş": idx + 1,
            "Temp (°C)": r["temperature"],
            "Filtr Temp (°C)": r["avg_temp"],
            "Rütubət (%)": r["humidity"],
            "Filtr Rütubət (%)": r["avg_hum"],
            "LED": "ON" if r["led_on"] else "OFF",
        } for idx, r in enumerate(results)])

        # ── Charts ──
        with chart_placeholder.container():
            ch1, ch2 = st.columns(2)
            with ch1:
                fig_temp = go.Figure()
                fig_temp.add_trace(go.Scatter(
                    x=df["Oxunuş"], y=df["Temp (°C)"],
                    mode="lines", name="Xam Temp",
                    line=dict(color="#E67E22", width=2),
                ))
                fig_temp.add_trace(go.Scatter(
                    x=df["Oxunuş"], y=df["Filtr Temp (°C)"],
                    mode="lines", name="Filtr Temp",
                    line=dict(color="#2E86C1", width=2),
                ))
                fig_temp.add_hline(y=TEMP_THRESHOLD, line_dash="dash", line_color="#C0392B",
                                   annotation_text="Hədd", annotation_font_color="#C0392B")
                fig_temp.update_layout(
                    title="Temperatur (°C)", title_font=dict(size=14, color="#5A6577"),
                    plot_bgcolor="#111620", paper_bgcolor="#0B0E14",
                    font=dict(family="JetBrains Mono", color="#5A6577", size=11),
                    xaxis=dict(gridcolor="#1E2530"), yaxis=dict(gridcolor="#1E2530", range=[15, 50]),
                    height=300, margin=dict(l=40, r=20, t=40, b=30),
                    legend=dict(orientation="h", y=-0.15),
                )
                st.plotly_chart(fig_temp, use_container_width=True)

            with ch2:
                fig_hum = go.Figure()
                fig_hum.add_trace(go.Scatter(
                    x=df["Oxunuş"], y=df["Rütubət (%)"],
                    mode="lines", name="Xam Rütubət",
                    line=dict(color="#27AE60", width=2),
                ))
                fig_hum.add_trace(go.Scatter(
                    x=df["Oxunuş"], y=df["Filtr Rütubət (%)"],
                    mode="lines", name="Filtr Rütubət",
                    line=dict(color="#8E44AD", width=2),
                ))
                fig_hum.add_hline(y=HUMIDITY_THRESHOLD, line_dash="dash", line_color="#C0392B",
                                   annotation_text="Hədd", annotation_font_color="#C0392B")
                fig_hum.update_layout(
                    title="Rütubət (%)", title_font=dict(size=14, color="#5A6577"),
                    plot_bgcolor="#111620", paper_bgcolor="#0B0E14",
                    font=dict(family="JetBrains Mono", color="#5A6577", size=11),
                    xaxis=dict(gridcolor="#1E2530"), yaxis=dict(gridcolor="#1E2530", range=[20, 100]),
                    height=300, margin=dict(l=40, r=20, t=40, b=30),
                    legend=dict(orientation="h", y=-0.15),
                )
                st.plotly_chart(fig_hum, use_container_width=True)

        # ── Metrics ──
        with metrics_placeholder.container():
            alert_count = sum(1 for r in results if r["led_on"])
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Oxunuş", f"{len(results)}")
            m2.metric("Xəbərdarlıq", f"{alert_count}")
            m3.metric("Cari Temp", f"{processed['temperature']}°C")
            m4.metric("Cari Rütubət", f"{processed['humidity']}%")
            with m5:
                led_cls = "led-on" if processed["led_on"] else "led-off"
                led_txt = "ON" if processed["led_on"] else "OFF"
                st.markdown(f'<div class="{led_cls}">{led_txt}</div>', unsafe_allow_html=True)

        # ── Log ──
        with log_placeholder.container():
            st.markdown("**Sistem Loqu**")
            log_html = "<div class='log-box'>"
            for log_line in st.session_state.logs:
                cls = "log-alert" if "⚠" in log_line else ""
                log_html += f"<div class='{cls}'>{log_line}</div>"
            log_html += "</div>"
            st.markdown(log_html, unsafe_allow_html=True)

        time.sleep(delay)

    # ── Final Summary ──
    st.markdown("---")
    st.markdown("### 📊 Simulyasiya Nəticəsi")

    final_df = pd.DataFrame([{
        "Oxunuş": idx + 1,
        "Vaxt": r["timestamp"],
        "Temp (°C)": r["temperature"],
        "Filtr Temp (°C)": r["avg_temp"],
        "Rütubət (%)": r["humidity"],
        "Filtr Rütubət (%)": r["avg_hum"],
        "LED": "ON" if r["led_on"] else "OFF",
        "Xəbərdarlıq": ", ".join(r["alerts"]) if r["alerts"] else "-",
    } for idx, r in enumerate(results)])

    st.dataframe(final_df, use_container_width=True, hide_index=True)

    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV olaraq yüklə", csv, "iot_simulation_results.csv", "text/csv")

# ── Boş vəziyyət ──────────────────────────────────────────────
elif not st.session_state.logs:
    st.markdown("""
    <div style="text-align:center; padding:60px; color:#2A3040; font-family:'JetBrains Mono',monospace;">
        <div style="font-size:48px; margin-bottom:16px;">🌡️</div>
        <div style="font-size:16px;">Simulyasiyanı başlatmaq üçün yuxarıdakı düyməyə basın</div>
    </div>
    """, unsafe_allow_html=True)
