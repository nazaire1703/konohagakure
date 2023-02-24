from libraries_and_vars import * 

def highlight_numeric(val):
    if val > 0:
        color = "green"
    elif val < 0:
        color = "red"
    else:
        color = "orange"
    return "color: {}".format(color)


@st.cache(allow_output_mutation=True)
def create_eps_estimate_df(stock=STOCK):
    df = yf.Ticker(stock).earnings_history.iloc[:, 2:]

    df["Earnings Date"] = pd.to_datetime(
        [" ".join(e.split(",")[:-1]) for e in df["Earnings Date"]]
    )

    df["Surprise(%)"] = [
        float(s.replace("+", "")) / 100 if type(s) == str else s
        for s in df["Surprise(%)"]
    ]

    df["EPS Difference"] = df["Reported EPS"] - df["EPS Estimate"]

    df = df.set_index("Earnings Date").dropna(how="all", axis=0).drop_duplicates()

    df["Surprise_abs"] = np.abs(df["Surprise(%)"]).fillna(0)
    return df


@st.cache(allow_output_mutation=True)
def create_eps_estimate_plot(df: pd.DataFrame, size=5, limit=0):
    if limit > 0:
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


def create_recommendation_plot(stock=STOCK):

    recommendation_df = yq.Ticker(stock).recommendation_trend.reset_index(drop=True)
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



@st.cache(allow_output_mutation=True)
def get_target_prices(df: pd.DataFrame, stock=STOCK):
    prices_df = df.loc[
        [
            "currentPrice",
            "targetHighPrice",
            "targetLowPrice",
            "targetMeanPrice",
            "targetMedianPrice",
        ],
        :,
    ]
    prices_df["percentage"] = [
        i / prices_df.loc["currentPrice"].values[0] - 1 for i in prices_df[stock]
    ]

    prices_df = prices_df.drop("currentPrice")

    names = {
        "targetHighPrice": "High",
        "targetLowPrice": "Low",
        "targetMeanPrice": "Mean",
        "targetMedianPrice": "Median",
    }
    cols = ["Target", "Percentage"]

    prices_df.index = prices_df.index.map(names)
    prices_df.columns = cols

    prices_df = (
        prices_df.style.format(formatter="{:.2%}", subset=["Percentage"])
        .format(formatter="{:.2f}", subset=["Target"])
        .applymap(highlight_numeric, subset=["Percentage"])
    )
    return prices_df


@st.cache(allow_output_mutation=True)
def get_yahoo_preds(stock=STOCK):
    ticker = yq.Ticker(stock)
    df_earnings = pd.DataFrame(ticker.earnings_trend[stock]['trend'])

    earnings_dict = {
            "0q": "Current Quarter",
            "+1q": "Next Quarter",
            "0y": "Current Year",
            "+1y": "Next Year",
            "+5y": "Next 5 Years",
            "-5y": "Past 5 Years",
        }
    
    def create_yahoo_df(df_orig:pd.DataFrame, column:str):
        df = pd.DataFrame(df_orig[column].to_list())
        df['period'] = df_orig['period']
        df["period"] = df["period"].map(earnings_dict)
        df = df.set_index("period")
        df = df.iloc[:-2]
        df = df.applymap(lambda x: 0 if isinstance(x, dict) else x).astype(np.float64)
        return df

    earningsEstimate = create_yahoo_df(df_earnings, 'earningsEstimate')
    revenueEstimate = create_yahoo_df(df_earnings, 'revenueEstimate')
    epsTrend = create_yahoo_df(df_earnings, 'epsTrend')
    # epsRevisions = create_yahoo_df(df_earnings, 'epsRevisions')

    earningsEstimate = earningsEstimate.div(earningsEstimate['yearAgoEps'], axis=0)-1
    earningsEstimate = earningsEstimate.drop(columns=['numberOfAnalysts','growth','yearAgoEps'])
    earningsEstimate = earningsEstimate.rename(columns=lambda x: x.capitalize())

    revenueEstimate = revenueEstimate.div(revenueEstimate['yearAgoRevenue'], axis=0)-1
    revenueEstimate = revenueEstimate.drop(columns=['numberOfAnalysts','growth','yearAgoRevenue'])
    revenueEstimate = revenueEstimate.rename(columns=lambda x: x.capitalize())

    # summary_trend = df_earnings[['period','growth']]
    # summary_trend["period"] = summary_trend["period"].map(earnings_dict)
    # summary_trend = summary_trend.set_index("period")
    # summary_trend = summary_trend.rename(columns=lambda x: x.capitalize())

    epsTrend = epsTrend.div(epsTrend['90daysAgo'], axis=0)-1
    epsTrend = epsTrend.drop(columns=['90daysAgo'])
    trend_rename_dict = {'current':'Current', '7daysAgo': '7 days ago', '30daysAgo': '30 days ago', '60daysAgo': '60 days ago'}
    epsTrend = epsTrend.rename(columns=trend_rename_dict)

    return earningsEstimate, revenueEstimate, epsTrend


@st.cache(allow_output_mutation=True)
def get_dataroma_insider_trades(stock=STOCK):

    url = "https://www.dataroma.com/m/ins/ins.php"

    querystring = {"t": "y", "sym": stock, "o": "fd", "d": "d"}

    payload = ""
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )

    html = response.text
    soup = BeautifulSoup(html, "lxml")

    summ = soup.find("table", id="sum")
    dataroma_summary = pd.read_html(str(summ))[0]
    dataroma_summary = dataroma_summary.set_index("Total")
    dataroma_summary["Amount"] = (
        dataroma_summary["Amount"].str.replace("$", "").str.replace(",", "")
    )
    dataroma_summary = dataroma_summary.astype(np.int64)
    dataroma_summary["Amount"] = np.round(dataroma_summary["Amount"] / 1e6, 2)

    grid = soup.find("table", id="grid")
    dataroma_df = pd.read_html(str(grid))[0]
    dataroma_df = dataroma_df.iloc[:5, 3:-1]
    dataroma_df.columns = [
        "Name",
        "Relationship",
        "Date",
        "Transaction",
        "Shares",
        "Price",
        "Amount",
    ]

    dataroma_df["Date"] = pd.to_datetime(dataroma_df["Date"])
    dataroma_df[["Shares", "Amount"]] = dataroma_df[["Shares", "Amount"]].astype(np.int64)
    dataroma_df["Price"] = dataroma_df["Price"].astype(np.float64)
    # dataroma_df.Name = dataroma_df.Name.str.title()

    def transaction_format(val):
        color = "green" if val == "Purchase" else "red"
        return "color: %s" % color

    dataroma_df = dataroma_df[
        ["Date", "Relationship", "Transaction", "Shares", "Price"]
    ]
    dataroma_df = (
        dataroma_df.style.text_gradient(
            subset=["Shares"], cmap=sns.color_palette("light:b", as_cmap=True)
        )
        .applymap(transaction_format, subset=["Transaction"])
        .format({"Date": "{:%Y-%m-%d}", "Price": "{:.2f}"})
    )
    # .set_properties(**{'font-size': '8pt'})

    return dataroma_df, dataroma_summary



@st.cache(allow_output_mutation=True)
def get_last_grades(stock=STOCK, limit=10):
    ticker = yq.Ticker(stock)
    grades = ticker.grading_history.reset_index(drop=True)
    grades["epochGradeDate"] = pd.to_datetime(grades["epochGradeDate"])

    positive_grades = [
        "Buy",
        "Overweight",
        "Outperform",
        "Market Outperform",
        "Positive",
        "Top Pick",
        "Strong Buy",
    ]
    neutral_grades = ["Neutral", "Sector Weight", "Hold"]
    negative_grades = ["Underweight", "Sell", "Negative", "Underperform"]

    def highlight_grades(val):
        if val in positive_grades:
            color = "green"
        elif val in negative_grades:
            color = "red"
        else:
            color = "orange"
        return "color: {}".format(color)

    def highlight_actions(val):
        if val == "up":
            color = "green"
        elif val == "down":
            color = "red"
        else:
            color = "white"
        return "color: {}".format(color)

    grades = grades.set_index("epochGradeDate")
    grades.columns = ["Firm", "To", "From", "Action"]

    grades = (
        grades.iloc[:limit]
        .style.applymap(highlight_grades, subset=["To", "From"])
        .applymap(highlight_actions, subset=["Action"])
    )

    return grades
