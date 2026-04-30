# StockPulsZ

Stock Sentinel Pro is a sleek, desktop-based financial visualization tool that fetches real-time stock data and generates interactive, animated trend charts. It allows you to compare multiple symbols side-by-side with automated technical indicators like Moving Averages.

##  Features
- **Animated Visualizations:** Watch the price action unfold over time with interactive Plotly-powered animations.
- **Multi-Stock Comparison:** Enter multiple tickers (e.g., `AAPL, MSFT, TSLA`) to compare their relative performance.
- **Technical Overlays:** Automatically calculates and displays 14-day Moving Averages to identify trends.
- **Smart Rate Limiting:** Built-in throttling to respect Alpha Vantage free-tier API limits (5 calls/min).
- **Dark Mode UI:** A premium, modern Tkinter interface for a high-end desktop experience.

##  Getting Started

### Prerequisites
- **Python 3.10+**
- **Alpha Vantage API Key:** Get a free key [here](https://www.alphavantage.co/support/#api-key).

### Installation
1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install alpha_vantage pandas plotly
   ```

### Configuration
Open `app.py` and replace the `API_KEY` with your own if you are not using the default provided:
```python
API_KEY = "YOUR_API_KEY_HERE"
```

### Running the App
Run the desktop application directly with Python:
```bash
python app.py
```

##  Built With
- **[Alpha Vantage](https://www.alphavantage.co/):** Real-time financial data API.
- **[Tkinter](https://docs.python.org/3/library/tkinter.html):** Python's built-in GUI library.
- **[Plotly](https://plotly.com/python/):** For high-performance, interactive data visualizations.
- **[Pandas](https://pandas.pydata.org/):** Data manipulation and analysis.

##  How to Use
1. Launch the app using `python app.py`.
2. Enter the stock tickers you want to visualize (comma-separated).
3. Click **Visualize**.
4. Wait for the data fetch to complete (the progress bar will track the 12-second delay between stocks to avoid rate limits).
5. A browser window will automatically open showing your animated `.html` report.


**Result**
https://github.com/zodiac9363/StockPulsZ/blob/main/ezgif-6eaf5a6ff027915b.gif


