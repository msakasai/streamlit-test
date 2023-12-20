import streamlit as st
import pandas as pd
import japanize_matplotlib
import seaborn as sns
import datetime
from const import tokyo_weather_json, icon_image_path, weather_icons

## seabornのスタイル設定 ###
sns.set_style(style="darkgrid")
sns.set_context("paper")
sns.set_color_codes("pastel")
sns.set(font='IPAexGothic')

### Functions ###
def weather_icon_image(icon_image: str) -> str:
    """画像URL取得"""
    return f'{icon_image_path}{icon_image}'

def weather_icon(weathers: list[str]) -> list[str]:
    """画像URLのリスト取得"""
    nowtime: int = int(datetime.datetime.now().strftime("%H")) + 9
    ret: str = []
    for weather in weathers:
        for icon in weather_icons:
            for k,v in icon.items():
                if k == weather:
                    ret.append(weather_icon_image(v[0] if 3 < nowtime < 15 else v[1]))
                    break
    return ret

def df_weather():
    """天気予報を取得し、データフレームにセットして返却"""
    df = pd.read_json(tokyo_weather_json)
    time_defines = df.iloc[0]["timeSeries"][0]["timeDefines"]
    tokyo = df.iloc[0]["timeSeries"][0]["areas"][0]
    ret = pd.DataFrame({
        "天気予報コード": tokyo["weatherCodes"],
        "天気予報icon": weather_icon(tokyo["weatherCodes"]),
        "天気予報": tokyo["weathers"],
        "風速": tokyo["winds"],
        "波高": tokyo["waves"],
    }, index=time_defines)
    ret.index = pd.to_datetime(ret.index)
    ret.index = ret.index.strftime("%Y-%m-%d")
    return ret

def lineplot(_st, _df, _title: str, xlabel: str, ylabel: str, ylim: int = None):
    """線グラフを描画"""
    _st.markdown(f"### {_title}")
    plot = sns.lineplot(_df, x=xlabel, y=ylabel, markers=True)
    plot.set_xticks([x for x in _df.index[::3]])
    plot.set_xticklabels([x for x in _df.index[::3]], rotation=90)
    plot.set_ylim(-0.01, ylim)
    _st.pyplot(plot.figure, clear_figure=True)

### Page Configuration ###
title = "気象データダッシュボード"
st.set_page_config(
    page_title=title,
    page_icon="🌈",
    layout="wide",
)
st.title(title)

### Page Content ###
## sidebar
st.sidebar.markdown('''
# MENU
- [weather](#weather)
- [csv upload](#csv-upload)
- [graph](#graph)
- [data sheet](#data-sheet)
''', unsafe_allow_html=True)

## main
st.header("weather news")
with st.container(border=True):
    st.dataframe(df_weather(), use_container_width=True, column_config={
        "天気予報icon": st.column_config.ImageColumn()
    })

st.markdown("---")
st.header("csv upload")
with st.container(border=True):
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

st.markdown("---")
st.header("graph")

if uploaded_file is not None:
    # CSVファイルの読み込み
    df = pd.read_csv(uploaded_file, index_col="年月日時", parse_dates=True)
    df.index = df.index.strftime("%H:%M")

    with st.container(border=True):
        # 2カラムを用意
        l_col, r_col = st.columns(2)

        # 気温(℃)（左カラム）
        df_temp = df.copy().iloc[:, :1]
        lineplot(l_col, df_temp, "気温(℃)", "年月日時", "気温(℃)")

        # 相対湿度(％)（右カラム）
        df_hum = df.copy().iloc[:, 1:2]
        lineplot(r_col, df_hum, "相対湿度(％)", "年月日時", "相対湿度(％)", 100)

    with st.container(border=True):
        # 2カラムを用意
        l_col, r_col = st.columns(2)

        # 降水量(mm)（左カラム）
        df_preci = df.copy().iloc[:, 2:3]
        lineplot(l_col, df_preci, "降水量(mm)", "年月日時", "降水量(mm)")

        # 日射量(MJ/㎡)（右カラム）
        df_sol = df.copy().iloc[:, 3:4]
        lineplot(r_col, df_sol, "日射量(MJ/㎡)", "年月日時", "日射量(MJ/㎡)")

st.markdown("---")
st.header("data sheet")

if uploaded_file is not None:
    with st.container(border=True):
        st.write(df)

