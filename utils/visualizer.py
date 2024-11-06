import plotly.graph_objs as go
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt


def visualize_data(data):
    st.subheader('Dataset')
    st.write(data.head())

    st.subheader('Grafik Dataset')
    fig = px.line(data, x=data.index, y='BP', title='Grafik BP dari Dataset')
    st.plotly_chart(fig)


# Visualize forecast using Plotly
def visualize_forecast(model, forecast, df_prophet, periods):
    st.subheader('Hasil Prediksi')

    # Determine the cutoff date for actual vs. future predictions
    cutoff_date = df_prophet['ds'].max()

    # Plot the forecast
    fig = go.Figure()

    # Add actual data (Bintik Hitam)
    fig.add_trace(go.Scatter(
        x=df_prophet['ds'], 
        y=df_prophet['y'], 
        mode='markers', 
        name='Actual Data (Bintik Hitam)',
        marker=dict(color='grey', size=3)
    ))

    # Add forecast data up to the cutoff date (in blue)
    fig.add_trace(go.Scatter(
        x=forecast[forecast['ds'] <= cutoff_date]['ds'], 
        y=forecast[forecast['ds'] <= cutoff_date]['yhat'], 
        mode='lines', 
        name='Historical Forecast',
        line=dict(color='blue'),
        legendgroup='group1'
    ))

    # Add upper bound and lower bound for historical data (in blue)
    fig.add_trace(go.Scatter(
        x=forecast[forecast['ds'] <= cutoff_date]['ds'], 
        y=forecast[forecast['ds'] <= cutoff_date]['yhat_upper'], 
        mode='lines', 
        line=dict(color='lightblue'),
        showlegend=False,
        legendgroup='group1'
    ))

    fig.add_trace(go.Scatter(
        x=forecast[forecast['ds'] <= cutoff_date]['ds'], 
        y=forecast[forecast['ds'] <= cutoff_date]['yhat_lower'], 
        mode='lines', 
        line=dict(color='lightblue'),
        fill='tonexty',
        showlegend=False,
        legendgroup='group1'
    ))

    # Future Forecast: Different colors based on yhat value
    future_forecast = forecast[forecast['ds'] > cutoff_date]
    
    # Green lines
    fig.add_trace(go.Scatter(
        x=future_forecast[future_forecast['yhat'] < 10000]['ds'], 
        y=future_forecast[future_forecast['yhat'] < 10000]['yhat'], 
        mode='lines', 
        name='Future Forecast < 10,000',
        line=dict(color='green'),
        legendgroup='group2'
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast[future_forecast['yhat'] < 10000]['ds'], 
        y=future_forecast[future_forecast['yhat'] < 10000]['yhat_upper'], 
        mode='lines', 
        line=dict(color='lightgreen'),
        showlegend=False,
        legendgroup='group2'
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast[future_forecast['yhat'] < 10000]['ds'], 
        y=future_forecast[future_forecast['yhat'] < 10000]['yhat_lower'], 
        mode='lines', 
        line=dict(color='lightgreen'),
        fill='tonexty',
        showlegend=False,
        legendgroup='group2'
    ))

    # Yellow lines
    fig.add_trace(go.Scatter(
        x=future_forecast[(future_forecast['yhat'] >= 10000) & (future_forecast['yhat'] <= 14000)]['ds'], 
        y=future_forecast[(future_forecast['yhat'] >= 10000) & (future_forecast['yhat'] <= 14000)]['yhat'], 
        mode='lines', 
        name='Future Forecast 10,000 - 14,000',
        line=dict(color='#FFB82B'),
        legendgroup='group3'
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast[(future_forecast['yhat'] >= 10000) & (future_forecast['yhat'] <= 14000)]['ds'], 
        y=future_forecast[(future_forecast['yhat'] >= 10000) & (future_forecast['yhat'] <= 14000)]['yhat_upper'], 
        mode='lines', 
        line=dict(color='#FFCF60'),
        showlegend=False,
        legendgroup='group3'
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast[(future_forecast['yhat'] >= 10000) & (future_forecast['yhat'] <= 14000)]['ds'], 
        y=future_forecast[(future_forecast['yhat'] >= 10000) & (future_forecast['yhat'] <= 14000)]['yhat_lower'], 
        mode='lines', 
        line=dict(color='#FFCF60'),
        fill='tonexty',
        showlegend=False,
        legendgroup='group3'
    ))

    # Red lines
    fig.add_trace(go.Scatter(
        x=future_forecast[future_forecast['yhat'] > 14000]['ds'], 
        y=future_forecast[future_forecast['yhat'] > 14000]['yhat'], 
        mode='lines', 
        name='Future Forecast > 14,000',
        line=dict(color='red'),
        legendgroup='group4'
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast[future_forecast['yhat'] > 14000]['ds'], 
        y=future_forecast[future_forecast['yhat'] > 14000]['yhat_upper'], 
        mode='lines', 
        line=dict(color='lightcoral'),
        showlegend=False,
        legendgroup='group4'
    ))
    fig.add_trace(go.Scatter(
        x=future_forecast[future_forecast['yhat'] > 14000]['ds'], 
        y=future_forecast[future_forecast['yhat'] > 14000]['yhat_lower'], 
        mode='lines', 
        line=dict(color='lightcoral'),
        fill='tonexty',
        showlegend=False,
        legendgroup='group4'
    ))

    # Update layout
    fig.update_layout(
        title='BP Forecasting using Prophet',
        xaxis_title='Date',
        yaxis_title='BP',
        legend_title='Legend',
        hovermode='x'
    )

    # Show the plot
    st.plotly_chart(fig)

    
    st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods))
    
    # Komponen Prediksi dengan Plotly
    st.subheader('Komponen Prediksi dengan Plotly')

    # Plot komponen tren dengan upper dan lower bound
    fig_trend = go.Figure()

    # Garis utama untuk trend
    fig_trend.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['trend'],
        mode='lines', name='Trend', line=dict(color='blue')
    ))

    # Garis untuk upper bound
    fig_trend.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['trend_upper'],
        mode='lines', name='Upper Bound', line=dict(color='lightblue'),
        fill=None
    ))

    # Garis untuk lower bound
    fig_trend.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['trend_lower'],
        mode='lines', name='Lower Bound', line=dict(color='lightblue'),
        fill='tonexty', fillcolor='rgba(173, 216, 230, 0.3)'  # Mengisi area antara upper dan lower bound
    ))

    fig_trend.update_layout(title='Komponen Tren dengan Upper & Lower Bound', 
                            xaxis_title='Tanggal', 
                            yaxis_title='Nilai Tren',
                            xaxis=dict(showgrid=True, gridcolor='LightGray', gridwidth=0.5),  # Menambahkan grid di sumbu X
                            yaxis=dict(showgrid=True, gridcolor='LightGray', gridwidth=0.5) )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Plot komponen musiman mingguan (jika ada)
    if 'weekly' in forecast.columns:
        fig_weekly = go.Figure()
        fig_weekly.add_trace(go.Scatter(
            x=forecast['ds'], y=forecast['weekly'],
            mode='lines', name='Musiman Mingguan', line=dict(color='orange')
        ))

        # Upper bound musiman mingguan
        if 'weekly_upper' in forecast.columns and 'weekly_lower' in forecast.columns:
            fig_weekly.add_trace(go.Scatter(
                x=forecast['ds'], y=forecast['weekly_upper'],
                mode='lines', name='Upper Bound', line=dict(color='lightorange'),
                fill=None
            ))

            fig_weekly.add_trace(go.Scatter(
                x=forecast['ds'], y=forecast['weekly_lower'],
                mode='lines', name='Lower Bound', line=dict(color='lightorange'),
                fill='tonexty', fillcolor='rgba(255, 165, 0, 0.3)'  # Mengisi area antara upper dan lower bound
            ))

        fig_weekly.update_layout(title='Komponen Musiman Mingguan dengan Upper & Lower Bound', 
                                xaxis_title='Tanggal', 
                                yaxis_title='Nilai Musiman Mingguan')
        st.plotly_chart(fig_weekly, use_container_width=True)

    # Plot komponen musiman tahunan (jika ada)
    if 'yearly' in forecast.columns:
        fig_yearly = go.Figure()
        fig_yearly.add_trace(go.Scatter(
            x=forecast['ds'], y=forecast['yearly'],
            mode='lines', name='Musiman Tahunan', line=dict(color='green')
        ))


        fig_yearly.update_layout(title='Komponen Musiman Tahunan dengan Upper & Lower Bound', 
                                xaxis_title='Tanggal', 
                                yaxis_title='Nilai Musiman Tahunan')
        st.plotly_chart(fig_yearly, use_container_width=True)

