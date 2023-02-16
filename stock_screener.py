#########################>cd /d D:\SN\Python
#########################>streamlit run stock_screener.py

# finance api
import yahoofinancials
import yahooquery as yq
import yfinance as yf
import nasdaqdatalink as ndl

# data
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

# visualization
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
import streamlit as st
from plotly.subplots import make_subplots
from annotated_text import annotated_text

# web scrapping
import requests
import json
import time
import re
import lxml
import cchardet
from bs4 import BeautifulSoup

NASDAQ_DATA_LINK_API_KEY = "xy8jtvPFDhiwnFktEugz"  # ndl.ApiConfig.api_key
pd.set_option("display.max_columns", None)

pio.templates.default = "plotly_dark"

######################################################################################################################
# Defining variables

STOCK = st.text_input(
    "Enter a ticker",
    label_visibility='visible',
    disabled=False,
    placeholder='AAPL',
).upper()

STOCKS_LIST = [
    "AAPL",
    "ABBV",
    "ABR",
    "ABT",
    "AFL",
    "AMD",
    "AMGN",
    "AMZN",
    "ASML",
    "ATVI",
    "AVGO",
    "BBY",
    "BHP",
    "BRK-B",
    "CCI",
    "COST",
    "CSCO",
    "CVX",
    "GOOGL",
    "HD",
    "IRM",
    "JNJ",
    "JPM",
    "LOW",
    "MA",
    "MAIN",
    "MCD",
    "MCO",
    "MDT",
    "META",
    "MRK",
    "MS",
    "MSFT",
    "NFLX",
    "NVDA",
    "O",
    "PEP",
    "PFE",
    "PLD",
    "PYPL",
    "SBUX",
    "STOR",
    "TGT",
    "TROW",
    "TSLA",
    "TSM",
    "UNP",
    "UPS",
    "V",
    "VICI",
    "WPC",
    "XOM",
    "ZTS",
]

CRYPTO_LIST = ["BTC-USD", "ETH-USD"]

ETF_LIST = ["SCHD", "SPHD", "VOO", "QQQ", "VGT", "ARKK"]

WATCHLIST_LIST = ["MO", "T"]

stock_list_new = [x.lower() if x != 'BRK-B' else 'brk.b' for x in STOCKS_LIST]
stock_list_test = [STOCK]

# https://www.simplysafedividends.com/world-of-dividends/posts/41-2022-dividend-kings-list-all-47-our-top-5-picks
# https://www.simplysafedividends.com/world-of-dividends/posts/6-2023-dividend-aristocrats-list-all-65-our-top-5-picks
PATH_ARICTOCRAT = 'Dividend Aristocrats - 2023-02-14-22-43-13.csv'
PATH_KING = 'Dividend Kings - 2023-02-14-22-43-26.csv'

######################################################################################################################

div_safety_metrics = [
    "div_safety_category",
    "cash_div_payout_ratio_ttm",
    "div_payout_gaap",
    "div_payout_nongaap",
    "div_payout_nongaap_fy1",
    "cf_payout",
    "cf_payout_fy1",
    "fcf_yield_div_yield",
    "div_yield_div_payout",
    "div_coverage_ratio_fy1",
    "int_cover",
    "net_lt_debt_tot_assets",
    "net_lt_debt_ebitda",
    "debt_eq",
    "tot_debt_cap",
    "net_margin",
    "rtn_on_common_equity",
    "cash_from_operations_as_reported",
    "cash_per_share_ttm",
    "log_of_unadjusted_stock_price",
    "capm_alpha_60m",
    "institutional_ownership_level",
    "sustainable_growth_rate",
    "div_grow_rate",
    "dividend_coverage_ratio_ttm",
    "fixed_asset_turnover_ttm",
    "dps_consensus_mean_percent_revisions_down_1_annual_period_fwd",
    "net_asset_to_pension_liabilities_annual",
    "div_safety_category_avg_5y",
    "cash_div_payout_ratio_ttm_avg_5y",
    "div_payout_gaap_avg_5y",
    "div_payout_nongaap_avg_5y",
    "div_payout_nongaap_fy1_avg_5y",
    "cf_payout_avg_5y",
    "cf_payout_fy1_avg_5y",
    "fcf_yield_div_yield_avg_5y",
    "div_yield_div_payout_avg_5y",
    "div_coverage_ratio_fy1_avg_5y",
    "int_cover_avg_5y",
    "net_lt_debt_tot_assets_avg_5y",
    "net_lt_debt_ebitda_avg_5y",
    "debt_eq_avg_5y",
    "tot_debt_cap_avg_5y",
    "net_margin_avg_5y",
    "rtn_on_common_equity_avg_5y",
    "cash_from_operations_as_reported_avg_5y",
    "cash_per_share_ttm_avg_5y",
    "log_of_unadjusted_stock_price_avg_5y",
    "capm_alpha_60m_avg_5y",
    "institutional_ownership_level_avg_5y",
    "sustainable_growth_rate_avg_5y",
    "div_grow_rate_avg_5y",
    "dividend_coverage_ratio_ttm_avg_5y",
    "fixed_asset_turnover_ttm_avg_5y",
    "dps_consensus_mean_percent_revisions_down_1_annual_period_fwd_avg_5y",
    "net_asset_to_pension_liabilities_annual_avg_5y",
]

div_growth_metrics = [
    "div_growth_category",
    "dps_yoy",
    "dividend_per_share_change_dislpay",
    "dividend_lt_fwd_growth",
    "div_grow_rate3",
    "div_grow_rate5",
    "div_grow_rate10",
    "revenue_change_display",
    "eps_change_display",
    "fcf_per_share_change_display",
    "ebitda_change_display",
    "ebit_change_display",
    "return_on_net_tangible_assets",
    "log_of_unadjusted_stock_price",
    "coefficient_of_variation_90d",
    "degree_of_operating_leverage_ttm",
    "div_growth_category_avg_5y",
    "dps_yoy_avg_5y",
    "dividend_per_share_change_dislpay_avg_5y",
    "dividend_lt_fwd_growth_avg_5y",
    "div_grow_rate3_avg_5y",
    "div_grow_rate5_avg_5y",
    "div_grow_rate10_avg_5y",
    "revenue_change_display_avg_5y",
    "eps_change_display_avg_5y",
    "fcf_per_share_change_display_avg_5y",
    "ebitda_change_display_avg_5y",
    "ebit_change_display_avg_5y",
    "return_on_net_tangible_assets_avg_5y",
    "log_of_unadjusted_stock_price_avg_5y",
    "coefficient_of_variation_90d_avg_5y",
    "degree_of_operating_leverage_ttm_avg_5y",
]

div_yield_metrics = [
    "div_yield_category",
    "div_yield_4y",
    "dividend_yield",
    "div_yield_fwd",
    "yld_on_cost_1y",
    "yld_on_cost_3y",
    "yld_on_cost_5y",
    "earnings_yield",
    "earn_yield_gaap_fy1",
    "oper_income_market_cap",
    "oper_income_fy1_market_cap",
    "fcf_yield",
    "fcf_yield_fy1",
    "div_yield_category_avg_5y",
    "div_yield_4y_avg_5y",
    "dividend_yield_avg_5y",
    "div_yield_fwd_avg_5y",
    "yld_on_cost_1y_avg_5y",
    "yld_on_cost_3y_avg_5y",
    "yld_on_cost_5y_avg_5y",
    "earnings_yield_avg_5y",
    "earn_yield_gaap_fy1_avg_5y",
    "oper_income_market_cap_avg_5y",
    "oper_income_fy1_market_cap_avg_5y",
    "fcf_yield_avg_5y",
    "fcf_yield_fy1_avg_5y",
]

div_history_metrics = [
    "div_consistency_category",
    "dividend_growth",
    "dividend_consistency",
    "div_consistency_category_avg_5y",
    "dividend_growth_avg_5y",
    "dividend_consistency_avg_5y",
]

earnings_metrics = [
    "analysts_up_percent",
    "analysts_down_percent",
    "analysts_up",
    "analysts_down",
    "analysts_up_percent_avg_5y",
    "analysts_down_percent_avg_5y",
    "analysts_up_avg_5y",
    "analysts_down_avg_5y",
]

valuation_metrics = [
    "pe_nongaap",
    "pe_nongaap_fy1",
    "pe_ratio",
    "pe_gaap_fy1",
    "peg_gaap",
    "peg_nongaap_fy1",
    "ev_12m_sales_ratio",
    "ev_sales_fy1",
    "ev_ebitda",
    "ev_ebitda_fy1",
    "ev_ebit",
    "ev_ebit_fy1",
    "ps_ratio",
    "ps_ratio_fy1",
    "pb_ratio",
    "pb_fy1_ratio",
    "price_cf_ratio",
    "price_cf_ratio_fy1",
    "dividend_yield",
    "pe_nongaap_avg_5y",
    "pe_nongaap_fy1_avg_5y",
    "pe_ratio_avg_5y",
    "pe_gaap_fy1_avg_5y",
    "peg_gaap_avg_5y",
    "peg_nongaap_fy1_avg_5y",
    "ev_12m_sales_ratio_avg_5y",
    "ev_sales_fy1_avg_5y",
    "ev_ebitda_avg_5y",
    "ev_ebitda_fy1_avg_5y",
    "ev_ebit_avg_5y",
    "ev_ebit_fy1_avg_5y",
    "ps_ratio_avg_5y",
    "ps_ratio_fy1_avg_5y",
    "pb_ratio_avg_5y",
    "pb_fy1_ratio_avg_5y",
    "price_cf_ratio_avg_5y",
    "price_cf_ratio_fy1_avg_5y",
    "dividend_yield_avg_5y",
]

growth_metrics = [
    "revenue_growth",
    "revenue_change_display",
    "ebitda_yoy",
    "ebitda_change_display",
    "operating_income_ebit_yoy",
    "ebit_change_display",
    "diluted_eps_growth",
    "eps_change_display",
    "eps_ltg",
    "levered_free_cash_flow_yoy",
    "fcf_per_share_change_display",
    "op_cf_yoy",
    "cf_op_change_display",
    "roe_yoy",
    "roe_change_display",
    "working_cap_change",
    "capex_change",
    "dividend_per_share_change_dislpay",
    "dps_yoy",
    "revenue_growth_avg_5y",
    "revenue_change_display_avg_5y",
    "ebitda_yoy_avg_5y",
    "ebitda_change_display_avg_5y",
    "operating_income_ebit_yoy_avg_5y",
    "ebit_change_display_avg_5y",
    "diluted_eps_growth_avg_5y",
    "eps_change_display_avg_5y",
    "eps_ltg_avg_5y",
    "levered_free_cash_flow_yoy_avg_5y",
    "fcf_per_share_change_display_avg_5y",
    "op_cf_yoy_avg_5y",
    "cf_op_change_display_avg_5y",
    "roe_yoy_avg_5y",
    "roe_change_display_avg_5y",
    "working_cap_change_avg_5y",
    "capex_change_avg_5y",
    "dividend_per_share_change_dislpay_avg_5y",
    "dps_yoy_avg_5y",
]

growth_symbol_data_fields = [
    "revenue_growth",
    "revenue_growth3",
    "revenue_growth5",
    "revenueGrowth10",
    "ebitdaYoy",
    "ebitda_3y",
    "ebitda_5y",
    "ebitda_10y",
    "operatingIncomeEbitYoy",
    "operatingIncomeEbit3y",
    "operatingIncomeEbit5y",
    "operatingIncomeEbit10y",
    "netIncomeYoy",
    "netIncome3y",
    "netIncome5y",
    "netIncome10y",
    "normalizedNetIncomeYoy",
    "normalizedNetIncome3y",
    "normalizedNetIncome5y",
    "normalizedNetIncome10y",
    "earningsGrowth",
    "earningsGrowth3",
    "earningsGrowth5y",
    "earningsGrowth10y",
    "dilutedEpsGrowth",
    "dilutedEps3y",
    "dilutedEps5y",
    "dilutedEps10y",
    "tangibleBookValueYoy",
    "tangibleBookValue3y",
    "tangibleBookValue5y",
    "tangibleBookValue10y",
    "totalAssetsYoy",
    "totalAssets3y",
    "totalAssets5y",
    "totalAssets10y",
    "leveredFreeCashFlowYoy",
    "leveredFreeCashFlow3y",
    "leveredFreeCashFlow5y",
    "leveredFreeCashFlow10y",
    "net_interest_income_yoy",
    "net_interest_income_3y",
    "net_interest_income_5y",
    "net_interest_income_10y",
    "gross_loans_yoy",
    "gross_loans_3y",
    "gross_loans_5y",
    "gross_loans_10y",
    "common_equity_yoy",
    "common_equity_3y",
    "common_equity_5y",
    "common_equity_10y",
]

profitability_metrics = [
    "gross_margin",
    "ebit_margin",
    "ebitda_margin",
    "net_margin",
    "levered_fcf_margin",
    "rtn_on_common_equity",
    "return_on_total_capital",
    "return_on_avg_tot_assets",
    "capex_to_sales",
    "assets_turnover",
    "cash_from_operations_as_reported",
    "net_inc_per_employee",
    "gross_margin_avg_5y",
    "ebit_margin_avg_5y",
    "ebitda_margin_avg_5y",
    "net_margin_avg_5y",
    "levered_fcf_margin_avg_5y",
    "rtn_on_common_equity_avg_5y",
    "return_on_total_capital_avg_5y",
    "return_on_avg_tot_assets_avg_5y",
    "capex_to_sales_avg_5y",
    "assets_turnover_avg_5y",
    "cash_from_operations_as_reported_avg_5y",
    "net_inc_per_employee_avg_5y",
]

peers_metrics = [
    "marketcap_display",
    "tev",
    "number_of_employees",
    "authors_count",
    "tot_analysts_recommendations",
    "close",
    "price_high_52w",
    "price_low_52w",
    "p_week_vol_shares",
    "total_return_1m",
    "total_return_3m",
    "total_return_6m",
    "total_return_9m",
    "total_return_ytd",
    "total_return_1y",
    "total_return_3y",
    "total_return_5y",
    "total_return_10y",
    "total_cash",
    "cash_per_share",
    "total_debt",
    "net_debt",
    "debt_eq",
    "debt_short_term",
    "debt_long_term",
    "current_ratio",
    "quick_ratio",
    "interest_coverage_ratio",
    "book_value",
    "debt_fcf",
    "long_term_debt_per_capital",
    "nocf",
    "cash_from_operations_as_reported",
    "levered_free_cash_flow",
    "capital_expenditures",
]

wallstreet_metrics = [
    'authors_rating_strong_buy_count',
    'authors_rating_buy_count',
    'authors_rating_hold_count',
    'authors_rating_sell_count',
    'authors_rating_strong_sell_count',
    'sell_side_rating_strong_buy_count',
    'sell_side_rating_buy_count',
    'sell_side_rating_hold_count',
    'sell_side_rating_sell_count',
    'sell_side_rating_strong_sell_count',
    'authors_rating',
    'sell_side_rating',
]

div_estimate_metrics = [
    "dividends_estimate_fy1_analyst_up_avg_5y",
    "dividends_estimate_fy1_analyst_down_avg_5y",
    "dividends_estimate_fy2_analyst_up_avg_5y",
    "dividends_estimate_fy2_analyst_down_avg_5y",
    "dividends_estimate_fy1_analyst_up",
    "dividends_estimate_fy1_analyst_down",
    "dividends_estimate_fy2_analyst_up",
    "dividends_estimate_fy2_analyst_down",
]

seeking_alpha_all_metrics = {
    'Dividend safety' : div_safety_metrics,
    'Dividend growth' : div_growth_metrics,
    'Dividend yield' : div_yield_metrics,
    'Dividend history' : div_history_metrics,
    'Earnings' : earnings_metrics,
    'Valuation' : valuation_metrics,
    'Growth' : growth_metrics+growth_symbol_data_fields,
    'Profitability' : profitability_metrics,
    'Wallstreet rating' : wallstreet_metrics,
    }

radar_categories = seeking_alpha_all_metrics.keys()

# https://docs.streamlit.io/library/advanced-features/caching

@st.cache(allow_output_mutation=True)
def get_macrotrends_data(url: str):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")

    var_data = ''
    for script in scripts:
        if "originalData" in script.text:
            var_data = script.text

    # Use regular expressions to extract the variable ???
    match = re.search("var originalData = (.*);", var_data)
    data = match.group(1)
    df = pd.read_json(data)

    for i, k in enumerate(df["field_name"]):
        if BeautifulSoup(k, "html.parser").find("a"):
            df.loc[i, "field_name"] = BeautifulSoup(k, "html.parser").find("a").text
        else:
            df.loc[i, "field_name"] = BeautifulSoup(k, "html.parser").find("span").text

    df = (
        df.drop(columns=["popup_icon"])
        .set_index("field_name")
        .replace("", 0)
        .astype(float)
        .T
    )
    return df

@st.cache(allow_output_mutation=True)
def create_macrotrends_df():
    income_df = get_macrotrends_data(f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/income-statement?freq={freq2}")*1e6
    balance = get_macrotrends_data(f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/balance-sheet?freq={freq2}")*1e6  # ?freq=A
    fin_ratios_df = get_macrotrends_data(f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/financial-ratios?freq={freq2}")
    cash_flow_df = get_macrotrends_data(f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/cash-flow-statement?freq={freq2}")*1e6
    
    df_prices = pd.DataFrame(yf.download([STOCK], start=fin_ratios_df.index.min(), end=fin_ratios_df.index.max())["Adj Close"])
    df_prices.columns = ['Price']
    df_prices['eom'] = [i + relativedelta(day=31) for i in df_prices.index]
    df_prices = df_prices.groupby('eom').last('Price')

    macrotrends_data = pd.concat([income_df, balance, cash_flow_df, fin_ratios_df], axis=1)
    macrotrends_data.index = pd.to_datetime(macrotrends_data.index)
    
    macrotrends_data = pd.concat([macrotrends_data, df_prices], axis=1, join='inner')

    # balance long-term assets not included in macrotrends
    macrotrends_data['Other Long-Term'] = \
        macrotrends_data['Total Long-Term Assets'] - (
            macrotrends_data[[
                "Property, Plant, And Equipment",
                "Long-Term Investments",
                "Goodwill And Intangible Assets",
                "Other Long-Term Assets"
                ]].sum(axis=1)
        )
    
    # https://www.investopedia.com/terms/f/freecashflowyield.asp
    # https://youtu.be/OZ0N74Ea0sg?t=567
    macrotrends_data['Free Cash Flow'] = macrotrends_data['Free Cash Flow Per Share'] * macrotrends_data['Shares Outstanding']
    macrotrends_data['Free Cash Flow Yield'] = macrotrends_data['Free Cash Flow Per Share'] / macrotrends_data['Price']

    macrotrends_data['CAPEX'] = macrotrends_data['Property, Plant, And Equipment'].diff(-1) + macrotrends_data['Total Depreciation And Amortization - Cash Flow']
    macrotrends_data['CAPEX'] = np.where(macrotrends_data['CAPEX']>0, macrotrends_data['CAPEX'], 0)
    # macrotrends_data['SG&A Expenses'] = macrotrends_data['SG&A Expenses'] - macrotrends_data['CAPEX']

    macrotrends_data['Expenses'] = macrotrends_data['Cost Of Goods Sold'] + macrotrends_data['Operating Expenses']
    macrotrends_data['Revenue/Expenses'] = macrotrends_data['Revenue'] / macrotrends_data['Expenses']
    
    # https://www.gurufocus.com/term/ROCE/MSFT/ROCE-Percentage/MSFT
    macrotrends_data['Capital Employed'] = macrotrends_data['Total Assets'] - macrotrends_data['Total Current Liabilities']
    macrotrends_data['ROCE - Return On Capital Employed'] = macrotrends_data['EBIT']/macrotrends_data['Capital Employed']*100

    if freq2 =='Y':
        period = 1
    else:
        period = 4
    
    macrotrends_data['Shares Growth'] = macrotrends_data['Shares Outstanding'].pct_change(-period)

    return macrotrends_data

@st.cache(allow_output_mutation=True)
def create_plot_bar_line(
    df: pd.DataFrame,
    bar=[""],
    line="",
    y2perc=False,
    secondary_y=True,
    bar_color=["#5a7d9f"],
    line_color="white",
    title="",
):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for i, b in enumerate(bar):
        fig.add_bar(
            x=df.index, y=df[b], name=b, secondary_y=False, marker_color=bar_color[i]
        )

    if title != "":
        title_ = title
    elif len(bar)==1:
        title_ = bar[0]
    else:
        title_=''

    fig.update_layout(
        height=400,
        width=600,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        title=title_,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25, xanchor="left"
        ),
    )

    if line != "":
        fig.add_scatter(
            x=df.index,
            y=df[line],
            name=line,
            secondary_y=secondary_y,
            marker_color=line_color,
        )
        if y2perc:
            fig.update_layout(yaxis2=dict(tickformat=".0%"))

    # fig.show()

    return fig

def create_ema_plot(tickers_list, start_date="2021-01-01", period="days", emas=[1]):

    colors = {
        "standard": "#424242",
        "min": "#00ab41",
        "other": "#8B8000",
        "max": "#c30010",
    }

    df_orig = pd.DataFrame(yf.download(tickers_list, start_date)["Adj Close"])

    if len(tickers_list) > 1:
        vertical_spacing = (1 / (len(tickers_list) - 1)) / 9
    else:
        vertical_spacing = 0
        df_orig.columns = tickers_list

    df = df_orig.copy()

    for n in emas:
        ema_period = f"{n} {period}"
        ema_df = df_orig.ewm(
            halflife=ema_period, times=df_orig.index, ignore_na=False
        ).mean()
        ema_df.columns = [f"{c}_{n}{period}_ema" for c in ema_df.columns]
        df = pd.concat([df, ema_df], axis=1)

    fig = make_subplots(
        rows=len(tickers_list),
        cols=1,
        # subplot_titles=tickers_list,
        vertical_spacing=vertical_spacing,
    )

    for i, c in enumerate(tickers_list, start=1):
        df_columns = [col for col in df.columns if col.startswith(c + "_") | (col == c)]
        df_new = df[df_columns].copy()
        for i2, c2 in enumerate(df_columns):

            if i2 == 0:
                color = colors["standard"]
                width = 2
            elif i2 == 1:
                color = colors["min"]
                width = 2
            elif i2 == len(df_columns) - 1:
                color = colors["max"]
                width = 2
            else:
                color = colors["other"]
                width = 0.5

            fig.add_trace(
                go.Scatter(
                    x=df_new.index,
                    y=df_new[c2],
                    line=dict(color=color, width=width),
                    name=c2,
                ),
                row=i,
                col=1,
            )

    fig.update_layout(
        height=len(tickers_list) * 400,
        width=600,
        showlegend=False,
        title="Exponential Moving Average",
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
    )

    # fig.show()
    st.plotly_chart(fig, use_container_width=True)

    return fig

def create_schd_plot(tickers_list, start_date="2013-01-01"):
    
    df = pd.DataFrame(yf.download(tickers_list+['SCHD'], start_date)["Adj Close"])
    df = df/df.iloc[0,:]*100
    
    if len(tickers_list) > 1:
        vertical_spacing = (1 / (len(tickers_list) - 1)) / 9
    else:
        vertical_spacing = 0
        df.columns = tickers_list+['SCHD']
    
    fig = make_subplots(
        rows=len(tickers_list),
        cols=1,
        vertical_spacing=vertical_spacing,
    )
    
    for i, c in enumerate(tickers_list, start=1):
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[c],
                line=dict(color="white"),
                name=c,
            ),
            row=i,
            col=1,
        )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['SCHD'],
            line=dict(color="#4066e0"),
            name='SCHD',
        ),
        row=1,
        col=1,
    )
    
    fig.update_layout(
        height=len(tickers_list) * 400,
        width=600,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        title="Stock Price Dynamics",
        template="plotly_dark",
        yaxis_ticksuffix = "%"
    )

    # fig.show()
    st.plotly_chart(fig, use_container_width=True)

    return fig

@st.cache(allow_output_mutation=True)
def create_line_plot(df: pd.DataFrame, y: list, title="", perc=True):
    fig = go.Figure()

    for line in y:
        fig.add_scatter(x=df.index, y=df[line], name=line)

    fig.update_layout(
        height=400,
        width=600,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.30, xanchor="left"
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        title=title,
    )

    if perc:
        fig.update_layout(yaxis=dict(tickformat=".1%"))

    # fig.show()

    return fig

@st.cache(allow_output_mutation=True)
def create_div_history_df(stock_list = stock_list_test):
    """Seeking alpha full dividend history"""
    div_history_df = pd.DataFrame()

    for tick in stock_list:
        url = f"https://seekingalpha.com/api/v3/symbols/{tick.lower()}/dividend_history"
        querystring = {"years":"100"}
        headers = {
            "cookie": "machine_cookie=4979826528810; _cls_v=072cd8fc-83ec-4b6d-b840-72ce92a351d4; _cls_s=da78f999-6e82-4412-bfd3-98a35379d96d:0; _pxvid=6190f403-0540-11ed-8356-71796f6e5767; pxcts=61910480-0540-11ed-8356-71796f6e5767; g_state=^{^\^i_l^^:0^}; has_paid_subscription=false; OptanonAlertBoxClosed=2022-07-16T19:49:37.138Z; _ga=GA1.2.422884809.1658000977; _igt=80f0662b-29d6-4ba2-daef-f15a084be986; _hjSessionUser_65666=eyJpZCI6IjVmNjA3NTU1LTFmODItNWFhOC05NzBkLTMxNmIwOTFkNDJjZSIsImNyZWF0ZWQiOjE2NTgwNDMwMjQxNTYsImV4aXN0aW5nIjp0cnVlfQ==; _hjCachedUserAttributes=eyJhdHRyaWJ1dGVzIjp7ImxvZ2dlZF9pbiI6dHJ1ZSwibXBfc3ViIjpmYWxzZSwicHJlbWl1bV9zdWIiOmZhbHNlLCJwcm9fc3ViIjpmYWxzZX0sInVzZXJJZCI6IjU2ODczOTA0In0=; ga_clientid=422884809.1658000977; _pcid=^%^7B^%^22browserId^%^22^%^3A^%^22l6l1zvh16ggo2rl5^%^22^%^7D; _clck=1sv21qj^|1^|f4c^|0; _ig=56873904; sailthru_content=2528dc295dc3fbbf1ec8e71fd6af16ea5ed0fab1751712d30b586234ac21ac69c6f48017810681510ac670347a1b237b395addcc8a084ec17e397065464a467803e85c27969d6ca11adf1e5bae9ce43e365ade53ba1716e0f5409199ca81b1b2d336ff2bdab2770099e746360c3b2e4a8f46c8cbd3b263891ad28c66986af90e8a2bb0fb3446957f12521164830063aa9eada221935b05aaed9d45ccc5957509; sailthru_visitor=4a85db3b-194e-42bd-bc87-31076f836304; sailthru_hid=29f91ce2c0119534955a4934eea65d5d62d3164919e4cd8e5507453023d2712d74fca4d95585b51117583622; _gcl_au=1.1.905016176.1671643238; __pat=-18000000; user_id=56873904; user_nick=; user_devices=2; u_voc=; marketplace_author_slugs=; user_cookie_key=cjjdiz; user_perm=; sapu=101; user_remember_token=04b7dcb2602e3f78db1c7c7b3e0e43599aa202f5; _sapi_session_id=0pCP6BL7ckaTjzz1yGfnvj2fYymMCVyRcdc0FilJJuJrLs^%^2BPk6M7pmkTNZq^%^2Bs0tQzLw0Gwxfpuz4XXdeLwjnEvGdwVGKVQdIhiI4kf6GgA6c6Aqo8EAHDVX3JUirUkOfv7^%^2Fv6zuUolHyz^%^2Bka3l7tx2Tmr6LfeaHe0syKkJJ99iSM^%^2FbcPrEEdST3wciFuUBwzxt3V9trL98gAlWdoY4Ces0hsdCU^%^2BEryApHpHc9rt8S2ZjmXsQ7PNxkHufEwIxhqC2LmTKsoVyrOgYz4rWUiq8CGM^%^2BdxILxHnEzl1LN9h2hU^%^3D--^%^2Fq^%^2FbqzYaui40jz7x--I^%^2FfbuLyN7DqYI^%^2BHocBaR9A^%^3D^%^3D; _pctx=^%^7Bu^%^7DN4IgrgzgpgThIC5QFYBsAOA7AZgJwAYAWRUABxigDMBLAD0RBABoQAXAT1KgYDUANEAF9BLSLADKrAIatIDCgHNqEVrCgATZiAjVVASU0IAdmAA2pwUA; _pxhd=9b81b7053d831d0e418b92698dce0fc88c8297e1e67eb88e98fefc26b9d3b6ac:80650f60-6b3b-11e9-814e-41aaaa844f02; ubvt=b26b3487-0e8c-451d-9656-705df157b6a2; session_id=27a89810-0094-4454-8793-f52f76340fbd; OptanonConsent=isIABGlobal=false&datestamp=Thu+Dec+22+2022+16^%^3A05^%^3A26+GMT^%^2B0100+(czas+^%^C5^%^9Brodkowoeuropejski+standardowy)&version=6.30.0&landingPath=NotLandingPage&groups=C0001^%^3A1^%^2CC0002^%^3A1^%^2CC0003^%^3A1^%^2CC0007^%^3A1&hosts=H40^%^3A1^%^2CH17^%^3A1^%^2CH13^%^3A1^%^2CH36^%^3A1^%^2CH55^%^3A1^%^2CH69^%^3A1^%^2CH45^%^3A1^%^2CH14^%^3A1^%^2CH15^%^3A1^%^2CH19^%^3A1^%^2CH47^%^3A1&AwaitingReconsent=false&genVendors=V12^%^3A1^%^2CV5^%^3A1^%^2CV7^%^3A1^%^2CV8^%^3A1^%^2CV13^%^3A1^%^2CV15^%^3A1^%^2CV3^%^3A1^%^2CV2^%^3A1^%^2CV6^%^3A1^%^2CV14^%^3A1^%^2CV1^%^3A1^%^2CV4^%^3A1^%^2CV9^%^3A1^%^2C&geolocation=PL^%^3B14; __pnahc=1; gk_user_access=1**1671790151; gk_user_access_sign=316999477f1cf3b270ec2daee33355ef077c23cf; __tac=; __tae=1671790157992; LAST_VISITED_PAGE=^%^7B^%^22pathname^%^22^%^3A^%^22https^%^3A^%^2F^%^2Fseekingalpha.com^%^2Fsymbol^%^2FDPZ^%^2Fdividends^%^2Fhistory^%^22^%^2C^%^22pageKey^%^22^%^3A^%^22ba85820c-c9a7-4301-91ed-047be2dec0c2^%^22^%^7D; _uetsid=c9555410815311ed8383e1bd89176270; _uetvid=6c9a7a40054011ed9912e34a5318d584; __pvi=eyJpZCI6InYtMjAyMi0xMi0yMy0xMS0wOS0xNC0zMDYtRFVlQXM1NWtGcHdFelhldy05OWVlM2VhYmJkMDU0N2NiMjRiMjQ2ZTU5ZTc4YmQ4OCIsImRvbWFpbiI6Ii5zZWVraW5nYWxwaGEuY29tIiwidGltZSI6MTY3MTc5MDY2ODc4NH0^%^3D; __tbc=^%^7Bkpex^%^7Dc34b4dUSkelinBilgVjlXAFjdExL2yDTVVsaH2tHeWieSgu52a503DdkAZX5En4R; xbc=^%^7Bkpex^%^7DpsZvcg-czvsWNhuvqvMZK8J5UpYhUPaAf31G9LNO4s_JNybiiLibHlVRHn3hm4E4nn-OgFei0KNGMmPkAUA1_w-h83kuroSVs6Wm4u7Ywo2khMWDgt1X4fFsw_eRSpv_RT073ml6wbguc-BKt5xBC3jze6MTqMhOTtHPaQlo8jgrWISTUeJdpSW5wg1k8whSzoS5_JJNFGD12hP_7LIJ9Rcboio5C_pfp4SlYIgOvl0t0F4JUlwH3AItmjnB36P2lQd46Wi4gj8SrJp-WVo44vskLuAbTmezh-9Nmb6v2dAtnefy1d_SnhK1ucoCCPyx9eHnXkzHTxLTKoa4V1CaJBGXBFnLuyNvM48L074T6SRARQTZyVNljtYreNy7Uxb-agK4V0R54vP3iIc0NEPleFizxGh8FZZoF4flQb7mGezf-1HBFpWUlIR7p55GktmivP2SWPpXI1SzKXApvhhYN_mlYAm6eHG7Pq1LZgIR4zWUkv2RKy3rJd9Qsk8cHLPlvjhuRmx_t1ZjQa7IsxW7_03FS_lF67VC3PfVw_sI7vJlVj9ccU7hT9ptOtwx7ECKKYPkv5zP7q_a3Yubi4CmIM5MP-cJhy_-6RU96KhQ-FqXxVYETn_nJbtT3MXgwQma1soxbODUZ0d9NKNDWU5_lu9l2WXp88Vf-PdLt9LNv-Q",
            "authority": "seekingalpha.com",
            "referer": f"https://seekingalpha.com/symbol/{tick}/dividends/history",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        response = requests.request("GET", url, headers=headers, params=querystring).json()['data']

        for id in response:
            row = pd.DataFrame([id['attributes']])
            row['Ticker'] = tick
            div_history_df = pd.concat([div_history_df, row], axis=0)

        if len(stock_list) >1:
            time.sleep(2) # in case of generating data on more then 1 ticker

    for c in [c for c in div_history_df.columns if '_date' in c]:
        div_history_df[c] = pd.to_datetime(div_history_df[c])

    div_history_df['amount'] = div_history_df['amount'].astype(float)
    div_history_df = div_history_df.reset_index(drop=True).set_index('date')

    return div_history_df

@st.cache(allow_output_mutation=True)
def create_income_statement(period = 'quarterly', stock_list = stock_list_test):
    income_statement = pd.DataFrame()

    for x in stock_list: # STOCKS_LIST

        url = f"https://stockanalysis.com/stocks/{x.lower()}/financials/__data.json"

        querystring = {"x-sveltekit-invalidated":"__1"} # also period can be "trailing" or no period at all (annual)
        if (period == 'quarterly')|(period == 'trailing'):
            querystring['period'] = period

        headers = {
            "authority": "stockanalysis.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,uk-UA;q=0.6,uk;q=0.5,pl;q=0.4",
            "cookie": "cf_chl_2=9c80dd02f1fc73c; cf_clearance=OwRTeLsjteKSq2vOGA415U77v0RksWzpM_0xtiixnIA-1671821196-0-160",
            "referer": f"https://stockanalysis.com/stocks/{x.lower()}/financials/",
            "sec-ch-ua": "^\^Not?A_Brand^^;v=^\^8^^, ^\^Chromium^^;v=^\^108^^, ^\^Google",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        
        response = requests.request("GET", url, headers=headers, params=querystring).json()

        # with open("stock_analysis.json", "w") as outfile:
        #     json.dump(response, outfile)

        response_new = response['nodes']
        for i in response_new:
            if i['type'] != 'skip':
                data = list(i['data'])
        
        dict1 = {}
        for k, v in zip(data[0].keys(), data[0].values()):
            dict1[k] = data[v]

        dict2 = {}
        for k, v in zip(dict1['financialData'].keys(), dict1['financialData'].values()):
            dict2[k] = data[v]

        dict3 = {}
        for k, v_list in zip(dict2.keys(), dict2.values()):
            values = []
            for v in v_list:
                values = values + [data[v]]
            dict3[k] = values

        dict_names = {}
        for m in dict1['map']:
            dict_names[data[data[m]['id']]] = data[data[m]['title']]
        dict_names['fcf'] = 'Free Cash Flow'
        dict_names['datekey'] = 'Date'

        income_df = pd.DataFrame(dict3)
        # income_df['Ticker'] = x
        income_df = income_df.rename(columns=dict_names)
        
        income_statement = pd.concat([income_statement, income_df], axis=0)

        # time.sleep(4) # in case of generating data on more then 1 ticker

    income_statement = income_statement.set_index('Date')

    if period!='quarterly':
        income_statement = income_statement.drop('TTM')

    income_statement.index = pd.to_datetime(income_statement.index)

    income_statement['Dividends'] = income_statement['Dividend Per Share'] * income_statement['Shares Outstanding (Basic)']

    shifting_dict = {'quarterly':-4, 'yearly':-1}

    income_diff = (income_statement/income_statement.shift(periods=shifting_dict[period]))-1

    income_statement = pd.merge(income_statement, income_diff, left_index=True, right_index=True, suffixes=[""," Growth (YoY)"])
    
    income_statement = income_statement.drop([c for c in income_statement.columns if "Growth (YoY) Growth (YoY)" in c], axis=1)

    income_statement = income_statement.loc[:,~income_statement.columns.duplicated()].copy()

    return income_statement

@st.cache(allow_output_mutation=True)
def create_expenses_df(df:pd.DataFrame):
    # expenses dataframe for plot
    expenses = [
        'Selling & Marketing',
        'General & Administrative',
        'Selling, General & Admin',
        'Research & Development',
        'Other Operating Expenses',
        "Interest Expense",
        'Interest Expense / Income',
        'Other Expense / Income'
        ]
    df_expenses = df.loc[:,[c for c in df.columns if c in expenses]]
    for c in df_expenses.columns:
        if 'Expense / Income' in c:
            for i in df_expenses.index:
                if df_expenses.loc[i,c]>0:
                    df_expenses.loc[i,c] = 0
                else:
                    df_expenses.loc[i,c] = -df_expenses.loc[i,c]
    return df_expenses

def create_stacker_bar(
    df: pd.DataFrame, title_="", colors=px.colors.sequential.Viridis
):

    fig = px.bar(data_frame=df, color_discrete_sequence=colors)

    fig.update_layout(
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        height=400,
        width=600,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.4, xanchor="left", title=None
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        title=title_,
    )
    # fig.show()
    
    # st.plotly_chart(fig, use_container_width=True)

    return fig

@st.cache(allow_output_mutation=True)
def get_macrotrends_html(url=""):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    html_table = soup.find("table", {"class": "table"}).prettify()
    df = pd.read_html(html_table)[0]
    df.columns = df.columns.get_level_values(1)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()

    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = pd.to_numeric(
                df[c].str.replace("$", "", regex=False), errors="coerce"
            )
    return df

@st.cache(allow_output_mutation=True)
def get_employees():
    url = f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/number-of-employees"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    html_table = soup.find("table", {"class": "table"}).prettify()
    df = pd.read_html(html_table)[0]
    df['Date'] = [dt.date(y, 12, 31) for y in df.iloc[:,0]]
    df = df.iloc[:,1:].set_index('Date')
    df.columns = ['Number of employees']
    return df

def create_3_subplots(df: pd.DataFrame, indicators: dict, _title=""):

    # Create a figure with subplots
    fig = make_subplots(
        rows=len(indicators), cols=1, shared_xaxes=True, vertical_spacing=0.02
    )

    for i, k in enumerate(indicators, start=1):
        fig.add_trace(indicators[k](x=df.index, y=df[k], name=k), row=i, col=1)

        # adding a median
        if "ratio" in k.lower():
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=[df[k].median()] * len(df[k]),
                    name=k + " median",
                    line=dict(color="grey", width=4, dash="dash"),
                ),
                row=i,
                col=1,
            )

    # Update the layout to have shared x-axis
    fig.update_layout(
        height=600,
        width=600,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        hovermode="x unified",
        legend_traceorder="normal",
        title=_title,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        xaxis3=dict(title="Dates"),
    )
    # fig.show()
    # st.plotly_chart(fig, use_container_width=True)

    return fig

@st.cache(allow_output_mutation=True)
def get_data_from_seeking_alpha(metrics_list:list, method=''):

    headers = {
        "cookie": "machine_cookie=9717268612629; machine_cookie_ts=1671790378",
        "authority": "seekingalpha.com",
        "referer": f"https://seekingalpha.com/symbol/{STOCK}/dividends/dividend-growth",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    result = {}

    if method =='grades':
        url = "https://seekingalpha.com/api/v3/ticker_metric_grades"
        querystring = {
            "filter[fields][]": metrics_list,
            "filter[slugs]": f"{STOCK.lower()}",
            "filter[algos][]": ["main_quant", "dividends"],
            "minified": "false",
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring
        ).json()
        for item in response["data"]:
            grade = item["attributes"]["grade"]
            metric_id = item["relationships"]["metric_type"]["data"]["id"]
            for included in response["included"]:
                if included["id"] == metric_id:
                    result[included["attributes"]["field"]] = grade
    
    elif method =='sector':
        url = f"https://seekingalpha.com/api/v3/symbols/{STOCK.lower()}/sector_metrics"
        querystring = {"filter[fields][]": metrics_list}
        response = requests.request(
            "GET", url, headers=headers, params=querystring
        ).json()
        for item in response["data"]:
            value = item["attributes"]["value"]
            metric_id = item["relationships"]["metric_type"]["data"]["id"]
            for included in response["included"]:
                if included["id"] == metric_id:
                    result[included["attributes"]["field"]] = value

    else:
        url = "https://seekingalpha.com/api/v3/metrics"
        querystring = {
            "filter[fields][]": metrics_list,
            "filter[slugs]": f"{STOCK.lower()}",
            "minified": "false",
        }
        
        response = requests.request(
            "GET", url, headers=headers, params=querystring
        ).json()
        for item in response["data"]:
            field = next(
                filter(
                    lambda included: included["id"]
                    == item["relationships"]["metric_type"]["data"]["id"],
                    response["included"],
                )
            )["attributes"]["field"]
            result[field] = item["attributes"]["value"]
            
    return result

@st.cache(allow_output_mutation=True)
def create_seeking_alpha_df(field='All'):
    if field=='All':
        metrics_list = []
        for v in seeking_alpha_all_metrics.values():
            for m in v:
                metrics_list.append(m)
    else:
        metrics_list = seeking_alpha_all_metrics[field]

    metrics = get_data_from_seeking_alpha(metrics_list, "metrics")

    averages = {}    
    for k in list(metrics.keys()):
        if '_avg_5y' in k:
            averages[k] = metrics[k]
            del metrics[k]
    new_keys = {}

    for k, v in list(averages.items()):
        if '_avg_5y' in k:
            new_keys[k] = k.replace("_avg_5y","")

    for old, new in new_keys.items():
        averages[new] = averages.pop(old)

    sector = get_data_from_seeking_alpha(metrics_list, "sector")
    grades = get_data_from_seeking_alpha(metrics_list, "grades")
    
    grades_dict = {
        1: "A+",
        2: "A",
        3: "A-",
        4: "B+",
        5: "B",
        6: "B-",
        7: "C+",
        8: "C",
        9: "C-",
        10: "D+",
        11: "D",
        12: "D-",
        13: "E+",
        14: "E",
        15: "E-",
        16: "F+",
        17: "F",
        18: "F-",
    }

    seeking_alpha_df = pd.DataFrame(
        [metrics, averages, sector, grades], index=["ticker", "avg_5y", "sector", "grade"]
    ).T.dropna()
    seeking_alpha_df['diff_sector'] = seeking_alpha_df["ticker"] / seeking_alpha_df["sector"]
    seeking_alpha_df['diff_avg_5y'] = seeking_alpha_df["ticker"] / seeking_alpha_df["avg_5y"]
    seeking_alpha_df["grade_final"] = seeking_alpha_df["grade"].map(grades_dict)

    return seeking_alpha_df

def create_radar_plot(df_orig: pd.DataFrame, field='', value="grade"):
    if field!='':
        df = df_orig.loc[df_orig['field']==field].copy()
    else:
        df = df_orig.copy()

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=df[value],  # Radial coordinates of each point
            theta=df.index,  # Angular coordinates of each point
            fill="toself",  # Fill the area between the line and the radial axis
            name=value,
            # hovertemplate=[
            #     f'{i}: {df.at[i, "ticker"]:.2%}' for i in df.index
            # ],  # Show ticker on hover
            marker=dict(color="#1fd655"),  # Change color of the plot
        )
    )

    r = np.ones(len(df.index))
    if value=='grade':
        r = r*7

    fig.add_trace(
        go.Scatterpolar(
            r=r,
            theta=df.index,
            name=value,
            # hovertemplate=[
            #     f'{i}: {df.at[i, "sector"]:.2%}' for i in df.index
            # ],  # Show sector on hover
            marker=dict(color="red"),  # Change color of the plot
        )
    )

    # Define the layout of the plot
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True),
            angularaxis=dict(
                direction="clockwise"
            ),  # Set the direction of the angular axis
        ),
        showlegend=False,
        width=800,
        height=500,
        margin=dict(l=200, r=200, t=20, b=20),
    )
    fig.for_each_trace(lambda t: t.update(hoveron="points"))

    # fig.show()
    # st.plotly_chart(fig, use_container_width=True)

    return fig

@st.cache(allow_output_mutation=True)
def create_eps_estimate_df(ticker=STOCK):
    df = yf.Ticker(ticker).earnings_history.iloc[:, 2:]

    df["Earnings Date"] = pd.to_datetime(
        [" ".join(e.split(",")[:-1]) for e in df["Earnings Date"]]
    )

    df["Surprise(%)"] = [
        float(s.replace("+", "")) / 100 if type(s) == str else s
        for s in df["Surprise(%)"]
    ]

    df["EPS Difference"] = (
        df["Reported EPS"] - df["EPS Estimate"]
    )

    df = (
        df.set_index("Earnings Date")
        .dropna(how="all", axis=0)
        .drop_duplicates()
    )

    df["Surprise_abs"] = np.abs(df["Surprise(%)"]).fillna(0)
    return df

@st.cache(allow_output_mutation=True)
def create_eps_estimate_plot(df:pd.DataFrame, size=5, limit=0):
    if limit>0:
        df = df.loc[
            df.index
            >= (dt.date.today() - dt.timedelta(days=365 * limit)).strftime("%Y-%m-%d")
        ]
        size = 20  # earning_history['Surprise_abs']*100

    hover_text = df[["Surprise(%)", "EPS Difference"]].apply(
        lambda x: "Surprise (%): {:.2%} <br>EPS Difference: {:.2f}".format(x[0], x[1]),
        axis=1,
    )

    epsActual_trace = go.Scatter(
        x=df.index,
        y=df["Reported EPS"],
        name="Reported EPS",
        mode="markers",
        marker=dict(
            size=size,
            color=[
                "green"
                if df["Reported EPS"][i] > df["EPS Estimate"][i]
                else "red"
                if df["Reported EPS"][i] < df["EPS Estimate"][i]
                else "grey"
                for i in range(len(df))
            ],
        ),
    )

    epsEstimate_trace = go.Scatter(
        x=df.index,
        y=df["EPS Estimate"],
        name="EPS Estimate",
        mode="markers",
        text=hover_text,
        marker=dict(color="grey", size=size),
    )

    data = [epsActual_trace, epsEstimate_trace]
    layout = go.Layout(title="EPS Estimates")
    fig = go.Figure(data=data, layout=layout)

    fig.update_layout(
        height=400,
        width=600,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        hovermode="x unified",
        barmode="relative",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="left", title=None
        ),
        # showlegend=False
    )
    # fig.show()
    
    return fig

def create_recommendation_plot():

    recommendation_df = yq.Ticker(STOCK).recommendation_trend.reset_index(drop=True)
    for i, p in enumerate(recommendation_df["period"]):
        recommendation_df.loc[i, "date"] = dt.date.today() + dt.timedelta(
            days=30 * int(recommendation_df.loc[i, "period"].replace("m", ""))
        )
    recommendation_df["date"] = [d.strftime("%Y-%m") for d in recommendation_df["date"]]
    recommendation_df = recommendation_df.set_index("date").drop(["period"], axis=1)

    colors = [
        "#ff6962",
        "#ff8989",
        "#ffb3a5",
        "#77dd76",
        "#03c03c",
    ]  # '#5fa777' 7abd91 # colors=px.colors.sequential.Rainbow
    data = []

    for i, column in enumerate(recommendation_df.columns[::-1]):
        data.append(
            go.Bar(
                x=recommendation_df.index,
                y=recommendation_df[column],
                name=column,
                text=recommendation_df[column],
                textfont={"color": "black"},
                textposition="inside",
                marker=dict(color=colors[i]),
            )
        )

    layout = go.Layout(title="Recommendations", barmode="stack")

    fig = go.Figure(data=data, layout=layout)

    fig.update_layout(
        height=400,
        width=400,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        hovermode="x unified",
    )
    # fig.show()
    st.plotly_chart(fig, use_container_width=True)
    return fig

def create_52w_plot(start_date=(dt.date.today() - dt.timedelta(days=365 * 2))):
    
    prices_df = pd.DataFrame(
        yf.download(
            stock_list_test,
            start_date.strftime("%Y-%m-%d"),
        )["Adj Close"]
    )
    prices_df["rolling_max"] = prices_df["Adj Close"].rolling(window=252).max()
    prices_df["rolling_min"] = prices_df["Adj Close"].rolling(window=252).min()
    prices_df["rolling_avg"] = prices_df["Adj Close"].rolling(window=252).mean()
    prices_df = prices_df.dropna(axis=0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=prices_df["rolling_min"], x=prices_df.index, mode="lines", name="Minimum 52w"
        )
    )
    fig.add_trace(
        go.Scatter(
            y=prices_df["rolling_max"], x=prices_df.index, mode="lines", name="Maximum 52w"
        )
    )
    fig.add_trace(
        go.Scatter(
            y=prices_df["Adj Close"], x=prices_df.index, mode="lines", name="Current"
        )
    )
    fig.add_trace(
        go.Scatter(
            y=prices_df["rolling_avg"],
            x=prices_df.index,
            mode="lines",
            name="Average 52w",
            line=dict(color="grey", width=4, dash="dash"),
        )
    )

    fig.update_layout(
        title="52 Week Price Range",
        yaxis_title="Price",
        height=400,
        width=600,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="left", title=None),
    )
    # fig.show()
    st.plotly_chart(fig, use_container_width=True)
    return fig

@st.cache(allow_output_mutation=True)
def get_nasdaq_div_data(ticker=STOCK):
    url = f"https://api.nasdaq.com/api/quote/{ticker}/dividends"
    querystring = {"assetclass": "stocks"}

    headers = {
        "authority": "api.nasdaq.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    
    div_dict = {}
    for i in ["exDividendDate", "dividendPaymentDate", "yield", "annualizedDividend"]:
        div_dict[i] = response["data"][i]

    div_dict = pd.DataFrame([div_dict])
    
    return div_dict

@st.cache(allow_output_mutation=True)
def get_yahoo_summary(ticker=STOCK):
    ticker = yq.Ticker(ticker)
    longName = ticker.price[STOCK]['longName']

    summary = pd.DataFrame(ticker.summary_detail)
    if 'dividendYield' in summary.index:
        summary = summary.loc[["dividendYield", "exDividendDate", "trailingAnnualDividendYield", "marketCap","open","payoutRatio"],:] # "beta", 
    else:
        summary = summary.loc[["beta", "marketCap","open"],:]

    financials = pd.DataFrame(ticker.financial_data)
    financials = financials.loc[['currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice'],:]

    profile = pd.DataFrame(ticker.summary_profile)
    profile = profile.loc[["industry", "sector", "country",'longBusinessSummary'],:]

    df = pd.concat([summary, financials, profile])
    df.loc['longName'] = longName

    return df

def highlight_numeric(val):
        if val >0:
            color = 'green'
        elif val <0:
            color = 'red'
        else:
            color = 'orange'
        return 'color: {}'.format(color)

@st.cache(allow_output_mutation=True)
def get_target_prices(df:pd.DataFrame):
    prices_df = df.loc[['currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice'],:]
    prices_df['percentage'] = [i/prices_df.loc['currentPrice'].values[0]-1 for i in prices_df[STOCK]]

    prices_df = prices_df.drop('currentPrice')

    names = {'targetHighPrice':'High', 'targetLowPrice':'Low', 'targetMeanPrice':'Mean', 'targetMedianPrice':'Median'}
    cols = ['Target', 'Percentage']

    prices_df.index = prices_df.index.map(names)
    prices_df.columns = cols

    prices_df = prices_df.style\
        .format(formatter="{:.2%}", subset=['Percentage'])\
        .format(formatter="{:.2f}", subset=['Target'])\
        .applymap(highlight_numeric, subset=['Percentage'])
    return prices_df

@st.cache(allow_output_mutation=True)
def get_last_grades(ticker=STOCK, limit=10):
    ticker = yq.Ticker(ticker)
    grades = ticker.grading_history.reset_index(drop=True)
    grades['epochGradeDate'] = pd.to_datetime(grades['epochGradeDate'])

    # https://www.elearnmarkets.com/blog/what-is-stock-rating/
    grades_dict = {
        "Buy":"A buy rating is a recommendation for buying a specific stock which implies that analysts are expecting the price of a stock to rise in the short- to mid-term. \
                The analysts are usually of the opinion that the stock can surpass the return of similar stocks in the same sector because of reasons such as the launch of a new product or service.",
        
        "Sell": "A sell rating is a recommendation for selling a particular stock which means that the analyst is expecting the price of a stock to fall below its current level in tcrehe short or mid-term.\
                A strong sell rating means that analysts are expecting the price of the specific stock to fall significantly below its current level in the near term.\
                If any analysts recommend a strong sell rating on any stock, then a particular company may end up losing its vital business from the company.",
        
        "Hold":"When an analyst gives a hold rating to stock then they expect it to perform the same with the market or as similar stocks of the same sector.\
                This rating tells the stockbrokers not to buy or sell the stock but to hold.\
                A hold rating is assigned to a stock when there is uncertainty in a company for example regarding new products/services.",
        
        "Underperform":"An underperform rating means that the company may do slightly worse than the market average or the benchmark index. \
                Thus research analysts recommend the traders stay away from the stock.\
                For example, if a stock's total return is 3% and the Nifty's total return is 6%, then it underperformed the index by 3%.",
        
        "Outperform":"An outperform rating is assigned to a stock that is projected to provide returns that are higher than the market average or a benchmark index.\
                For example, if a stock's total return is 10% and the Dow Jones Industrial Average's total return is 6%, it has outperformed the index by 4%.",
        
        "Overweight":"An overweight rating on a stock usually means that it deserves a higher weighting than the benchmark's current weighting for that stock. \
                An overweight rating on a stock means that an equity analyst believes the company's stock price should perform better in the future.",
        
        "Underweight":"Underweight is a sell or don't buy recommendation that analysts give to specific stocks. \
                It means that they think the stock will perform poorly over the next 12 months. \
                This can mean either losing value or growing slowly, depending on market conditions, but it always means that the analyst believes the stock will underperform its market."
    }

    positive_grades = ['Buy','Overweight','Outperform','Market Outperform','Positive','Top Pick','Strong Buy']
    neutral_grades = ['Neutral','Sector Weight','Hold']
    negative_grades = ['Underweight','Sell','Negative','Underperform']

    def highlight_grades(val):
        if val in positive_grades:
            color = 'green'
        elif val in negative_grades:
            color = 'red'
        else:
            color = 'orange'
        return 'color: {}'.format(color)

    def highlight_actions(val):
        if val == 'up':
            color = 'green'
        elif val =='down':
            color = 'red'
        else:
            color = 'white'
        return 'color: {}'.format(color)

    grades = grades.set_index('epochGradeDate')
    grades.columns = ['Firm','To','From','Action']

    grades = grades.iloc[:limit].style\
        .applymap(highlight_grades, subset=['To', 'From'])\
        .applymap(highlight_actions, subset=['Action'])

    return grades

@st.cache(allow_output_mutation=True)
def get_annualized_cagr(df:pd.DataFrame, years=0, period='quarterly'):

    df = df[[c for c in df.columns if ('Growth (YoY)' in c) & ('Growth Growth (YoY)' not in c)]] + 1

    if period=='quarterly':
        years = years*4
        # df = df.loc[[(x.month == df.iloc[:1,:].index.month)[0] for x in df.index],:]

    if (years!=0) & (years<len(df)):
        df = df.iloc[:years].copy()
    else:
        df = df.copy()

    df = df.dropna(axis=0, thresh=5)

    annualized_values = df.cumprod().iloc[-1]**(1/len(df))-1

    return annualized_values

@st.cache(allow_output_mutation=True)
def get_earnings_preds(stock=STOCK):
    ticker = yq.Ticker(stock)

    earnings_trend = pd.DataFrame(ticker.earnings_trend[stock]['trend'])[['period','growth']]

    earnings_dict = {
        '0q':'Current Quarter',
        '+1q':'Next Quarter',
        '0y':'Current Year',
        '+1y':'Next Year',
        '+5y':'Next 5 Years',
        '-5y':'Past 5 Years',
    }

    def highlight_preds(val):
        if val >= 0.08:
            color = 'green'
        elif val < 0:
            color = 'red'
        else:
            color = 'orange'
        return 'color: {}'.format(color)

    earnings_trend['period'] = earnings_trend['period'].map(earnings_dict)
    earnings_trend = earnings_trend.set_index('period')

    earnings_trend.columns = ['Growth']

    earnings_trend = earnings_trend.style.applymap(highlight_preds, subset=['Growth']).format(formatter='{:.2%}', subset=['Growth'])
    
    return earnings_trend

@st.cache(allow_output_mutation=True)
def get_inflation_forecast():
    url = "https://stats.oecd.org/sdmx-json/data/DP_LIVE/.CPIFORECAST.TOT.AGRWTH.A/OECD"
    querystring = {"json-lang":"en","dimensionAtObservation":"allDimensions","startPeriod":"2018"}
    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)

    rates = {k:v[0] for (k,v) in response.json()['dataSets'][0]['observations'].items()}
    df = pd.DataFrame([rates], index=['inflation']).T

    dimensions = response.json()['structure']['dimensions']['observation'][0]['values']
    dict_c = {i: n['name'] for i, n in enumerate(dimensions)} 
    
    df['country'] = [int(i.split(":")[0]) for i in df.index]
    df['country'] = df['country'].map(dict_c)

    time_periods = response.json()['structure']['dimensions']['observation'][5]['values']
    dict_y = {i: int(n['name']) for i, n in enumerate(time_periods)} 

    df['year'] = [int(i.split(":")[-1]) for i in df.index]
    df['year'] = df['year'].map(dict_y)

    df = df\
        .reset_index(drop=True)\
            .query(f"year>{dt.date.today().year}")\
                .groupby('country').agg('mean')[['inflation']]

    return df

@st.cache(allow_output_mutation=True)
def get_valuations(inflation_df:pd.DataFrame, stock=STOCK, margin_of_safety=0.15, discount_multiplier=2):

    income_statement = create_income_statement(period='yearly')

    ticker = yq.Ticker(stock)

    earnings_trend = pd.DataFrame(ticker.earnings_trend[stock]['trend'])[['period','growth']].set_index('period')
    eps_pred = earnings_trend.loc['+5y','growth']

    summary = pd.DataFrame(ticker.summary_detail)
    div_yield = summary.loc['dividendYield'].values[0]
    pe_ratio = summary.loc['forwardPE'].values[0]

    eps_df = ticker.earning_history.reset_index(drop=True)
    eps = eps_df.loc[eps_df['period']=='-1q', 'epsActual'].values[0]

    price = summary.loc['open'].values[0]

    # get AAA corporate yield
    url = "https://ycharts.com/charts/fund_data.json"
    querystring = {"securities":"id:I:USCAAAEY,include:true,,"}
    payload = ""
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    
    aaa_yield = response.json()['chart_data'][0][0]['last_value']/100

    # df = avg forecasted inflation X2, my own idea based on https://www.investopedia.com/terms/d/discountrate.asp
    discount_factor = inflation_df.loc['OECD - Total', 'inflation']/100 * discount_multiplier

    # Lynch: https://youtu.be/qxFgUGixDxQ
    lynch_valuation = (eps_pred + div_yield) / (pe_ratio/100) * price

    # Graham: https://youtu.be/8jmjxXc5H8c
    graham_valuation = ((eps * (8.5 + 2*eps_pred)) * 4.4 / aaa_yield) * margin_of_safety
    graham_valuation_v2 = ((eps * (7 + eps_pred)) * 4.4 / aaa_yield) * margin_of_safety
    
    # DCF model: https://youtu.be/lZzg8lPCY3g
    fcf_avg_growth = np.mean(income_statement.iloc[::-1]['Free Cash Flow'].pct_change())
    last_fcf = income_statement.iloc[0]['Free Cash Flow']
    balance = ticker.balance_sheet().iloc[-1]
    cash = balance['CashAndCashEquivalents']
    debt = balance['TotalDebt']
    shares = income_statement.iloc[0]['Shares Outstanding (Basic)']

    fcf_forecast = {}
    for i in range(1,10):
        if i==1:
            fcf_forecast[i] = last_fcf * (1+fcf_avg_growth)
        else:
            fcf_forecast[i] = fcf_forecast[i-1] * (1+fcf_avg_growth)

    fcf_forecast[10] = fcf_forecast[9] * (1 + aaa_yield) / (discount_factor - aaa_yield)
    pv_forecast = {i:(fcf_forecast[i]/(1+discount_factor)**i) for i in fcf_forecast.keys()}
    
    sum_pv_fcf = sum(pv_forecast.values())

    dcf_valuation = (sum_pv_fcf + cash - debt) / shares

    valuations = pd.DataFrame({
        'Current price':[price],
        'Lynch valuation':[lynch_valuation],
        'Graham valuation':[graham_valuation],
        'Graham valuation (v2)':[graham_valuation_v2],
        'DCF valuation':[dcf_valuation]
    }).T

    return valuations

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################

# nasdaq_div_dict = get_nasdaq_div_data()

yahoo_summary = get_yahoo_summary()
open_percentage = yahoo_summary.loc['open'].values[0] / yahoo_summary.loc['currentPrice'].values[0] -1

country_comment = f"{yahoo_summary.loc['country'].values[0]}" if 'country' in yahoo_summary.index else ""

col1, col2, col3 = st.columns([4,1,1])

with col1:
    st.title(f"{yahoo_summary.loc['longName'].values[0]} ({STOCK})")

with col2:
    if 'dividendYield' in yahoo_summary.index:
        st.metric("Dividend yield", 
                f"{yahoo_summary.loc['dividendYield'].values[0]:.2%}", 
                f"TTM {yahoo_summary.loc['trailingAnnualDividendYield'].values[0]:.2%}",
                delta_color="off")
with col3:
    st.metric("Current price", 
            f"{yahoo_summary.loc['currentPrice'].values[0]:.2f}", 
            f"{open_percentage:.2%}")

st.caption(yahoo_summary.loc['longBusinessSummary'].values[0])

sp500 = pd.read_html('https://www.liberatedstocktrader.com/sp-500-companies/')[1]
sp500.columns = sp500.iloc[0]
sp500 = sp500.iloc[1:].reset_index()

sp500_founded = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
sp_comment = f"(#{sp500.loc[sp500['Ticker']==STOCK, 'index'].values[0]} in SP500)" if STOCK in list(sp500['Ticker']) else ""

dividend_aristocrats = pd.read_csv(PATH_ARICTOCRAT)
dividend_kings = pd.read_csv(PATH_KING)

st.warning("Add table of contents: https://discuss.streamlit.io/t/table-of-contents-widget/3470/8")

col1, col2 = st.columns(2)

with col1:
    if 'marketCap' in yahoo_summary.index:
        st.write(f"<font color='#878787'>*Market cap:*</font> \
            {yahoo_summary.loc['marketCap'].values[0]/1e6:,.0f} M {sp_comment}", unsafe_allow_html=True)

    if STOCK in list(sp500_founded['Symbol']):
        st.write(f"<font color='#878787'>*Founded:*</font> \
            {sp500_founded.loc[sp500_founded['Symbol']==STOCK, 'Founded'].values[0]} in {country_comment}", unsafe_allow_html=True)
    else:
        st.write(f"<font color='#878787'>*Founded:*</font> {country_comment}", unsafe_allow_html=True)

    st.write(f"<font color='#878787'>*Sector:*</font> \
    {yahoo_summary.loc['sector'].values[0]} ({yahoo_summary.loc['industry'].values[0]})", unsafe_allow_html=True)
    
    if 'beta' in yahoo_summary.index:
        st.write(f"<font color='#878787'>*beta:*</font> \
            {yahoo_summary.loc['beta'].values[0]}", unsafe_allow_html=True)
        
with col2:
    if 'payoutRatio' in yahoo_summary.index:
        st.write(f"<font color='#878787'>*Payout ratio:*</font> \
            {yahoo_summary.loc['payoutRatio'].values[0]:.2%}", unsafe_allow_html=True)

    if 'exDividendDate' in yahoo_summary.index:
        st.write(f"<font color='#878787'>*ex-Dividend Date:*</font> \
            {pd.to_datetime(yahoo_summary.loc['exDividendDate'].values[0]).strftime('%Y-%m-%d')}", unsafe_allow_html=True)
    
    # https://github.com/tvst/st-annotated-text
    if STOCK in dividend_kings['Ticker'].to_list():
        div_safety = dividend_kings.loc[dividend_kings['Ticker']==STOCK, 'Dividend Safety'].values[0]
        annotated_text(("Dividend King", div_safety, "#4cbb17"))

    elif STOCK in dividend_aristocrats['Ticker'].to_list():
        div_safety = dividend_aristocrats.loc[dividend_aristocrats['Ticker']==STOCK, 'Dividend Safety'].values[0]
        annotated_text(("Dividend Aristocrat", div_safety, "#000080"))

st.write('## Technical Analysis')

d1 = st.date_input(
    "Select initial date",
    dt.date(2013, 1, 1),
    label_visibility="collapsed")

schd_plot = create_schd_plot([STOCK], start_date=d1.strftime('%Y-%m-%d'))

d2 = st.date_input(
    "Select initial date",
    (dt.date.today() - dt.timedelta(days=365 * 2)),
    label_visibility="collapsed")

plot_52_weeks = create_52w_plot(start_date=d2)

ema_plot = create_ema_plot([STOCK], emas=[10, 20, 30, 40, 50], start_date=d2.strftime('%Y-%m-%d'))

st.write('## Qualitative Analysis')

mean_ = yq.Ticker(STOCK).financial_data[STOCK]['recommendationMean']
key_ = yq.Ticker(STOCK).financial_data[STOCK]['recommendationKey']

col_1, col_2 = st.columns([2,1])
with col_1:
    recommendation_plot = create_recommendation_plot()
with col_2:
    st.metric('Overall recommendation', key_.upper())
    st.slider('Overall recommendation', 1., 5., mean_, label_visibility='collapsed', disabled=True,
              help="1 - Strong Buy, \n2 - Buy, \n3 - Hold, \n4 - Underperform, \n5 - Sell")
    # st.caption("1 - Strong Buy, \t2 - Buy, \t3 - Hold, \t4 - Underperform, \t5 - Sell")
    try:
        prices_df = get_target_prices(yahoo_summary)
        st.write("**Price forecast**")
        st.table(prices_df)
    except:
        st.warning('Action was not succeeded')
    
grades = get_last_grades()
st.table(grades)

eps_estimates = create_eps_estimate_df()
eps_plot = create_eps_estimate_plot(eps_estimates, limit=5)
st.plotly_chart(eps_plot, use_container_width=True)

st.warning("change get_earnings_preds() to get full forecasts")
try:
    earnings_preds = get_earnings_preds()
    st.write("**Earnings forecast**")
    st.table(earnings_preds)
except:
    st.warning('Action was not succeeded')

st.write('## Financial Analysis')

if 'dividendYield' in yahoo_summary.index:
    div_history_df = create_div_history_df()

freq = st.radio(
        "Set frequency",
        ["Quarterly", "Yearly"],
        label_visibility='collapsed',
        horizontal=True,
)
# first letter, Q or Y
freq2 = freq[0]

income_statement = create_income_statement(period=freq.lower())

st.warning('change stockanalysis to macrotrends as a source of income_statement because it has older history (2009 not 2014).\
        Note that you have to calculate CAPEX without depreciation when taking data from macrotrends. simply diff the PP&E in balance. \
        difference between SG&A and you newly calculated CAPEX is in fact the real SG&A (because it is originally included in SG&A in case of macrotrends)')

tickers_macrotrends_dict = {}
macrotrends_list = requests.get(
    "https://www.macrotrends.net/assets/php/ticker_search_list.php?_=1673472383864"
).json()

for e in macrotrends_list:
    url_link = list(e.values())[1]
    ticker = list(e.values())[0].split(" - ")[0]
    tickers_macrotrends_dict[ticker] = url_link

macrotrends_data = create_macrotrends_df()

annualized_data_3y = get_annualized_cagr(income_statement, 3, period=freq.lower())
annualized_data_5y = get_annualized_cagr(income_statement, 5, period=freq.lower())
annualized_data_10y = get_annualized_cagr(income_statement, 10, period=freq.lower())

def print_annualized_data(indicator:str):
    st.write(f"<font color='#878787'>*CAGR*:</font>", unsafe_allow_html=True)
    st.write(f"<font color='#878787'>*3y:*</font> {annualized_data_3y[f'{indicator} Growth (YoY)']:.2%}", unsafe_allow_html=True)
    st.write(f"<font color='#878787'>*5y:*</font> {annualized_data_5y[f'{indicator} Growth (YoY)']:.2%}", unsafe_allow_html=True)
    st.write(f"<font color='#878787'>*10y:*</font> {annualized_data_10y[f'{indicator} Growth (YoY)']:.2%}", unsafe_allow_html=True)

revenue_plot = create_plot_bar_line(
        macrotrends_data, ["Revenue",'Expenses'], "Revenue/Expenses", y2perc=True, bar_color=["#805d67", '#0b6596']
)
income_plot = create_plot_bar_line(
    macrotrends_data, ["Net Income"], "Operating Income", secondary_y=False, bar_color=["#30ba96"]
)
fcf_plot = create_plot_bar_line(
macrotrends_data, ["Free Cash Flow", "Stock-Based Compensation"], "Free Cash Flow Yield", y2perc=True, bar_color=["#8d8b55","#6900c4"] #8d8b55
)

col1, col2 = st.columns([5,1])
with col1:
    st.plotly_chart(revenue_plot, use_container_width=True)
with col2:
    print_annualized_data('Revenue')

st.warning('Maybe delete the YoY Growth from plots and change it to something more useful')

col1, col2 = st.columns([5,1])
with col1:
    st.plotly_chart(income_plot, use_container_width=True)
with col2:
    print_annualized_data('Net Income')

col1, col2 = st.columns([5,1])
with col1:
    st.plotly_chart(fcf_plot, use_container_width=True)
with col2:
    print_annualized_data('Free Cash Flow')

st.warning("Add Free Cash Flow yield: https://youtu.be/OZ0N74Ea0sg?t=567 formula: https://www.investopedia.com/terms/f/freecashflowyield.asp")

with st.expander("**If it's a financial company, don't watch at FCF, rather watch at Price to Book.\
            If it's a REIT, don't watch at FCF either, rather watch at dividend yield growth.**"):

    st.caption("*'If we cannot estimate net capital expenditures or non-cash working capital, we clearly cannot estimate the free cashflow to equity. \
            Since this is the case with financial service firms, we have three choices. \
            The first is to use dividends as cash flows to equity and assume that firms over time pay out their free cash flows to equity as dividends. \
            Since dividends are observable, we therefore do not have to confront the question of how much firms reinvest. \
            The second is to adapt the free cashflow to equity measure to allow for the types of reinvestment that financial service firms make. \
            For instance, given that banks operate under a regulatory capital ratio constraint, it can be argued that these firms have to increase regulatory capital in order to make more loans in the future. \
            The third is to keep the focus on excess returns, rather than on earnings, dividends and growth rates, and to value these excess returns.'* \
            https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/finfirm09.pdf")

# profit_plot = create_plot_bar_line(
#     income_statement, "Gross Profit", "Operating Expenses", secondary_y=False, bar_color="#7c459c"
# )

shares_plot = create_plot_bar_line(
    macrotrends_data, ["Shares Outstanding"], 'Shares Growth', y2perc=True, bar_color=["#ea7726"]
)

if 'dividendYield' in yahoo_summary.index:
    col1, col2 = st.columns([5,1])
    with col1:
        dividends_plot = create_plot_bar_line(
            div_history_df, ["amount"], "adjusted_amount", secondary_y=False, bar_color=["#03c03c"],
        )
        st.plotly_chart(dividends_plot, use_container_width=True)
    with col2:
        print_annualized_data('Dividends')
    
    st.warning("Add historical dividend yield instead of Dividend Growth")

col1, col2 = st.columns([5,1])
with col1:
    st.plotly_chart(shares_plot, use_container_width=True)
with col2:
    print_annualized_data('Shares Outstanding (Basic)')

margins_plot = create_line_plot(
    income_statement,
    y=["Gross Margin", "Operating Margin", "Profit Margin", "Free Cash Flow Margin"],
    title="Margins",
)
st.plotly_chart(margins_plot, use_container_width=True)

# eps_plot = create_plot_bar_line(income_statements, 'EPS (Basic)', 'EPS Growth', y2perc=True, bar_color='#7eb37a')
# dividends_full_history = create_plot_bar_line(div_history_df, 'amount', 'adjusted_amount', title='Full dividend history', bar_color='#03c03c')
# crypto_df = create_ema_plot(CRYPTO_LIST, emas=[10, 20, 30, 40, 50])
# stocks_df = create_ema_plot(STOCKS_LIST, emas=[10, 20, 30, 40, 50])

df_expenses =  macrotrends_data[['Cost Of Goods Sold',
                                 'Research And Development Expenses', 
                                 'SG&A Expenses',
                                 'Other Operating Income Or Expenses']]# #create_expenses_df(df=income_statement)

expenses_plot = create_stacker_bar(df_expenses, title_='Expenses', colors=px.colors.sequential.Turbo_r)
st.plotly_chart(expenses_plot, use_container_width=True)

st.warning('Add Annualized CAGR of total Expenses (total-total, not the sum of df)')

st.warning('Add CAPEX: https://youtu.be/c7GK02L7AFc?t=1255 formula: https://www.wallstreetmojo.com/capital-expenditure-formula-capex/')

assets_full_stackplot = create_stacker_bar(
    macrotrends_data[
        [   # current
            "Cash On Hand",
            "Receivables",
            "Inventory",
            "Pre-Paid Expenses",
            "Other Current Assets",
            # long-term ()
            "Property, Plant, And Equipment",
            "Long-Term Investments",
            "Goodwill And Intangible Assets",
            "Other Long-Term Assets",
            'Other Long-Term'
        ]
    ],
    title_="Total assets",
)

assets_stackplot = create_stacker_bar(
    macrotrends_data[
        [   
            "Total Current Assets",
            "Total Long-Term Assets"
        ]
    ],
    title_="Total assets",
)

liabilities_full_stackplot = create_stacker_bar(
    macrotrends_data[
        [   
            "Total Current Liabilities",
            "Long Term Debt",
            "Other Non-Current Liabilities",
            "Common Stock Net",
            "Retained Earnings (Accumulated Deficit)",
            "Comprehensive Income",
            "Other Share Holders Equity"
        ]
    ],
    title_="Total liabilities",
)

liabilities_stackplot = create_stacker_bar(
    macrotrends_data[
        [   
            "Total Current Liabilities",
            "Total Long Term Liabilities",
            "Share Holder Equity"
        ]
    ],
    title_="Total liabilities",
)

tab1, tab2  = st.tabs(["Simplified version", "Full version"])
with tab1:
    st.plotly_chart(assets_stackplot, use_container_width=True)
with tab2:
    st.plotly_chart(assets_full_stackplot, theme="streamlit", use_container_width=True)

tab1, tab2  = st.tabs(["Simplified version", "Full version"])
with tab1:
    st.plotly_chart(liabilities_stackplot, use_container_width=True)
with tab2:
    st.plotly_chart(liabilities_full_stackplot, theme="streamlit", use_container_width=True)

st.warning("Add total Assets/Liabilities plot as in tradingview")

# cash flow statement

asset_liab_plot = create_plot_bar_line(macrotrends_data, 
                                       ["Total Assets", 'Total Liabilities'], 
                                       bar_color=["#1260cc","#febe00"],
                                       title="Assets/Liabilities"
)
st.plotly_chart(asset_liab_plot, use_container_width=True)

debt_cash_plot = create_plot_bar_line(macrotrends_data,
                                      ["Long Term Debt","Cash On Hand"], 
                                      "Debt/Equity Ratio", 
                                      bar_color=["#d0312d","#008631"], # "#EADA52" # 5e1916
                                      title="Cash & Debt"
)
st.plotly_chart(debt_cash_plot, use_container_width=True)

st.warning("Add number of employees from macrotrends")

# financial ratios
returns_plot = create_line_plot(
    macrotrends_data,
    y=[
        "ROE - Return On Equity",
        "ROCE - Return On Capital Employed",
        # "Return On Tangible Equity",
        "ROA - Return On Assets",
        "ROI - Return On Investment",
    ],
    title="Returns",
    perc=False,
)

st.plotly_chart(returns_plot, use_container_width=True)

# https://youtu.be/c7GK02L7AFc
# st.warning("ROCE % measures how well a company generates profits from its capital. \
#         It is calculated as EBIT divided by Capital Employed, where Capital Employed is calculated as Total Assets minus Total Current Liabilities. \
#         Microsoft's annualized ROCE % for the quarter that ended in Dec. 2022 was 30.01%.\
#         https://www.gurufocus.com/term/ROCE/MSFT/ROCE-Percentage/MSFT")

# Book Value Per Share
# bv_ratio_plot = create_line_plot(fin_ratios_df, y=['Book Value Per Share'], title='Book Value Per Share')

pe_ratio_df = get_macrotrends_html(
    f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/pe-ratio"
)
# pe_ratio_plot = create_plot_bar_line(pe_ratio_df, 'TTM Net EPS', 'PE Ratio')

pe_ratio_plot = create_3_subplots(
    df=pe_ratio_df,
    indicators={
        "Stock Price": go.Scatter,
        "TTM Net EPS": go.Bar,
        "PE Ratio": go.Scatter,
    },
    _title="PE Ratio",
)

ps_ratio_df = get_macrotrends_html(
    f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/price-sales"
)
# ps_ratio_plot = create_plot_bar_line(ps_ratio_df, 'TTM Sales per Share', 'Price to Sales Ratio')
ps_ratio_plot = create_3_subplots(
    df=ps_ratio_df,
    indicators={
        "Stock Price": go.Scatter,
        "TTM Sales per Share": go.Bar,
        "Price to Sales Ratio": go.Scatter,
    },
    _title="Price to Sales Ratio",
)

pb_ratio_df = get_macrotrends_html(
    f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/price-book"
)

# pb_ratio_plot = create_plot_bar_line(pb_ratio_df, 'Book Value per Share', 'Price to Book Ratio')

pb_ratio_plot = create_3_subplots(
    df=pb_ratio_df,
    indicators={
        "Stock Price": go.Scatter,
        "Book Value per Share": go.Bar,
        "Price to Book Ratio": go.Scatter,
    },
    _title="Price to Book Ratio",
)

pf_ratio_df = get_macrotrends_html(
    f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[STOCK]}/price-fcf"
)
# pf_ratio_plot = create_plot_bar_line(pf_ratio_df, 'TTM FCF per Share', 'Price to FCF Ratio')

pf_ratio_plot = create_3_subplots(
    df=pf_ratio_df,
    indicators={
        "Stock Price": go.Scatter,
        "TTM FCF per Share": go.Bar,
        "Price to FCF Ratio": go.Scatter,
    },
    _title="Price to FCF Ratio",
)

tab1, tab2, tab3, tab4  = st.tabs(["Price to Earnings", "Price to Sales", "Price to Book", "Price to FCF"])
with tab1:
    st.plotly_chart(pe_ratio_plot, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(ps_ratio_plot, use_container_width=True)
with tab3:
    st.plotly_chart(pb_ratio_plot, use_container_width=True)
with tab4:
    st.plotly_chart(pf_ratio_plot, use_container_width=True)

st.write('## Valuation')

st.warning("get some info from https://www.gurufocus.com/term/gf_score/MSFT/GF-Score/Microsoft")

inflation_df = get_inflation_forecast()

col1, col2 = st.columns(2)
with col1:
    st.write(f"Forecasted inflation is: {inflation_df.loc['OECD - Total', 'inflation']/100:.2%}")
    discount_multiplier = st.select_slider('Discount multiplier, %', options=range(0, 301), value=200)
    margin_of_safety = st.select_slider('Margin of safety, %', options=range(100), value=15)

    # st.write(f"Discount factor will be: {inflation_df.loc['OECD - Total', 'inflation']/100 * discount_multiplier/100:.2%}")

with col2:
    valuations = get_valuations(inflation_df, discount_multiplier=discount_multiplier/100, margin_of_safety=margin_of_safety/100)
    st.table(valuations)

st.warning("add formatting for valuation")

st.write('## Comparison to Sector')

# get_data_from_seeking_alpha(div_estimate_metrics, method='')

seeking_alpha_df = []
for k in seeking_alpha_all_metrics.keys():
    df = create_seeking_alpha_df(k)
    df['field'] = k
    seeking_alpha_df.append(df)

seeking_alpha_df = pd.concat(seeking_alpha_df)

radar_plots = []
for c in radar_categories:
    plot = create_radar_plot(seeking_alpha_df, value="grade", field=c)
    radar_plots.append(plot)

tabs_ = st.tabs(radar_categories)

for i, t in enumerate(tabs_):
    with tabs_[i]:
        st.plotly_chart(radar_plots[i], use_container_width=True)