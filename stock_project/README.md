# Investment Dashboard

This project is a one-page investment dashboard created by a beginner data scientist who has a hobby for investing. The dashboard provides a summary and overview of various stocks, technical analysis, qualitative analysis, financial analysis, and valuation and comparison to sector. The developer was inspired by some business intelligence tools and dashboards like Power BI and also used a lot of data engineering and data analytics concepts and practices such as ETL, data cleaning, feature engineering, and data visualization to create this project.

## Features

* Summary and Overview
    * Current dividend yield (forward & TTM), current price, information about company, market capitalization, # in S&P500 (if available), year when it was founded, sector, industry, last ex-dividend date, beta, and badges (dividend king or dividend aristocrat, SCHD holding).
* Technical Analysis
    * Price % historical comparison to SCHD, exponential moving averages, 52-week change, MACD, RSI, Bollinger Bands, Ichimoku Cloud
* Qualitative Analysis
    * Analysts' recommendations from Yahoo, target prices, EPS estimates & dynamics, newest grades for stock by different agencies, last year insider trades
* Financial Analysis
    * Ability to analyze fundamentals YoY or QoQ
    * Plots of different company fundamentals like revenue, EBIT/EBITDA, net income, free cash flow, dividends per share, number of shares outstanding, assets, liabilities, cash/debt, expenses, margins (gross, net profit, FCF, operating margin), returns (ROE, ROCE, ROA, ROI)
    * 3y/5y/10y annualized CAGR for each fundamental
    * Price ratios: P/FCF, P/E, Price/Book, Price/Sales, and median for these ratios to see if stock is relatively expensive compared to historical values
* Valuation & Comparison to Sector
    * A lot of valuation techniques like Lynch valuation, two versions of Graham valuations, DCF model, multiples valuation, and valuation based on dividends. You can set you own margin of safety.
    * Radar plot to compare different metrics to average sector metrics
* Fully interactive plots
    * You can filter them, customize, set dates, range, and sometimes even additional settings
* Table of contents on the left side
    * Interactive, with hyperlinks

## Technologies Used

* Python
* Web scraping from a lot of different sites 
* Working with external public APIs
* Connection to hidden API using Insomnia tool
* Plotly for creating plots
* Streamlit for creating the website

## Usage

To start the website locally, follow these steps:

1. Download the folder from GitHub
2. Run `start.cmd` file
3. Wait for the app to install necessary libraries and run on localhost

Note that the app scrapes different sites/APIs/other sources in real-time and builds plots and does calculations also in real-time. When everything is loaded, it is cached for 1 hour to make it faster next time.

## Future Work

The developer plans to add more features like comparison to peers, news aggregator, some machine learning models (NLTK, Keras LSTM, ARIMA, Facebook Prophet etc.), simulations (e.g. Monte Carlo), price predictions, portfolio analysis, ETF dashboard and other. The developer also plans to deploy the website on AWS Cloud and Heroku someday. For now, it is only available on GitHub because project is constantly in development.

## Acknowledgements

The developer would like to acknowledge the following sources for providing useful information:

* [Stockanalysis](https://stockanalysis.com/)
* [Macrotrends](https://www.macrotrends.net/)
* [Dataroma](https://www.dataroma.com/)
* [Seekingalpha](https://seekingalpha.com/)
* [Alpha Spread](https://www.alphaspread.com/dashboard)
* [YahooFinance](https://finance.yahoo.com/)
* [Alpha Vantage](https://www.alphavantage.co/)
* [TradingView](https://www.tradingview.com/)

Also all the other references (like articles or sites or youtube videos) are given in the code itself as comments.

## Example
![Simple MSFT example](image_2023-03-06_22-34-18.png)

## License

This project is licensed under the MIT License
```
The MIT License (MIT)

Copyright (c) 2023-present Nazar Strypa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.```
