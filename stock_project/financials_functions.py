from libraries_and_vars import *
from seeking_alpha_metrics import *


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
def get_macrotrends_data(url: str):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")

    var_data = ""
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
def create_macrotrends_df(stock=STOCK, period=freq2):
    income_df = (
        get_macrotrends_data(
            f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[stock]}/income-statement?freq={period}"
        )
        * 1e6
    )
    balance = (
        get_macrotrends_data(
            f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[stock]}/balance-sheet?freq={period}"
        )
        * 1e6
    )  # ?freq=A
    fin_ratios_df = get_macrotrends_data(
        f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[stock]}/financial-ratios?freq={period}"
    )
    cash_flow_df = (
        get_macrotrends_data(
            f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[stock]}/cash-flow-statement?freq={period}"
        )
        * 1e6
    )

    df_prices = pd.DataFrame(
        yf.download([stock], start=fin_ratios_df.index.min())["Adj Close"]
    )
    df_prices.columns = ["Price"]
    df_prices["eom"] = [i + relativedelta(day=31) for i in df_prices.index]
    df_prices = df_prices.groupby("eom").last("Price")

    all_data = pd.concat([income_df, balance, cash_flow_df, fin_ratios_df], axis=1)
    all_data.index = pd.to_datetime(all_data.index)

    all_data = pd.concat([all_data, df_prices], axis=1, join="inner")

    # balance long-term assets not included in macrotrends
    all_data["Other Long-Term"] = all_data["Total Long-Term Assets"] - (
        all_data[
            [
                "Property, Plant, And Equipment",
                "Long-Term Investments",
                "Goodwill And Intangible Assets",
                "Other Long-Term Assets",
            ]
        ].sum(axis=1)
    )

    # https://www.investopedia.com/terms/f/freecashflowyield.asp
    # https://youtu.be/OZ0N74Ea0sg?t=567
    all_data["Free Cash Flow"] = (
        all_data["Free Cash Flow Per Share"] * all_data["Shares Outstanding"]
    )
    all_data["Free Cash Flow Yield"] = (
        all_data["Free Cash Flow Per Share"] / all_data["Price"]
    )  # need changes, too small, don't like it. maybe better Price/FCF but inverted

    all_data["CAPEX"] = (
        all_data["Property, Plant, And Equipment"].diff(-1)
        + all_data["Total Depreciation And Amortization - Cash Flow"]
    )
    all_data["CAPEX"] = np.where(all_data["CAPEX"] > 0, all_data["CAPEX"], 0)
    # all_data['SG&A Expenses'] = all_data['SG&A Expenses'] - all_data['CAPEX']

    all_data["Expenses"] = (
        all_data["Cost Of Goods Sold"] + all_data["Operating Expenses"]
    )
    all_data["Revenue/Expenses"] = all_data["Revenue"] / all_data["Expenses"]

    # https://www.gurufocus.com/term/ROCE/MSFT/ROCE-Percentage/MSFT
    all_data["Capital Employed"] = (
        all_data["Total Assets"] - all_data["Total Current Liabilities"]
    )
    all_data["ROCE - Return On Capital Employed"] = (
        all_data["EBIT"] / all_data["Capital Employed"] * 100
    )

    all_data[[c for c in all_data.columns if "Margin" in c]] = (
        all_data[[c for c in all_data.columns if "Margin" in c]] / 100
    )

    if period == "Y":
        n_ = 1
    else:
        n_ = 4

    all_data["Shares Change"] = all_data["Shares Outstanding"].pct_change(-n_)

    return all_data


@st.cache(allow_output_mutation=True)
def create_div_history_df(stock=STOCK):
    """Seeking alpha full dividend history"""

    div_history_df = pd.DataFrame()

    url = f"https://seekingalpha.com/api/v3/symbols/{stock.lower()}/dividend_history"
    querystring = {"years": "100"}
    headers = {
        "cookie": "machine_cookie=4979826528810; _cls_v=072cd8fc-83ec-4b6d-b840-72ce92a351d4; _cls_s=da78f999-6e82-4412-bfd3-98a35379d96d:0; _pxvid=6190f403-0540-11ed-8356-71796f6e5767; pxcts=61910480-0540-11ed-8356-71796f6e5767; g_state=^{^\^i_l^^:0^}; has_paid_subscription=false; OptanonAlertBoxClosed=2022-07-16T19:49:37.138Z; _ga=GA1.2.422884809.1658000977; _igt=80f0662b-29d6-4ba2-daef-f15a084be986; _hjSessionUser_65666=eyJpZCI6IjVmNjA3NTU1LTFmODItNWFhOC05NzBkLTMxNmIwOTFkNDJjZSIsImNyZWF0ZWQiOjE2NTgwNDMwMjQxNTYsImV4aXN0aW5nIjp0cnVlfQ==; _hjCachedUserAttributes=eyJhdHRyaWJ1dGVzIjp7ImxvZ2dlZF9pbiI6dHJ1ZSwibXBfc3ViIjpmYWxzZSwicHJlbWl1bV9zdWIiOmZhbHNlLCJwcm9fc3ViIjpmYWxzZX0sInVzZXJJZCI6IjU2ODczOTA0In0=; ga_clientid=422884809.1658000977; _pcid=^%^7B^%^22browserId^%^22^%^3A^%^22l6l1zvh16ggo2rl5^%^22^%^7D; _clck=1sv21qj^|1^|f4c^|0; _ig=56873904; sailthru_content=2528dc295dc3fbbf1ec8e71fd6af16ea5ed0fab1751712d30b586234ac21ac69c6f48017810681510ac670347a1b237b395addcc8a084ec17e397065464a467803e85c27969d6ca11adf1e5bae9ce43e365ade53ba1716e0f5409199ca81b1b2d336ff2bdab2770099e746360c3b2e4a8f46c8cbd3b263891ad28c66986af90e8a2bb0fb3446957f12521164830063aa9eada221935b05aaed9d45ccc5957509; sailthru_visitor=4a85db3b-194e-42bd-bc87-31076f836304; sailthru_hid=29f91ce2c0119534955a4934eea65d5d62d3164919e4cd8e5507453023d2712d74fca4d95585b51117583622; _gcl_au=1.1.905016176.1671643238; __pat=-18000000; user_id=56873904; user_nick=; user_devices=2; u_voc=; marketplace_author_slugs=; user_cookie_key=cjjdiz; user_perm=; sapu=101; user_remember_token=04b7dcb2602e3f78db1c7c7b3e0e43599aa202f5; _sapi_session_id=0pCP6BL7ckaTjzz1yGfnvj2fYymMCVyRcdc0FilJJuJrLs^%^2BPk6M7pmkTNZq^%^2Bs0tQzLw0Gwxfpuz4XXdeLwjnEvGdwVGKVQdIhiI4kf6GgA6c6Aqo8EAHDVX3JUirUkOfv7^%^2Fv6zuUolHyz^%^2Bka3l7tx2Tmr6LfeaHe0syKkJJ99iSM^%^2FbcPrEEdST3wciFuUBwzxt3V9trL98gAlWdoY4Ces0hsdCU^%^2BEryApHpHc9rt8S2ZjmXsQ7PNxkHufEwIxhqC2LmTKsoVyrOgYz4rWUiq8CGM^%^2BdxILxHnEzl1LN9h2hU^%^3D--^%^2Fq^%^2FbqzYaui40jz7x--I^%^2FfbuLyN7DqYI^%^2BHocBaR9A^%^3D^%^3D; _pctx=^%^7Bu^%^7DN4IgrgzgpgThIC5QFYBsAOA7AZgJwAYAWRUABxigDMBLAD0RBABoQAXAT1KgYDUANEAF9BLSLADKrAIatIDCgHNqEVrCgATZiAjVVASU0IAdmAA2pwUA; _pxhd=9b81b7053d831d0e418b92698dce0fc88c8297e1e67eb88e98fefc26b9d3b6ac:80650f60-6b3b-11e9-814e-41aaaa844f02; ubvt=b26b3487-0e8c-451d-9656-705df157b6a2; session_id=27a89810-0094-4454-8793-f52f76340fbd; OptanonConsent=isIABGlobal=false&datestamp=Thu+Dec+22+2022+16^%^3A05^%^3A26+GMT^%^2B0100+(czas+^%^C5^%^9Brodkowoeuropejski+standardowy)&version=6.30.0&landingPath=NotLandingPage&groups=C0001^%^3A1^%^2CC0002^%^3A1^%^2CC0003^%^3A1^%^2CC0007^%^3A1&hosts=H40^%^3A1^%^2CH17^%^3A1^%^2CH13^%^3A1^%^2CH36^%^3A1^%^2CH55^%^3A1^%^2CH69^%^3A1^%^2CH45^%^3A1^%^2CH14^%^3A1^%^2CH15^%^3A1^%^2CH19^%^3A1^%^2CH47^%^3A1&AwaitingReconsent=false&genVendors=V12^%^3A1^%^2CV5^%^3A1^%^2CV7^%^3A1^%^2CV8^%^3A1^%^2CV13^%^3A1^%^2CV15^%^3A1^%^2CV3^%^3A1^%^2CV2^%^3A1^%^2CV6^%^3A1^%^2CV14^%^3A1^%^2CV1^%^3A1^%^2CV4^%^3A1^%^2CV9^%^3A1^%^2C&geolocation=PL^%^3B14; __pnahc=1; gk_user_access=1**1671790151; gk_user_access_sign=316999477f1cf3b270ec2daee33355ef077c23cf; __tac=; __tae=1671790157992; LAST_VISITED_PAGE=^%^7B^%^22pathname^%^22^%^3A^%^22https^%^3A^%^2F^%^2Fseekingalpha.com^%^2Fsymbol^%^2FDPZ^%^2Fdividends^%^2Fhistory^%^22^%^2C^%^22pageKey^%^22^%^3A^%^22ba85820c-c9a7-4301-91ed-047be2dec0c2^%^22^%^7D; _uetsid=c9555410815311ed8383e1bd89176270; _uetvid=6c9a7a40054011ed9912e34a5318d584; __pvi=eyJpZCI6InYtMjAyMi0xMi0yMy0xMS0wOS0xNC0zMDYtRFVlQXM1NWtGcHdFelhldy05OWVlM2VhYmJkMDU0N2NiMjRiMjQ2ZTU5ZTc4YmQ4OCIsImRvbWFpbiI6Ii5zZWVraW5nYWxwaGEuY29tIiwidGltZSI6MTY3MTc5MDY2ODc4NH0^%^3D; __tbc=^%^7Bkpex^%^7Dc34b4dUSkelinBilgVjlXAFjdExL2yDTVVsaH2tHeWieSgu52a503DdkAZX5En4R; xbc=^%^7Bkpex^%^7DpsZvcg-czvsWNhuvqvMZK8J5UpYhUPaAf31G9LNO4s_JNybiiLibHlVRHn3hm4E4nn-OgFei0KNGMmPkAUA1_w-h83kuroSVs6Wm4u7Ywo2khMWDgt1X4fFsw_eRSpv_RT073ml6wbguc-BKt5xBC3jze6MTqMhOTtHPaQlo8jgrWISTUeJdpSW5wg1k8whSzoS5_JJNFGD12hP_7LIJ9Rcboio5C_pfp4SlYIgOvl0t0F4JUlwH3AItmjnB36P2lQd46Wi4gj8SrJp-WVo44vskLuAbTmezh-9Nmb6v2dAtnefy1d_SnhK1ucoCCPyx9eHnXkzHTxLTKoa4V1CaJBGXBFnLuyNvM48L074T6SRARQTZyVNljtYreNy7Uxb-agK4V0R54vP3iIc0NEPleFizxGh8FZZoF4flQb7mGezf-1HBFpWUlIR7p55GktmivP2SWPpXI1SzKXApvhhYN_mlYAm6eHG7Pq1LZgIR4zWUkv2RKy3rJd9Qsk8cHLPlvjhuRmx_t1ZjQa7IsxW7_03FS_lF67VC3PfVw_sI7vJlVj9ccU7hT9ptOtwx7ECKKYPkv5zP7q_a3Yubi4CmIM5MP-cJhy_-6RU96KhQ-FqXxVYETn_nJbtT3MXgwQma1soxbODUZ0d9NKNDWU5_lu9l2WXp88Vf-PdLt9LNv-Q",
        "authority": "seekingalpha.com",
        "referer": f"https://seekingalpha.com/symbol/{stock}/dividends/history",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    response = requests.request("GET", url, headers=headers, params=querystring).json()[
        "data"
    ]

    for id in response:
        row = pd.DataFrame([id["attributes"]])
        row["Ticker"] = stock
        div_history_df = pd.concat([div_history_df, row], axis=0)

    for c in [c for c in div_history_df.columns if "_date" in c]:
        div_history_df[c] = pd.to_datetime(div_history_df[c])

    div_history_df["amount"] = div_history_df["amount"].astype(float)
    div_history_df = div_history_df.reset_index(drop=True)

    div_history_df["date"] = pd.to_datetime(div_history_df["date"])

    div_history_df["date_adjusted"] = div_history_df["date"].dt.to_period("Q")

    div_history_df = div_history_df.pivot_table(
        index="date_adjusted", columns="freq", values="adjusted_amount", aggfunc="sum"
    )

    div_history_df.columns = div_history_df.columns.str.capitalize()
    
    # getting fiscal year end
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={stock}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    fiscal_month = dt.datetime.strptime(data['FiscalYearEnd'], '%B').month
    
    if fiscal_month % 3 == 0:
        dates = div_history_df.index.astype("datetime64[ns]") + pd.offsets.QuarterEnd(startingMonth=3)
    elif fiscal_month % 3 == 2:
        dates = div_history_df.index.astype("datetime64[ns]") + pd.offsets.QuarterEnd(startingMonth=2)
    elif fiscal_month % 3 == 1:
        dates = div_history_df.index.astype("datetime64[ns]") + pd.offsets.QuarterEnd(startingMonth=1)

    price = yf.download(stock, start=min(dates)).reset_index()

    price = price.groupby(price["Date"].dt.to_period("Q")).apply(lambda x: x.iloc[[-1]])
    price.index = price.index.get_level_values(0)

    final_df = pd.merge(div_history_df, price, left_index=True, right_index=True)
    final_df["Dividend Per Share"] = div_history_df.sum(axis=1)

    final_df.index = dates

    # https://www.angelone.in/calculators/dividend-yield-calculator
    final_df["year"] = final_df.index.year
    final_df["yearly_sum"] = final_df.groupby("year")["Dividend Per Share"].transform("sum")
    final_df["Dividend Yield"] = final_df["yearly_sum"] / final_df["Close"]

    final_df = final_df[list(div_history_df.columns) + ["Dividend Yield", 'Dividend Per Share']]

    return final_df


@st.cache(allow_output_mutation=True)
def create_income_statement(period="quarterly", stock=STOCK):

    income_df = pd.DataFrame()

    t = period[0]

    url1 = f"https://stockanalysis.com/api/symbol/s/{stock.lower()}/financials/is/{t}"
    url2 = f"https://stockanalysis.com/api/symbol/s/{stock.lower()}/financials/bs/{t}"
    url3 = f"https://stockanalysis.com/api/symbol/s/{stock.lower()}/financials/cf/{t}"
    url4 = f"https://stockanalysis.com/api/symbol/s/{stock.lower()}/financials/r/{t}"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    for url in [url1, url2, url3, url4]:
        response = requests.request("GET", url, headers=headers).json()
        data = response["data"]["data"]

        # Determine the length of the longest array
        max_length = max(len(arr) for arr in data.values())
        data_new = {}
        for key, values in data.items():
            padded_array = np.pad(values, (0, max_length - len(values)), "edge")
            data_new[key] = padded_array[:max_length]

        df = pd.DataFrame(data_new)

        income_df = pd.concat([income_df, df], axis=1)

    income_df = income_df.loc[:, ~income_df.columns.duplicated()]

    # this one takes 11 sec., so i've prepared it beforehand, in metrics.py file
    # stockanalysis_tooltips = {}
    # for c in income_df.columns[1:]:
    #     respon = requests.get(url_tooltips+c.lower(), headers=headers).json()
    #     stockanalysis_tooltips[c] = respon['data']['title']

    income_df = income_df.rename(columns=stockanalysis_tooltips)

    income_df = income_df.set_index("Date")

    if "TTM" in income_df.index:
        income_df = income_df.drop("TTM")

    income_df.index = pd.to_datetime(income_df.index)

    income_df = income_df.astype(float).dropna(how="all", axis=1)

    income_df = income_df.rename(columns={"Profit Margin": "Net Profit Margin"})

    # shifting_dict = {"quarterly": -4, "yearly": -1}

    # income_diff = (income_df / income_df.shift(periods=shifting_dict[period])) - 1

    # income_df = pd.merge(
    #     income_df,
    #     income_diff,
    #     left_index=True,
    #     right_index=True,
    #     suffixes=["", " Growth (YoY)"],
    # )

    # income_df = income_df.drop(
    #     [c for c in income_df.columns if "Growth (YoY) Growth (YoY)" in c],
    #     axis=1,
    # )

    # income_df = income_df.loc[:, ~income_df.columns.duplicated()].copy()

    return income_df


@st.cache(allow_output_mutation=True)
def combine_macro_income(macro: pd.DataFrame, income: pd.DataFrame):

    if np.abs((macro.index[0] - income.index[0]).days) < 80:
        # we are setting 'index' from macrotrends_df because it has standard dates, ends of Q
        merged_df = pd.merge(
            macro.reset_index(),
            income.reset_index(),
            how="outer",
            left_index=True,
            right_index=True,
            suffixes=["_m", "_i"],
        ).set_index("index")

    elif macro.index[0] < income.index[0]:
        merged_df = pd.merge(
            macro.reset_index(),
            income.shift().reset_index(),
            how="outer",
            left_index=True,
            right_index=True,
            suffixes=["_m", "_i"],
        ).set_index("index")

    elif macro.index[0] > income.index[0]:
        merged_df = pd.merge(
            macro.shift().reset_index(),
            income.reset_index(),
            how="outer",
            left_index=True,
            right_index=True,
            suffixes=["_m", "_i"],
        ).set_index("index")

    cols = [c for c in merged_df.columns if "_m" in c]
    for col in cols:
        merged_df[col[:-2]] = merged_df[col[:-2] + "_i"].combine_first(
            merged_df[col[:-2] + "_m"].fillna(0)
        )
        merged_df = merged_df.drop([col[:-2] + "_m", col[:-2] + "_i"], axis=1)

    merged_df = merged_df.drop("Date", axis=1)
    merged_df = merged_df[sorted(merged_df.columns.to_list())]

    return merged_df


@st.cache(allow_output_mutation=True)
def create_expenses_df(df: pd.DataFrame):
    # expenses dataframe for plot
    expenses = [
        "Selling & Marketing",
        "General & Administrative",
        "Selling, General & Admin",
        "Research & Development",
        "Other Operating Expenses",
        "Interest Expense",
        "Interest Expense / Income",
        "Other Expense / Income",
    ]
    df_expenses = df.loc[:, [c for c in df.columns if c in expenses]]
    for c in df_expenses.columns:
        if "Expense / Income" in c:
            for i in df_expenses.index:
                if df_expenses.loc[i, c] > 0:
                    df_expenses.loc[i, c] = 0
                else:
                    df_expenses.loc[i, c] = -df_expenses.loc[i, c]
    return df_expenses


@st.cache(allow_output_mutation=True)
def get_annualized_cagr(df: pd.DataFrame, years=0, period="quarterly"):

    df = df[[c for c in df.columns if ("Growth (YoY)" not in c)]]

    if period == "quarterly":
        n = years * 4
    else:
        n = years

    if (n != 0) & (n + 1 < len(df)):
        df = df.iloc[: n + 1].copy()
    else:
        df = df.copy()

    df = df.dropna(axis=0, thresh=5)

    # cagr = stats.gmean(df[c])
    # cagr = df[c].cumprod().iloc[-1]**(1/len(df))-1
    # https://www.linkedin.com/pulse/reply-how-handle-percent-change-cagr-negative-numbers-timo-krall/

    annualized_values = {}
    for c in df.columns:
        begin = df[c][-1]
        final = df[c][0]

        if (begin > 0) & (final > 0):
            CAGR_flexible = (final / begin) ** (1 / years) - 1
        elif (begin < 0) & (final < 0):
            CAGR_flexible = (-1) * ((np.abs(final) / np.abs(begin)) ** (1 / years) - 1)
        elif (begin < 0) & (final > 0):
            CAGR_flexible = ((final + 2 * np.abs(begin)) / np.abs(begin)) ** (
                1 / years
            ) - 1
        elif (begin > 0) & (final < 0):
            CAGR_flexible = (-1) * (
                ((np.abs(final) + 2 * begin) / begin) ** (1 / years) - 1
            )
        else:
            CAGR_flexible = 0

        annualized_values[c] = CAGR_flexible

    cagr = pd.DataFrame([annualized_values]).T
    return cagr
