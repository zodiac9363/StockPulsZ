import tkinter as tk
from tkinter import ttk, messagebox
import threading
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import webbrowser
import time
import os

# ---- CONFIG ----
API_KEY = "B9O0WNXL23X7Q4D4"  # replace if needed
REQUEST_DELAY = 12  # seconds between Alpha Vantage calls to respect free-tier rate limit (5/min)

# ---- DATA FETCHING ----
def fetch_stock_data(ticker, ts_client):
    try:
        data, _ = ts_client.get_daily(symbol=ticker, outputsize='compact')
        if data.empty:
            raise ValueError(f"No data for {ticker}")
        # Reverse so oldest first
        data = data.sort_index()
        data['7MA'] = data['4. close'].rolling(window=7).mean()
        data['14MA'] = data['4. close'].rolling(window=14).mean()
        return data
    except Exception as e:
        raise RuntimeError(f"{ticker}: {e}")

def fetch_all(tickers, callback, progress_callback):
    ts_client = TimeSeries(key=API_KEY, output_format='pandas')
    result = {}
    for i, t in enumerate(tickers):
        try:
            data = fetch_stock_data(t, ts_client)
            result[t] = data
        except Exception as e:
            # collect error to show later
            result[t] = {"error": str(e)}
        progress_callback(i + 1, len(tickers))
        if i != len(tickers) - 1:
            time.sleep(REQUEST_DELAY)  # throttle to avoid rate limit
    callback(result)

# ---- PLOTLY ANIMATED CHART ----
def create_animated_plot(data_dict):
    fig = go.Figure()

    # Build frames: incremental reveal for animation
    max_len = max(len(df) for df in data_dict.values() if isinstance(df, pd.DataFrame))
    frames = []

    for frame_idx in range(1, max_len + 1):
        frame_data = []
        for symbol, df in data_dict.items():
            if isinstance(df, dict) and "error" in df:
                continue
            slice_df = df.iloc[:frame_idx]
            frame_data.append(go.Scatter(
                x=slice_df.index,
                y=slice_df['4. close'],
                mode='lines',
                name=f"{symbol} Price",
                line=dict(width=3),
                legendgroup=symbol,
                showlegend=(frame_idx == 1)
            ))
            # moving average (14) as smoother trend
            if '14MA' in slice_df.columns:
                frame_data.append(go.Scatter(
                    x=slice_df.index,
                    y=slice_df['14MA'],
                    mode='lines',
                    name=f"{symbol} 14-day MA",
                    line=dict(width=2, dash='dash'),
                    legendgroup=symbol,
                    showlegend=(frame_idx == 1)
                ))
        frames.append(go.Frame(data=frame_data, name=str(frame_idx)))

    # Initial data (first frame)
    if frames:
        fig.add_traces(frames[0].data)

    fig.update_layout(
        title="Animated Stock Price Trends with Moving Average",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.05,
            x=1.15,
            xanchor="right",
            yanchor="top",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, {"frame": {"duration": 80, "redraw": True},
                                       "fromcurrent": True, "transition": {"duration": 0}}]),
                     dict(label="Pause",
                          method="animate",
                          args=[[None], {"frame": {"duration": 0, "redraw": False},
                                         "mode": "immediate",
                                         "transition": {"duration": 0}}])]
        )]
    )
    fig.frames = frames

    # Write and open
    out_path = os.path.abspath("stock_sentinel_animated.html")
    pio.write_html(fig, file=out_path, auto_open=False, include_plotlyjs='cdn')
    webbrowser.open(f"file://{out_path}")

# ---- GUI ----
class ElegantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stock Sentinel Pro — Animated Trends")
        self.configure(bg="#0f111a")
        self.geometry("650x320")
        self.resizable(False, False)

        # Style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#0f111a", foreground="white", font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("TEntry", fieldbackground="#1f2236", foreground="white", borderwidth=0, padding=6)
        self.style.configure("Accent.TButton", background="#6366f1", foreground="white", font=("Segoe UI", 12, "bold"), padding=8)
        self.style.map("Accent.TButton",
                       background=[("active", "#4f46e5")],
                       relief=[("pressed", "sunken"), ("!pressed", "raised")])

        # Header
        ttk.Label(self, text="Stock Sentinel Pro", style="Header.TLabel").pack(pady=(15, 5))
        ttk.Label(self, text="Compare multiple stocks with animated trend insights", font=("Segoe UI", 10)).pack()

        # Input frame
        frame = tk.Frame(self, bg="#0f111a")
        frame.pack(pady=15, fill="x", padx=30)

        ttk.Label(frame, text="Tickers (comma-separated):").grid(row=0, column=0, sticky="w")
        self.entry = ttk.Entry(frame, width=40, style="TEntry")
        self.entry.grid(row=1, column=0, pady=6, sticky="w")
        self.entry.insert(0, "AAPL, MSFT")

        self.fetch_btn = ttk.Button(frame, text="Visualize", style="Accent.TButton", command=self.on_click)
        self.fetch_btn.grid(row=1, column=1, padx=10)

        # Progress & status
        self.status_label = ttk.Label(self, text="Ready", font=("Segoe UI", 9))
        self.status_label.pack(pady=(5, 2))
        self.progress = ttk.Progressbar(self, mode="determinate", length=500)
        self.progress.pack(pady=(0, 10))

        # Footer
        footer = ttk.Label(self, text="Powered by Alpha Vantage | Animated by Stock Sentinel", font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=5)

    def on_click(self):
        raw = self.entry.get().strip()
        if not raw:
            messagebox.showwarning("Input Required", "Enter at least one ticker symbol.")
            return
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
        self.fetch_btn.state(["disabled"])
        self.status_label.config(text="Fetching data...")
        self.progress["value"] = 0
        threading.Thread(target=self.run_fetch, args=(tickers,), daemon=True).start()

    def run_fetch(self, tickers):
        def progress_callback(done, total):
            percent = int(done / total * 100)
            self.progress["value"] = percent
            self.status_label.config(text=f"Fetching {done}/{total}...")

        def finish_callback(result):
            errors = []
            clean = {}
            for symbol, content in result.items():
                if isinstance(content, dict) and "error" in content:
                    errors.append(f"{symbol}: {content['error']}")
                elif isinstance(content, pd.DataFrame):
                    clean[symbol] = content
            if not clean:
                self.status_label.config(text="Failed to fetch any data.")
                messagebox.showerror("Fetch Error", "All tickers failed to load.\\n" + "\\n".join(errors))
            else:
                self.status_label.config(text="Rendering chart...")
                create_animated_plot(clean)
                self.status_label.config(text="Done.")
            self.fetch_btn.state(["!disabled"])
            self.progress["value"] = 0

        fetch_all(tickers, finish_callback, progress_callback)

if __name__ == "__main__":
    app = ElegantApp()
    app.mainloop()