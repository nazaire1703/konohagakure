from libraries_and_vars import * 
from seeking_alpha_metrics import *
from financials_functions import *
from qualitative_functions import *
from summary_functions import * 
from plot_functions import *

# https://docs.streamlit.io/library/advanced-features/caching

STOCK = st.text_input(
    "Enter a ticker",
    value="MSFT",
    label_visibility="visible",
    disabled=False,
    placeholder="MSFT",
).upper()

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

# stock_test = st.selectbox("Enter a ticker", ticker_names).upper()
# st.write(stock_test)

yahoo_summary = get_yahoo_summary(stock=STOCK)

open_percentage = (
    yahoo_summary.loc["previousClose"].values[0]
    / yahoo_summary.loc["currentPrice"].values[0]
    - 1
)

current_price = yahoo_summary.loc["currentPrice"].values[0]

col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    st.title(f"{yahoo_summary.loc['longName'].values[0]} ({STOCK})")

with col2:
    if "dividendYield" in yahoo_summary.index:
        st.metric(
            "Dividend yield",
            f"{yahoo_summary.loc['dividendYield'].values[0]:.2%}",
            f"TTM {yahoo_summary.loc['trailingAnnualDividendYield'].values[0]:.2%}",
            delta_color="off",
        )
with col3:
    st.metric("Current price", f"{current_price:.2f}", f"{open_percentage:.2%}")

st.caption(yahoo_summary.loc["longBusinessSummary"].values[0])

country_comment = (
    f"{yahoo_summary.loc['country'].values[0]}"
    if "country" in yahoo_summary.index
    else ""
)

t0 = dt.datetime.today()

sp500 = pd.read_html("https://www.liberatedstocktrader.com/sp-500-companies/")[1]
sp500.columns = sp500.iloc[0]
sp500 = sp500.iloc[1:].reset_index()

sp500_founded = pd.read_html(
    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
)[0]
sp_comment = (
    f"(#{sp500.loc[sp500['Ticker']==STOCK, 'index'].values[0]} in SP500)"
    if STOCK in list(sp500["Ticker"])
    else ""
)

dividend_aristocrats = pd.read_csv(PATH_ARICTOCRAT)
dividend_kings = pd.read_csv(PATH_KING)

day_high = yahoo_summary.loc["dayHigh"].values[0]
day_low = yahoo_summary.loc["dayLow"].values[0]

schd_holdings = get_schd_holdings()

col1, col2 = st.columns(2)

with col1:

    st.slider("Daily change", day_low, day_high, current_price, disabled=True)

    if "marketCap" in yahoo_summary.index:
        st.write(
            f"<font color='#878787'>*Market cap:*</font> \
            {yahoo_summary.loc['marketCap'].values[0]/1e6:,.0f} M {sp_comment}",
            unsafe_allow_html=True,
        )

    if STOCK in list(sp500_founded["Symbol"]):
        st.write(
            f"<font color='#878787'>*Founded:*</font> \
            {sp500_founded.loc[sp500_founded['Symbol']==STOCK, 'Founded'].values[0]} in {country_comment}",
            unsafe_allow_html=True,
        )
    else:
        st.write(
            f"<font color='#878787'>*Founded:*</font> {country_comment}",
            unsafe_allow_html=True,
        )

    st.write(
        f"<font color='#878787'>*Sector:*</font> \
    {yahoo_summary.loc['sector'].values[0]} ({yahoo_summary.loc['industry'].values[0]})",
        unsafe_allow_html=True,
    )

    if "beta" in yahoo_summary.index:
        st.write(
            f"<font color='#878787'>*beta:*</font> \
            {yahoo_summary.loc['beta'].values[0]}",
            unsafe_allow_html=True,
        )

with col2:

    if "payoutRatio" in yahoo_summary.index:
        st.write(
            f"<font color='#878787'>*Payout ratio:*</font> \
            {yahoo_summary.loc['payoutRatio'].values[0]:.2%}",
            unsafe_allow_html=True,
        )

    if "exDividendDate" in yahoo_summary.index:
        st.write(
            f"<font color='#878787'>*ex-Dividend Date:*</font> \
            {pd.to_datetime(yahoo_summary.loc['exDividendDate'].values[0]).strftime('%Y-%m-%d')}",
            unsafe_allow_html=True,
        )

    # https://github.com/tvst/st-annotated-text
    if STOCK in dividend_kings["Ticker"].to_list():
        div_safety = dividend_kings.loc[
            dividend_kings["Ticker"] == STOCK, "Dividend Safety"
        ].values[0]
        annotated_text(("Dividend King", div_safety, "#4cbb17"))

    elif STOCK in dividend_aristocrats["Ticker"].to_list():
        div_safety = dividend_aristocrats.loc[
            dividend_aristocrats["Ticker"] == STOCK, "Dividend Safety"
        ].values[0]
        annotated_text(("Dividend Aristocrat", div_safety, "#000080"))

    if STOCK in schd_holdings.index.to_list():
        schd_percentage = schd_holdings.loc[STOCK, "% of Assets"]  # .values()[0]
        annotated_text(("SCHD", schd_percentage, "#9512a1"))

st.write("## Technical Analysis")

div_include = st.checkbox('Show plots with adjusted prices (dividends included)', value=1)

schd_plot_all = create_schd_plot(STOCK, years_=0, div=div_include)
schd_plot_1y = create_schd_plot(STOCK, years_=1, div=div_include)
schd_plot_5y = create_schd_plot(STOCK, years_=5, div=div_include)

tab1, tab2, tab3 = st.tabs(['All', '5Y', '1Y'])
with tab1:
    st.plotly_chart(schd_plot_all, use_container_width=True)
with tab2:
    st.plotly_chart(schd_plot_5y, use_container_width=True)
with tab3:
    st.plotly_chart(schd_plot_1y, use_container_width=True)
    
d2 = st.date_input(
    "Select initial date",
    (dt.date.today() - dt.timedelta(days=365 * 2)),
    label_visibility="collapsed",
)

plot_52_weeks = create_52w_plot(start_date=d2, stock=STOCK)

ema_plot = create_ema_plot(
    [STOCK], emas=[10, 20, 30, 40, 50], start_date=d2.strftime("%Y-%m-%d")
)

rsi_plot = create_rsi_plot(stock=STOCK)
ichimoku_plot = create_ichimoku_cloud(stock=STOCK)

st.write("## Qualitative Analysis")

mean_ = yq.Ticker(STOCK).financial_data[STOCK]["recommendationMean"]
key_ = yq.Ticker(STOCK).financial_data[STOCK]["recommendationKey"]

col_1, col_2 = st.columns([2, 1])
with col_1:
    recommendation_plot = create_recommendation_plot(stock=STOCK)
with col_2:
    st.metric("Overall recommendation", key_.upper())
    st.slider(
        "Overall recommendation",
        1.0,
        5.0,
        mean_,
        label_visibility="collapsed",
        disabled=True,
        help="1 - Strong Buy, \n2 - Buy, \n3 - Hold, \n4 - Underperform, \n5 - Sell",
    )
    try:
        prices_df = get_target_prices(yahoo_summary, stock=STOCK)
        st.write("**Price forecast**")
        st.table(prices_df)
    except:
        st.info("get_target_prices() was not succeeded")

grades = get_last_grades(stock=STOCK)
st.table(grades)

eps_estimates = create_eps_estimate_df(stock=STOCK)
eps_plot = create_eps_estimate_plot(eps_estimates, limit=5)
st.plotly_chart(eps_plot, use_container_width=True)

earnings_preds, revenue_preds, eps_trend = get_yahoo_preds(stock=STOCK)

earnings_preds = earnings_preds.style.applymap(highlight_numeric).format(formatter="{:.2%}")
revenue_preds = revenue_preds.style.applymap(highlight_numeric).format(formatter="{:.2%}")
eps_trend = eps_trend.style.applymap(highlight_numeric).format(formatter="{:.2%}")

col1, col2 = st.columns(2)
with col1:
    st.write("**Earnings forecast (compared to 1 year ago)**")
    st.table(earnings_preds)
with col2:
    st.write("**Revenue forecast (compared to 1 year ago)**")
    st.table(revenue_preds)

st.write("**EPS forecast (compared to 90 days ago)**")
st.table(eps_trend)

insider_df, insider_summary = get_dataroma_insider_trades(stock=STOCK)

st.write("**Insider trades**")
col1, col2 = st.columns([5, 1])
with col1:
    st.table(insider_df)
with col2:
    st.metric(
        "Buys 1y",
        insider_summary.loc["Buys", "Transactions"],
        f"{insider_summary.loc['Buys', 'Amount']}M",
    )
    st.metric(
        "Sells 1y",
        insider_summary.loc["Sells", "Transactions"],
        f"{insider_summary.loc['Sells', 'Amount']}M",
        delta_color="inverse",
    )

st.write("## Financial Analysis")

if "dividendYield" in yahoo_summary.index:
    div_history_df = create_div_history_df(stock_list=[STOCK])

freq = st.radio(
    "Set frequency",
    ["Quarterly", "Yearly"],
    label_visibility="collapsed",
    horizontal=True,
)
# first letter, Q or Y
freq2 = freq[0]

income_statement = create_income_statement(stock=STOCK, period=freq.lower())
macrotrends_data = create_macrotrends_df(stock=STOCK, period=freq2)

financials = combine_macro_income(macrotrends_data, income_statement)

annualized_data_3y = get_annualized_cagr(financials, 3, period=freq.lower())
annualized_data_5y = get_annualized_cagr(financials, 5, period=freq.lower())
annualized_data_10y = get_annualized_cagr(financials, 10, period=freq.lower())


def print_annualized_data(indicator: str):
    st.metric("3y CAGR", f"{annualized_data_3y.loc[f'{indicator}'][0]:.1%}")
    st.metric("5y CAGR", f"{annualized_data_5y.loc[f'{indicator}'][0]:.1%}")
    st.metric("10y CAGR", f"{annualized_data_10y.loc[f'{indicator}'][0]:.1%}")


revenue_plot = create_plot_bar_line(
    financials,
    ["Revenue", "Expenses"],
    "Revenue/Expenses",
    y2perc=True,
    bar_color=["#805d67", "#0b6596"],
    title="Revenue",
)
income_plot = create_plot_bar_line(
    financials,
    ["Net Income"],
    "Operating Income",
    secondary_y=False,
    bar_color=["#30ba96"],
)
ebitda_plot = create_plot_bar_line(
    financials,
    ["EBIT", "EBITDA"],
    bar_color=["#e68bf0", "#016770"],  # 837bdb
    title="EBITDA",
)
fcf_plot = create_plot_bar_line(
    financials,
    ["Free Cash Flow", "Stock-Based Compensation"],
    'Free Cash Flow Yield',
    y2perc=True,
    bar_color=["#8d8b55", "#6900c4"],
    title="Free Cash Flow",
)
# Free Cash Flow yield: https://youtu.be/OZ0N74Ea0sg?t=567

col1, col2 = st.columns([5, 1])
with col1:
    st.plotly_chart(revenue_plot, use_container_width=True)
with col2:
    print_annualized_data("Revenue")

col1, col2 = st.columns([5, 1])
with col1:
    st.plotly_chart(ebitda_plot, use_container_width=True)
with col2:
    print_annualized_data("EBITDA")

col1, col2 = st.columns([5, 1])
with col1:
    st.plotly_chart(income_plot, use_container_width=True)
with col2:
    print_annualized_data("Net Income")

col1, col2 = st.columns([5, 1])
with col1:
    st.plotly_chart(fcf_plot, use_container_width=True)
with col2:
    print_annualized_data("Free Cash Flow")

with st.expander(
    "**If it's a financial company, don't watch at FCF, rather watch at Price to Book.\
            If it's a REIT, don't watch at FCF either, rather watch at dividend yield growth.**"
):

    st.caption(
        "*'If we cannot estimate net capital expenditures or non-cash working capital, we clearly cannot estimate the free cashflow to equity. \
            Since this is the case with financial service firms, we have three choices. \
            The first is to use dividends as cash flows to equity and assume that firms over time pay out their free cash flows to equity as dividends. \
            Since dividends are observable, we therefore do not have to confront the question of how much firms reinvest. \
            The second is to adapt the free cashflow to equity measure to allow for the types of reinvestment that financial service firms make. \
            For instance, given that banks operate under a regulatory capital ratio constraint, it can be argued that these firms have to increase regulatory capital in order to make more loans in the future. \
            The third is to keep the focus on excess returns, rather than on earnings, dividends and growth rates, and to value these excess returns.'* \
            https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/finfirm09.pdf"
    )

# profit_plot = create_plot_bar_line(
#     income_statement, "Gross Profit", "Operating Expenses", secondary_y=False, bar_color="#7c459c"
# )

shares_plot = create_plot_bar_line(
    financials,
    ["Shares Outstanding"],
    "Shares Change",
    y2perc=True,
    bar_color=["#ea7726"],
)

if "dividendYield" in yahoo_summary.index:
    col1, col2 = st.columns([5, 1])
    with col1:
        dividends_plot = create_plot_bar_line(
            financials,
            ["Dividend Per Share"],
            "Dividend Yield",
            y2perc=True,
            bar_color=["#03c03c"],
        )
        st.plotly_chart(dividends_plot, use_container_width=True)

        # dividends_plot2 = create_plot_bar_line(
        #     div_history_df,
        #     div_history_df.columns,
        #     # "Dividend Yield",
        #     # secondary_y=False,
        #     # bar_color=["#03c03c"],
        # )
        # st.plotly_chart(dividends_plot2, use_container_width=True)

    with col2:
        print_annualized_data("Dividend Per Share")

col1, col2 = st.columns([5, 1])
with col1:
    st.plotly_chart(shares_plot, use_container_width=True)
with col2:
    print_annualized_data("Shares Outstanding (Basic)")

margins_plot = create_line_plot(
    financials,
    y=["Gross Margin", "Operating Margin", "Net Profit Margin", "Free Cash Flow Margin"],
    title="Margins",
)

col1, col2 = st.columns([5, 1])

with col1:
    st.plotly_chart(margins_plot, use_container_width=True)
with col2:
    st.metric(
        "Gross Margin",
        f"{financials['Gross Margin'][0]:.1%}",
        f"{financials['Gross Margin'].median():.1%}",
        delta_color="off",
    )
    st.metric(
        "Operating Margin",
        f"{financials['Operating Margin'][0]:.1%}",
        f"{financials['Operating Margin'].median():.1%}",
        delta_color="off",
    )
    st.metric(
        "Net Profit Margin",
        f"{financials['Net Profit Margin'][0]:.1%}",
        f"{financials['Net Profit Margin'].median():.1%}",
        delta_color="off",
    )
    st.metric(
        "FCF Margin",
        f"{financials['Free Cash Flow Margin'][0]:.1%}",
        f"{financials['Free Cash Flow Margin'].median():.1%}",
        delta_color="off",
    )

# eps_plot = create_plot_bar_line(income_statements, 'EPS (Basic)', 'EPS Growth', y2perc=True, bar_color='#7eb37a')
# dividends_full_history = create_plot_bar_line(div_history_df, 'amount', 'adjusted_amount', title='Full dividend history', bar_color='#03c03c')
# crypto_df = create_ema_plot(CRYPTO_LIST, emas=[10, 20, 30, 40, 50])
# stocks_df = create_ema_plot(STOCKS_LIST, emas=[10, 20, 30, 40, 50])

df_expenses = financials[
    [
        "Cost Of Goods Sold",
        "Research And Development Expenses",
        "SG&A Expenses",
        "Other Operating Income Or Expenses",
    ]
]  # #create_expenses_df(df=income_statement)

expenses_plot = create_stacker_bar(
    df_expenses, title_="Expenses", colors=px.colors.sequential.Turbo_r
)
st.plotly_chart(expenses_plot, use_container_width=True)

assets_full_stackplot = create_stacker_bar(
    financials[
        [  # current
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
            "Other Long-Term",
        ]
    ],
    title_="Total assets",
)

assets_stackplot = create_stacker_bar(
    financials[["Total Current Assets", "Total Long-Term Assets"]],
    title_="Total assets",
)

liabilities_full_stackplot = create_stacker_bar(
    financials[
        [
            "Total Current Liabilities",
            "Long Term Debt",
            "Other Non-Current Liabilities",
            "Common Stock Net",
            "Retained Earnings (Accumulated Deficit)",
            "Comprehensive Income",
            "Other Share Holders Equity",
        ]
    ],
    title_="Total liabilities",
)

liabilities_stackplot = create_stacker_bar(
    financials[
        [
            "Total Current Liabilities",
            "Total Long Term Liabilities",
            "Share Holder Equity",
        ]
    ],
    title_="Total liabilities",
)

tab1, tab2 = st.tabs(["Full version","Simplified version"])
with tab1:
    st.plotly_chart(assets_full_stackplot, use_container_width=True)
with tab2:
    st.plotly_chart(assets_stackplot, use_container_width=True)

tab1, tab2 = st.tabs(["Full version","Simplified version"])
with tab1:
    st.plotly_chart(liabilities_full_stackplot, use_container_width=True)
with tab2:
    st.plotly_chart(liabilities_stackplot, use_container_width=True)

# cash flow statement

asset_liab_plot = create_plot_bar_line(
    financials,
    ["Total Assets", "Total Liabilities"],
    bar_color=["#1260cc", "#febe00"],
    title="Assets/Liabilities",
)
st.plotly_chart(asset_liab_plot, use_container_width=True)

debt_cash_plot = create_plot_bar_line(
    financials,
    ["Long Term Debt", "Cash On Hand"],
    "Debt/Equity Ratio",
    bar_color=["#d0312d", "#008631"],  # "#EADA52" # 5e1916
    title="Cash & Debt",
)
st.plotly_chart(debt_cash_plot, use_container_width=True)

# financial ratios
returns_plot = create_line_plot(
    financials,
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

# https://youtu.be/c7GK02L7AFc
# https://www.gurufocus.com/term/ROCE/MSFT/ROCE-Percentage/MSFT
st.plotly_chart(returns_plot, use_container_width=True)

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

pf_ratio_plot = create_3_subplots(
    df=pf_ratio_df,
    indicators={
        "Stock Price": go.Scatter,
        "TTM FCF per Share": go.Bar,
        "Price to FCF Ratio": go.Scatter,
    },
    _title="Price to FCF Ratio",
)

col1, col2 = st.columns([5, 1])

with col1:
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Price to Earnings", "Price to Sales", "Price to Book", "Price to FCF"]
    )
    with tab1:
        st.plotly_chart(pe_ratio_plot, use_container_width=True)
    with tab2:
        st.plotly_chart(ps_ratio_plot, use_container_width=True)
    with tab3:
        st.plotly_chart(pb_ratio_plot, use_container_width=True)
    with tab4:
        st.plotly_chart(pf_ratio_plot, use_container_width=True)

with col2:
    st.metric(
        "P/E",
        f"{pe_ratio_df['PE Ratio'][-1]:.2f}",
        f"{pe_ratio_df['PE Ratio'].median():.2f}",
        delta_color="off",
    )
    st.metric(
        "P/FCF",
        f"{pf_ratio_df['Price to FCF Ratio'][-1]:.2f}",
        f"{pf_ratio_df['Price to FCF Ratio'].median():.2f}",
        delta_color="off",
    )
    st.metric(
        "P/B",
        f"{pb_ratio_df['Price to Book Ratio'][-1]:.2f}",
        f"{pb_ratio_df['Price to Book Ratio'].median():.2f}",
        delta_color="off",
    )
    st.metric(
        "P/S",
        f"{ps_ratio_df['Price to Sales Ratio'][-1]:.2f}",
        f"{ps_ratio_df['Price to Sales Ratio'].median():.2f}",
        delta_color="off",
    )

st.write("## Valuation")

try:
    inflation_df = get_inflation_forecast()

    col1, col2 = st.columns(2)
    with col1:
        st.write(
            f"Forecasted inflation is: {inflation_df.loc['OECD - Total', 'inflation']/100:.2%}"
        )
        discount_multiplier = st.select_slider(
            "Discount multiplier, %", options=range(0, 301), value=200
        )
        margin_of_safety = st.select_slider(
            "Margin of safety, %", options=range(100), value=15
        )

        # st.write(f"Discount factor will be: {inflation_df.loc['OECD - Total', 'inflation']/100 * discount_multiplier/100:.2%}")

    with col2:
        valuations = get_valuations(
            inflation_df,
            discount_multiplier=discount_multiplier / 100,
            margin_of_safety=margin_of_safety / 100,
            stock=STOCK,
        )
        st.table(valuations)
except:
    st.info("valuation was not succeeded")


st.write("## Comparison to Sector")

try:
    get_data_from_seeking_alpha(
        stock=STOCK, metrics_list=div_estimate_metrics, method=""
    )
except:
    st.info("get_data_from_seeking_alpha() was not succeeded")

try:
    seeking_alpha_df = []
    for k in seeking_alpha_all_metrics.keys():
        df = create_seeking_alpha_df(k)
        df["field"] = k
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
except:
    st.info("create_radar_plot() was not succeeded")


# nasdaq_div_dict = get_nasdaq_div_data()

st.warning(
    """
\n alphavantage.co/documentation/
\n Add historical dividend amount from div_history to financials df
\n add YoY CAGR of Total expenses
\n add formatting for valuation (valuation doesn't work???)
\n add peers from seeking-alpha
\n TSLA other non-current liabilities difference between macrotrends vs stockanalysis. maybe don't use macrotrends? :(
\n Add ETF holding stocks: https://www.etf.com/stock/MSFT
\n Add table of contents: https://discuss.streamlit.io/t/table-of-contents-widget/3470/8
\n calculate CAPEX and show it somewhere https://youtu.be/c7GK02L7AFc?t=1255 formula: https://www.wallstreetmojo.com/capital-expenditure-formula-capex/
\n get some info from https://www.gurufocus.com/term/gf_score/MSFT/GF-Score/Microsoft
\n Add number of employees from macrotrends
\n Change Free Cash Flow yield to Price/FCF inverted, formula: https://www.investopedia.com/terms/f/freecashflowyield.asp")
\n add forecasted ex-div dates? smth like https://www.dividendmax.com/united-states/nyse/tobacco/altria-group-inc/dividends
\n add biggest individual holders?? like Bill Gates, Warren Buffet etc.
\n change radar_plot() to be more pretty, do smth with get_data_from_seeking_alpha()
\n add Bollinger Bands? Ichimoku Clouds? smth like that
\n add selector list at the beginning (selectbox from macrotrends?)
\n add y/y growth to every cash-flow/balance/income
\n add forecasts to plots (ARIMA or smth like that) + forecasts from analytics (seekingalpha.com) + Keras LSTM
\n add portfolio analysis (at least from etoro): sectors + dividend and price forecasting
\n add explanation to different ratios and indicators
\n add ETF analytics - sectors, top holdings (stockanalysis.com), overall position of different firms in portfolio
\n add different stuff based on alphaspread and seekingalpha examples
\n add news aggregator (maybe play a little bit with NLTK for text recognition and classification)
\n add grades from analytics and firms (current and historical, checked using logistic regression??)
\n add Monte Carlo simulation based on historical performance
\n add somewhere ML / Gradient Boosting / Decision Tree / etc. ??
\n add this to Streamlit (Heroku?), in order to do it -> .py. not .ipynb
\n add all of this to AWS (or other Cloud) for data to be updated automatically?
"""
)
