import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_fetcher import load_csv
from src.indicators import sma, rsi, macd

st.set_page_config(page_title='تحلیل‌گر سهام ایران (MVP)', layout='wide')

st.title('تحلیل‌گر سهام ایران — MVP')
st.write('یک نمونهٔ اولیه برای بارگذاری دادهٔ تاریخی سهام و محاسبهٔ اندیکاتورهای پایه')

with st.sidebar:
    st.header('ورودی دیتا')
    uploaded_file = st.file_uploader('بارگذاری فایل CSV (ستون Date و Close حداقل)', type=['csv'])
    ticker = st.text_input('تیکر (اختیاری) — برای آینده: دریافت خودکار از TSETMC', value='')

    st.header('اندیکاتورها')
    show_sma = st.checkbox('نمایش SMA', value=True)
    sma_window = st.number_input('دوره SMA', min_value=2, max_value=200, value=20)

    show_rsi = st.checkbox('نمایش RSI', value=True)
    rsi_window = st.number_input('دوره RSI', min_value=2, max_value=100, value=14)

    show_macd = st.checkbox('نمایش MACD', value=True)
    macd_fast = st.number_input('MACD fast', min_value=2, max_value=50, value=12)
    macd_slow = st.number_input('MACD slow', min_value=2, max_value=100, value=26)
    macd_signal = st.number_input('MACD signal', min_value=1, max_value=50, value=9)

    st.markdown('---')
    st.markdown('راهنما: برای MVP فعلی، لطفاً فایل CSV با حداقل ستون‌های `Date` و `Close` بارگذاری کنید. فرمت تاریخ yyyy-mm-dd توصیه می‌شود.')


if uploaded_file is None:
    st.info('یک فایل CSV بارگذاری کنید تا تحلیل انجام شود.')
else:
    df = load_csv(uploaded_file)
    if 'Close' not in df.columns:
        st.error('ستون Close در CSV پیدا نشد. نام ستون‌ها: {}'.format(df.columns.tolist()))
    else:
        price = df['Close'].astype(float)
        title = st.text_input('عنوان نمودار', value='قیمت Close')

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=price.index, y=price.values, name='Close', line=dict(color='black')))

        if show_sma:
            s = sma(price, int(sma_window))
            fig.add_trace(go.Scatter(x=s.index, y=s.values, name=f'SMA({sma_window})'))

        fig.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(1)
        with cols[0]:
            if show_rsi:
                r = rsi(price, int(rsi_window))
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=r.index, y=r.values, name=f'RSI({rsi_window})'))
                fig2.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(range=[0,100]))
                st.plotly_chart(fig2, use_container_width=True)

            if show_macd:
                m = macd(price, int(macd_fast), int(macd_slow), int(macd_signal))
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=m.index, y=m['macd'], name='MACD'))
                fig3.add_trace(go.Scatter(x=m.index, y=m['signal'], name='Signal'))
                fig3.add_trace(go.Bar(x=m.index, y=m['histogram'], name='Histogram'))
                fig3.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig3, use_container_width=True)

        # Data & download
        if st.button('دانلود داده با اندیکاتورها (CSV)'):
            out = df.copy()
            if show_sma:
                out[f'SMA_{sma_window}'] = sma(price, int(sma_window))
            if show_rsi:
                out[f'RSI_{rsi_window}'] = rsi(price, int(rsi_window))
            if show_macd:
                out_macd = macd(price, int(macd_fast), int(macd_slow), int(macd_signal))
                out = out.join(out_macd)

            csv = out.to_csv(index=True)
            st.download_button('دانلود CSV', data=csv, file_name='with_indicators.csv', mime='text/csv')
