from libraries_and_vars import *

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
    elif len(bar) == 1:
        title_ = bar[0]
    else:
        title_ = ""

    fig.update_layout(
        height=400,
        width=600,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        title=title_,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left"),
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


def create_schd_plot(stock, years_=0, div=True):

    if div:
        col = "Adj Close"
    else:
        col = "Close"

    df_ticker = pd.DataFrame(yf.download(stock)[col])
    df_schd = pd.DataFrame(yf.download("SCHD")[col])
    df = pd.merge(df_ticker, df_schd, left_index=True, right_index=True)
    df.columns = [stock, 'SCHD']

    date_max = df.iloc[-1].name
    if years_ > 0:
        df = df.loc[df.index > date_max + relativedelta(years=-years_),:]

    df = (df / df.iloc[0, :] -1) * 100

    fig = make_subplots(1,1)

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[stock],
            line=dict(color="white"),
            name=stock,
        )
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["SCHD"], line=dict(color="#4066e0"), name="SCHD")
    )

    fig.update_layout(
        height=400,
        width=600,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        title="Stock Price Dynamics",
        template="plotly_dark",
        yaxis_ticksuffix="%",
    )

    return fig


@st.cache(allow_output_mutation=True)
def create_line_plot(df: pd.DataFrame, y: list, title="", perc=True):
    fig = go.Figure()

    for line in y:
        fig.add_scatter(x=df.index, y=df[line], name=line)

    fig.update_layout(
        height=400,
        width=600,
        legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="left"),
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_dark",
        title=title,
    )

    if perc:
        fig.update_layout(yaxis=dict(tickformat=".1%"))

    # fig.show()

    return fig


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


def create_radar_plot(df_orig: pd.DataFrame, field="", value="grade"):
    if field != "":
        df = df_orig.loc[df_orig["field"] == field].copy()
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
    if value == "grade":
        r = r * 7

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


def create_52w_plot(
    start_date=(dt.date.today() - dt.timedelta(days=365 * 2)), stock=STOCK
):

    prices_df = pd.DataFrame(
        yf.download(
            stock,
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
            y=prices_df["rolling_min"],
            x=prices_df.index,
            mode="lines",
            name="Minimum 52w",
        )
    )
    fig.add_trace(
        go.Scatter(
            y=prices_df["rolling_max"],
            x=prices_df.index,
            mode="lines",
            name="Maximum 52w",
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
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="left", title=None
        ),
    )
    # fig.show()
    st.plotly_chart(fig, use_container_width=True)
    return fig