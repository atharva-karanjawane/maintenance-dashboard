import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

# Load data into a pandas DataFrame
data = pd.read_csv('fan_data.csv', parse_dates=['date'])

# Streamlit application setup
st.set_page_config(page_title="Fan Performance Dashboard", layout="wide")

# Custom sidebar for user inputs
st.sidebar.title("Fan Performance Dashboard")
selected_fan = st.sidebar.selectbox("Select Fan ID", data['Fan ID'].unique())

# Filter data based on selected fan
filtered_data = data[data['Fan ID'] == selected_fan]

# Date Range Filter
st.sidebar.subheader("Date Range")
start_date, end_date = st.sidebar.date_input(
    "Select Date Range:",
    [filtered_data['date'].min(), filtered_data['date'].max()]
)
filtered_data = filtered_data[(filtered_data['date'] >= pd.Timestamp(start_date)) & (filtered_data['date'] <= pd.Timestamp(end_date))]

# Main Title
st.markdown(f"<h1 style='text-align: center; color: #4A90E2;'>Fan Performance Overview for {selected_fan}</h1>", unsafe_allow_html=True)
st.markdown("---")

# Top section with KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# Latest data for the selected fan
latest_data = filtered_data.iloc[-1]

# KPI 1: Power Consumption
kpi1.metric(label="Power Consumption (kW)", value=f"{latest_data['Power Consumption (kW)']:.2f} kW")

# KPI 2: Motor Temperature
kpi2.metric(label="Motor Temperature (°C)", value=f"{latest_data['Motor Temp (°C)']:.2f} °C")

# KPI 3: Operational Status
kpi3.metric(label="Operational Status", value=latest_data['Operational Status'])

# KPI 4: Airflow
kpi4.metric(label="Airflow (m³/s)", value=f"{latest_data['Airflow (m³/s)']:.2f} m³/s")

st.markdown("---")

# Main plots
st.subheader('Performance Trends')
trend1, trend2 = st.columns(2)

# Airflow Trend Over Time
with trend1:
    airflow_fig = px.line(filtered_data, x='date', y='Airflow (m³/s)',
                          title='Airflow Over Time',
                          template='plotly_dark',
                          markers=True)
    airflow_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Airflow (m³/s)",
        title_font=dict(size=18, family='Arial', color='#1f77b4'),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, zeroline=False)
    )
    st.plotly_chart(airflow_fig, use_container_width=True)

# Power Consumption Trend Over Time
with trend2:
    power_fig = px.line(filtered_data, x='date', y='Power Consumption (kW)',
                        title='Power Consumption Over Time',
                        template='plotly_dark',
                        markers=True)
    power_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Power Consumption (kW)",
        title_font=dict(size=18, family='Arial', color='#ff7f0e'),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, zeroline=False)
    )
    st.plotly_chart(power_fig, use_container_width=True)

st.markdown("---")

# Motor Temperature vs. Vibration Scatter Plot
st.subheader('Motor Temperature vs. Vibration')
temp_vs_vibration_fig = px.scatter(
    filtered_data,
    x='Motor Temp (°C)',
    y='Vibration (mm/s)',
    size='Power Consumption (kW)',
    color='Operational Status',
    hover_name='Notes',
    title='Motor Temperature vs. Vibration',
    template='plotly_dark'
)
temp_vs_vibration_fig.update_layout(
    xaxis_title="Motor Temperature (°C)",
    yaxis_title="Vibration (mm/s)",
    title_font=dict(size=18, family='Arial', color='#17becf'),
    xaxis=dict(showgrid=True, zeroline=False),
    yaxis=dict(showgrid=True, zeroline=False),
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(temp_vs_vibration_fig, use_container_width=True)

st.markdown("---")

# Fan Health Status Gauges
st.subheader('Fan Health Status Indicators')
fan_health_fig = go.Figure()

# Power Consumption Gauge
fan_health_fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=latest_data['Power Consumption (kW)'],
    domain={'x': [0, 0.5], 'y': [0, 1]},
    title={'text': "Power Consumption (kW)"},
    gauge={'axis': {'range': [0, latest_data['Power Rating (kW)']]},
           'bar': {'color': "blue"},
           'steps': [{'range': [0, latest_data['Power Rating (kW)']/2], 'color': 'lightblue'},
                     {'range': [latest_data['Power Rating (kW)']/2, latest_data['Power Rating (kW)']], 'color': 'blue'}]}))

# Motor Temperature Gauge
fan_health_fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=latest_data['Motor Temp (°C)'],
    domain={'x': [0.5, 1], 'y': [0, 1]},
    title={'text': "Motor Temp (°C)"},
    gauge={'axis': {'range': [0, 100]},
           'bar': {'color': "red"},
           'steps': [{'range': [0, 50], 'color': 'lightcoral'},
                     {'range': [50, 100], 'color': 'red'}]}))

fan_health_fig.update_layout(
    grid={'rows': 1, 'columns': 2, 'pattern': "independent"},
    title={'text': "Fan Health Status Indicators", 'font': {'size': 20, 'color': '#1f77b4'}},
    template='plotly_dark'
)

st.plotly_chart(fan_health_fig, use_container_width=True)

st.markdown("---")

# Compute Fan Condition Score
st.subheader('Fan Condition Score')

# Define weights for each metric
weights = {
    'Power Consumption (kW)': 0.3,
    'Motor Temp (°C)': 0.3,
    'Airflow (m³/s)': 0.2,
    'Vibration (mm/s)': 0.2
}

# Normalize each metric
scaler = MinMaxScaler()

metrics = {
    'Power Consumption (kW)': filtered_data['Power Consumption (kW)'].values,
    'Motor Temp (°C)': filtered_data['Motor Temp (°C)'].values,
    'Airflow (m³/s)': filtered_data['Airflow (m³/s)'].values,
    'Vibration (mm/s)': filtered_data['Vibration (mm/s)'].values
}

normalized_metrics = pd.DataFrame(scaler.fit_transform(pd.DataFrame(metrics)), columns=metrics.keys())

# Calculate condition score
condition_score = (
    weights['Power Consumption (kW)'] * normalized_metrics['Power Consumption (kW)'].iloc[-1] +
    weights['Motor Temp (°C)'] * (1 - normalized_metrics['Motor Temp (°C)'].iloc[-1]) +  # Lower temp is better
    weights['Airflow (m³/s)'] * normalized_metrics['Airflow (m³/s)'].iloc[-1] +
    weights['Vibration (mm/s)'] * (1 - normalized_metrics['Vibration (mm/s)'].iloc[-1])  # Lower vibration is better
) * 100

st.metric(label="Overall Fan Condition Score", value=f"{condition_score:.2f}")

st.markdown("---")

# Display Fan Condition Score as a Gauge
st.subheader('Overall Fan Condition Score')
condition_score_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=condition_score,
    title={'text': "Fan Condition Score"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "green"},
        'steps': [
            {'range': [0, 50], 'color': 'lightcoral'},
            {'range': [50, 75], 'color': 'lightyellow'},
            {'range': [75, 100], 'color': 'lightgreen'}
        ]
    }
))

condition_score_fig.update_layout(
    title={'text': "Fan Condition Score", 'font': {'size': 20, 'color': '#1f77b4'}},
    template='plotly_dark'
)

st.plotly_chart(condition_score_fig, use_container_width=True)