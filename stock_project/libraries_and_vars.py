# finance api
# import yahoofinancials
import yahooquery as yq
import yfinance as yf
import nasdaqdatalink as ndl

# data
import numpy as np
import pandas as pd
import pandas_ta as ta
import datetime as dt
from dateutil.relativedelta import relativedelta

# visualization
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from plotly.subplots import make_subplots
from annotated_text import annotated_text

# web scrapping
import requests
import json
import time
import re
import lxml
from bs4 import BeautifulSoup

NASDAQ_DATA_LINK_API_KEY = "xy8jtvPFDhiwnFktEugz"  # ndl.ApiConfig.api_key
ALPHA_VANTAGE_API_KEY = "F32LXOAF8HHN5Q4N" # https://www.alphavantage.co/documentation/#

pd.set_option("display.max_columns", None)

pio.templates.default = "plotly_dark"

# Defining variables
STOCK = "MSFT"

STOCKS_LIST = ["AAPL", "BRK-B", "COST", "MSFT"]

CRYPTO_LIST = ["BTC-USD", "ETH-USD"]

ETF_LIST = ["SCHD", "SPHD", "VOO", "QQQ", "VGT", "ARKK"]

stock_list_new = [x.lower() if x != "BRK-B" else "brk.b" for x in STOCKS_LIST]
freq2 = 'Q'

# https://www.simplysafedividends.com/world-of-dividends/posts/41-2022-dividend-kings-list-all-47-our-top-5-picks
# https://www.simplysafedividends.com/world-of-dividends/posts/6-2023-dividend-aristocrats-list-all-65-our-top-5-picks
PATH_ARICTOCRAT = "Dividend Aristocrats - 2023-02-14-22-43-13.csv"
PATH_KING = "Dividend Kings - 2023-02-14-22-43-26.csv"


tickers_macrotrends_dict = {}
macrotrends_list = requests.get(
    "https://www.macrotrends.net/assets/php/ticker_search_list.php?_=1673472383864"
).json()


ticker_names = []
for e in macrotrends_list:
    url_link = list(e.values())[1]
    ticker = list(e.values())[0].split(" - ")[0]
    ticker_names.append(list(e.values())[0])
    tickers_macrotrends_dict[ticker] = url_link

class Toc:
    """https://discuss.streamlit.io/t/table-of-contents-widget/3470/8?u=epogrebnyak"""
    def __init__(self):
        self._items = []
        self._placeholder = None
    
    def title(self, text):
        self._markdown(text, "h1")

    def header(self, text):
        self._markdown(text, "h2", " " * 2)

    def subheader(self, text):
        self._markdown(text, "h3", " " * 4)

    def placeholder(self, sidebar=False):
        self._placeholder = st.sidebar.empty() if sidebar else st.empty()

    def generate(self):
        if self._placeholder:
            self._placeholder.markdown("\n".join(self._items), unsafe_allow_html=True)
    
    def _markdown(self, text, level, space=""):
        key = text.lower().replace('(','').replace(')','').replace(' ','-')

        st.markdown(f"<{level} id='{key}'>{text}</{level}>", unsafe_allow_html=True)
        self._items.append(f"{space}* <a href='#{key}'>{text}</a>")