#  Equity Index Construction & Backtesting Engine – Detailed Report

---

## 1. Introduction

Modern financial markets rely heavily on indices to track performance, benchmark investments, and construct passive strategies. This project presents the design and implementation of a **custom equity index construction and backtesting engine** that simulates how professional indices are built and evaluated.

The system integrates:
- Data acquisition  
- Stock screening  
- Index construction  
- Portfolio rebalancing  
- Backtesting  
- Risk-performance evaluation  

The goal is to create a **modular and realistic framework** that captures key aspects of real-world index management, including transaction costs, sector constraints, and bias avoidance.

---

## 2. Objectives

The primary objectives of this project are:

- To design a **rule-based index construction framework**
- To implement **systematic stock screening criteria**
- To simulate **portfolio performance over time**
- To compute **risk-adjusted performance metrics**
- To generate **visual analytics for evaluation**
- To ensure **realistic assumptions** (transaction costs, no lookahead bias)

---

## 3. System Architecture

The system follows a pipeline-based architecture:

Universe → Screening → Weighting → Rebalancing → Backtesting → Metrics → Reporting


Each stage is modular and implemented as an independent component.

---

## 4. Data Collection

### 4.1 Data Source

The system uses the `yfinance` API to retrieve:
- Historical price data (adjusted close)
- Fundamental attributes:
  - Market capitalization  
  - Sector and industry  
  - Trading volume  
  - Stock price  

### 4.2 Universe Definition

A predefined list of large-cap U.S. stocks (subset of S&P 500) is used as the initial universe.

---

## 5. Screening Methodology

Stocks are filtered using rule-based criteria:

### 5.1 Filters Applied

- **Market Cap Filter**  
  Ensures only mid/large-cap stocks are included.

- **Liquidity Filter**  
  Based on average daily trading volume.

- **Price Filter**  
  Eliminates low-priced (penny) stocks.

- **Sector Filter**  
  Restricts selection to predefined sectors.

- **REIT Exclusion**  
  Removes real estate investment trusts.

- **ADR Filtering (Optional)**  
  Can exclude foreign listings.

### 5.2 Outcome

The result is a **clean, investable universe** that meets minimum quality standards.

---

## 6. Index Construction

### 6.1 Weighting Schemes

Two methods are supported:

1. **Equal Weighting**
   - Each stock gets equal allocation  
   - Promotes diversification  

2. **Market Cap Weighting**
   - Weights proportional to market capitalization  
   - Reflects market dominance  

---

### 6.2 Sector Cap Constraint

To avoid over-concentration:

- Maximum sector weight is capped (e.g., 30%)
- Excess weight is redistributed iteratively

This is implemented using an **iterative normalization process**, ensuring:
- No sector exceeds the threshold  
- Total weights remain normalized  

---

### 6.3 Constituent Selection

- Stocks are ranked by market cap  
- Top N stocks are selected (configurable)

---

## 7. Rebalancing Strategy

### 7.1 Frequency

- Quarterly (default), configurable

### 7.2 Rebalance Logic

- At each rebalance date:
  - New weights are computed
  - Portfolio is adjusted accordingly

### 7.3 Point-in-Time Safety

The system ensures:
- Only data available before the rebalance date is used  
- Prevents **lookahead bias**

---

## 8. Backtesting Engine

### 8.1 Portfolio Simulation

The backtester simulates daily portfolio value (NAV):

- Uses daily returns of each stock  
- Applies weights dynamically  
- Tracks portfolio value over time  

---

### 8.2 Transaction Cost Model

Transaction costs are modeled using turnover:

Turnover = (|New Weights - Old Weights|).sum() / 2


Cost applied at each rebalance:

Transaction Cost = Turnover × Cost Rate × Portfolio Value


This makes the simulation more realistic.

---

### 8.3 Output

- Daily NAV (Net Asset Value)
- Daily holdings (per stock allocation)

---

## 9. Performance Metrics

The system computes industry-standard metrics:

### 9.1 Return Metrics

- Annualized Return  
- Benchmark Return  

### 9.2 Risk Metrics

- Annualized Volatility  
- Maximum Drawdown  

### 9.3 Risk-Adjusted Metrics

- Sharpe Ratio  
- Sortino Ratio  
- Calmar Ratio  

### 9.4 Relative Performance

- Alpha  
- Beta  
- Tracking Error  
- Information Ratio  

---

## 10. Visualization & Reporting

A comprehensive report is generated with:

### 10.1 Plots

- Cumulative performance vs benchmark  
- Drawdown curve  
- Rolling Sharpe ratio  
- Annual returns comparison

<img width="1743" height="1046" alt="{907B533C-5291-417E-A5BE-3B5C96BCA95B}" src="https://github.com/user-attachments/assets/cf32a42b-1f99-42f7-9f90-d1075ab59e30" />


### 10.2 Summary Table

Displays all computed metrics in a structured format.

<img width="436" height="575" alt="{003B17F5-CE70-45B8-8CA5-B0CF3F58DF77}" src="https://github.com/user-attachments/assets/d49cedce-82e7-4f27-b31c-9db1c3dffe44" />

---

## 11. Key Design Considerations

### 11.1 Avoiding Lookahead Bias

Weights are computed using only past data, ensuring realistic simulation.

---

### 11.2 Realistic Trading Costs

Turnover-based cost modeling reflects actual portfolio rebalancing expenses.

---

### 11.3 Modularity

Each component (screening, weighting, backtesting) is independent, making the system:
- Scalable  
- Easy to extend  

---

### 11.4 Data Limitations

- Uses current fundamentals (not point-in-time historical fundamentals)
- Introduces slight survivorship bias

---

## 12. Limitations

- No intraday trading simulation  
- No slippage modeling  
- Limited to historical backtesting (no live deployment)  
- Fundamental data is not strictly point-in-time  
- Uses a static universe (not dynamically evolving)

---

## 13. Future Enhancements

- Factor-based models (momentum, value, quality)  
- Machine learning-based stock selection  
- Walk-forward optimization  
- Real-time portfolio tracking  
- Integration with alternative data sources  
- Web dashboard (e.g., Streamlit)  

---

## 14. Conclusion

This project successfully demonstrates a **complete pipeline for index construction and backtesting**, incorporating key financial principles and practical constraints.

It highlights:
- Strong understanding of **portfolio management concepts**
- Ability to implement **quantitative finance models**
- Awareness of **real-world challenges** like transaction costs and bias

The system serves as a solid foundation for:
- Quantitative research  
- Portfolio strategy development  
- Financial data science applications  
