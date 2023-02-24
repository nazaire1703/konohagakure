from libraries_and_vars import * 
from financials_functions import *
from seeking_alpha_metrics import *

@st.cache(allow_output_mutation=True)
def get_schd_holdings():
    url = "https://www.schwabassetmanagement.com/allholdings/SCHD"
    querystring = {"_wrapper_format": "drupal_modal"}

    payload = "js=true&_drupal_ajax=1&ajax_page_state%5Btheme%5D=sch_beacon_csim&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=cog%2Flib%2Ccore%2Fpicturefill%2Centity_embed%2Fcaption%2Ceu_cookie_compliance%2Feu_cookie_compliance_default%2Clazy%2Flazy%2Csch_beacon%2Ffontawesome%2Csch_beacon%2Ffonts%2Csch_beacon%2Fglobal_styles%2Csch_beacon%2Futilib%2Csch_beacon_csim%2Fcsim-accordion%2Csch_beacon_csim%2Fcsim-card-links%2Csch_beacon_csim%2Ffooter_nav%2Csch_beacon_csim%2Fglobal_styles%2Csch_beacon_csim%2Fhighchart-impact-of-expenses%2Csch_beacon_csim%2Fpinned-nav%2Csch_beacon_csim%2Fsegment_selector%2Csch_beacon_csim%2Ftable-enhancements%2Cschwab_charts%2Fhighcharts%2Cschwab_charts%2Fhighcharts_attachments%2Cschwab_charts%2Fhighcharts_plugins%2Cschwab_charts%2Fresponsive_image_charts%2Cschwab_core%2Fvisitor_location%2Cschwab_editor_link%2Fdialog%2Cschwab_editor_link%2Fpopup_link%2Cschwab_funds_product%2Fsfp_tab_container%2Cschwab_gdpr%2Fschwab_gdpr%2Cschwab_images%2Fblazy%2Cschwab_segmentation_redirect%2Fcontent_segment_redirect%2Cschwab_segmentation_splash_page%2Fsplash_page_modal%2Cschwab_share%2Flib%2Cschwab_tealium%2Fabtest.prospect%2Cschwab_tealium%2Ftealium.libraries%2Cschwab_tealium%2Ftealium.variables%2Cschwab_views%2Fschwab_views%2Csystem%2Fbase%2Cviews%2Fviews.module"
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    response = requests.request(
        "POST", url, data=payload, headers=headers, params=querystring
    )
    data = response.json()[2]["data"]
    # json.loads(data)
    holdings = pd.read_html(data)[0]
    return holdings.set_index("Symbol")



@st.cache(allow_output_mutation=True)
def get_yahoo_summary(stock=STOCK):
    ticker = yq.Ticker(stock)
    longName = ticker.price[stock]["longName"]

    summary = pd.DataFrame(ticker.summary_detail)

    # if 'dividendYield' in summary.index:
    #     summary = summary.loc[["dividendYield", "exDividendDate", "trailingAnnualDividendYield", "marketCap","previousClose","payoutRatio"],:] # "beta",
    # else:
    #     summary = summary.loc[["beta", "marketCap","previousClose"],:]

    financials = pd.DataFrame(ticker.financial_data)
    financials = financials.loc[
        [
            "currentPrice",
            "targetHighPrice",
            "targetLowPrice",
            "targetMeanPrice",
            "targetMedianPrice",
        ],
        :,
    ]

    profile = pd.DataFrame(ticker.summary_profile)
    profile = profile.loc[["industry", "sector", "country", "longBusinessSummary"], :]

    df = pd.concat([summary, financials, profile])
    df.loc["longName"] = longName

    return df


@st.cache(allow_output_mutation=True)
def get_employees(stock=STOCK):
    url = f"https://www.macrotrends.net/stocks/charts/{tickers_macrotrends_dict[stock]}/number-of-employees"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    html_table = soup.find("table", {"class": "table"}).prettify()
    df = pd.read_html(html_table)[0]
    df["Date"] = [dt.date(y, 12, 31) for y in df.iloc[:, 0]]
    df = df.iloc[:, 1:].set_index("Date")
    df.columns = ["Number of employees"]
    return df


@st.cache(allow_output_mutation=True)
def get_nasdaq_div_data(stock=STOCK):
    url = f"https://api.nasdaq.com/api/quote/{stock}/dividends"
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
def get_data_from_seeking_alpha(metrics_list: list, method="", stock=STOCK):

    headers = {
        "cookie": "machine_cookie=9717268612629; machine_cookie_ts=1671790378",
        "authority": "seekingalpha.com",
        "referer": f"https://seekingalpha.com/symbol/{stock}/dividends/dividend-growth",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    result = {}

    if method == "grades":
        url = "https://seekingalpha.com/api/v3/ticker_metric_grades"
        querystring = {
            "filter[fields][]": metrics_list,
            "filter[slugs]": f"{stock.lower()}",
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

    elif method == "sector":
        url = f"https://seekingalpha.com/api/v3/symbols/{stock.lower()}/sector_metrics"
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
            "filter[slugs]": f"{stock.lower()}",
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
def create_seeking_alpha_df(field="All"):
    if field == "All":
        metrics_list = []
        for v in seeking_alpha_all_metrics.values():
            for m in v:
                metrics_list.append(m)
    else:
        metrics_list = seeking_alpha_all_metrics[field]

    metrics = get_data_from_seeking_alpha(metrics_list, "metrics")

    averages = {}
    for k in list(metrics.keys()):
        if "_avg_5y" in k:
            averages[k] = metrics[k]
            del metrics[k]
    new_keys = {}

    for k, v in list(averages.items()):
        if "_avg_5y" in k:
            new_keys[k] = k.replace("_avg_5y", "")

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
        [metrics, averages, sector, grades],
        index=["ticker", "avg_5y", "sector", "grade"],
    ).T.dropna()
    seeking_alpha_df["diff_sector"] = (
        seeking_alpha_df["ticker"] / seeking_alpha_df["sector"]
    )
    seeking_alpha_df["diff_avg_5y"] = (
        seeking_alpha_df["ticker"] / seeking_alpha_df["avg_5y"]
    )
    seeking_alpha_df["grade_final"] = seeking_alpha_df["grade"].map(grades_dict)

    return seeking_alpha_df


@st.cache(allow_output_mutation=True)
def get_inflation_forecast():
    url = "https://stats.oecd.org/sdmx-json/data/DP_LIVE/.CPIFORECAST.TOT.AGRWTH.A/OECD"
    querystring = {
        "json-lang": "en",
        "dimensionAtObservation": "allDimensions",
        "startPeriod": "2018",
    }
    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)

    rates = {
        k: v[0] for (k, v) in response.json()["dataSets"][0]["observations"].items()
    }
    df = pd.DataFrame([rates], index=["inflation"]).T

    dimensions = response.json()["structure"]["dimensions"]["observation"][0]["values"]
    dict_c = {i: n["name"] for i, n in enumerate(dimensions)}

    df["country"] = [int(i.split(":")[0]) for i in df.index]
    df["country"] = df["country"].map(dict_c)

    time_periods = response.json()["structure"]["dimensions"]["observation"][5][
        "values"
    ]
    dict_y = {i: int(n["name"]) for i, n in enumerate(time_periods)}

    df["year"] = [int(i.split(":")[-1]) for i in df.index]
    df["year"] = df["year"].map(dict_y)

    df = (
        df.reset_index(drop=True)
        .query(f"year>{dt.date.today().year}")
        .groupby("country")
        .agg("mean")[["inflation"]]
    )

    return df


@st.cache(allow_output_mutation=True)
def get_valuations(
    inflation_df: pd.DataFrame,
    stock=STOCK,
    margin_of_safety=0.15,
    discount_multiplier=2,
):

    income_statement = create_income_statement(period="yearly")

    ticker = yq.Ticker(stock)

    earnings_trend = pd.DataFrame(ticker.earnings_trend[stock]["trend"])[
        ["period", "growth"]
    ].set_index("period")
    eps_pred = earnings_trend.loc["+5y", "growth"]

    summary = pd.DataFrame(ticker.summary_detail)
    div_yield = summary.loc["dividendYield"].values[0]
    pe_ratio = summary.loc["forwardPE"].values[0]

    eps_df = ticker.earning_history.reset_index(drop=True)
    eps = eps_df.loc[eps_df["period"] == "-1q", "epsActual"].values[0]

    price = summary.loc["open"].values[0]

    # get AAA corporate yield
    url = "https://ycharts.com/charts/fund_data.json"
    querystring = {"securities": "id:I:USCAAAEY,include:true,,"}
    payload = ""
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )

    aaa_yield = response.json()["chart_data"][0][0]["last_value"] / 100

    # df = avg forecasted inflation X2, my own idea based on https://www.investopedia.com/terms/d/discountrate.asp
    discount_factor = (
        inflation_df.loc["OECD - Total", "inflation"] / 100 * discount_multiplier
    )

    # Lynch: https://youtu.be/qxFgUGixDxQ
    lynch_valuation = (eps_pred + div_yield) / (pe_ratio / 100) * price

    # Graham: https://youtu.be/8jmjxXc5H8c
    graham_valuation = (
        (eps * (8.5 + 2 * eps_pred)) * 4.4 / aaa_yield
    ) * margin_of_safety
    graham_valuation_v2 = ((eps * (7 + eps_pred)) * 4.4 / aaa_yield) * margin_of_safety

    # DCF model: https://youtu.be/lZzg8lPCY3g
    fcf_avg_growth = np.mean(income_statement.iloc[::-1]["Free Cash Flow"].pct_change())
    last_fcf = income_statement.iloc[0]["Free Cash Flow"]
    balance = ticker.balance_sheet().iloc[-1]
    cash = balance["CashAndCashEquivalents"]
    debt = balance["TotalDebt"]
    shares = income_statement.iloc[0]["Shares Outstanding (Basic)"]

    fcf_forecast = {}
    for i in range(1, 10):
        if i == 1:
            fcf_forecast[i] = last_fcf * (1 + fcf_avg_growth)
        else:
            fcf_forecast[i] = fcf_forecast[i - 1] * (1 + fcf_avg_growth)

    fcf_forecast[10] = fcf_forecast[9] * (1 + aaa_yield) / (discount_factor - aaa_yield)
    pv_forecast = {
        i: (fcf_forecast[i] / (1 + discount_factor) ** i) for i in fcf_forecast.keys()
    }

    sum_pv_fcf = sum(pv_forecast.values())

    dcf_valuation = (sum_pv_fcf + cash - debt) / shares

    valuations = pd.DataFrame(
        {
            "Current price": [price],
            "Lynch valuation": [lynch_valuation],
            "Graham valuation": [graham_valuation],
            "Graham valuation (v2)": [graham_valuation_v2],
            "DCF valuation": [dcf_valuation],
        }
    ).T

    return valuations