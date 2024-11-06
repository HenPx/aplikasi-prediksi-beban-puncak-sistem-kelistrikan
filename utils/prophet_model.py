from prophet import Prophet
import pandas as pd

def prepare_prophet_data(data):
    df_prophet = data.reset_index().rename(columns={'Date': 'ds', 'BP': 'y'})
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'], dayfirst=True)

    return df_prophet

def initialize_model():
    model = Prophet(
        changepoint_prior_scale=0.1,
        daily_seasonality=False,
        interval_width=0.8,
        seasonality_mode='multiplicative',
        seasonality_prior_scale=10.0,
        weekly_seasonality=False,
        yearly_seasonality=True
    )
    return model

def predict_future(df_prophet, periods):
    model = initialize_model()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return model, forecast
