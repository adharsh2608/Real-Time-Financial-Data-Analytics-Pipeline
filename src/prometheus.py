import os
import json
import time
from prometheus_client import start_http_server, Gauge

# Define Prometheus metrics
stock_price_gauge = Gauge(
    "stock_price",
    "Current stock prices for various companies",
    ["stock_name", "price_type"]
)
dataset_dir = "/app/data"  # Directory where stock data files are stored
different_stocks_gauge ={}
for file in os.listdir(dataset_dir):
    different_stocks_gauge[file.replace("_minute.csv", "")] = Gauge(
        f"stock_price_{file.replace('_minute.csv', '').replace('-', '_')}",
        f"Current stock prices for {file.replace('_minute.csv', '')}",
        ["stock_name", "price_type"]
    )


STOCKS_FOLDER = "stocks_consumed"  # Folder where the consumer writes stock files


def process_file(file_path):
    """Process a single stock file and push data to Prometheus."""
    with open(file_path, "r") as f:
        for line in f:
            data = json.loads(line)
            stock_name = data["stock"]

            # Push stock metrics to Prometheus
            stock_price_gauge.labels(stock_name=stock_name, price_type="open").set(data["open"])
            stock_price_gauge.labels(stock_name=stock_name, price_type="high").set(data["high"])
            stock_price_gauge.labels(stock_name=stock_name, price_type="low").set(data["low"])
            stock_price_gauge.labels(stock_name=stock_name, price_type="close").set(data["close"])
            
            # Push stock metrics to Prometheus
            different_stocks_gauge[stock_name].labels(stock_name=stock_name, price_type="open").set(data["open"])
            different_stocks_gauge[stock_name].labels(stock_name=stock_name, price_type="high").set(data["high"])
            different_stocks_gauge[stock_name].labels(stock_name=stock_name, price_type="low").set(data["low"])
            different_stocks_gauge[stock_name].labels(stock_name=stock_name, price_type="close").set(data["close"])

            print(f"Pushed data to Prometheus: {data}")

    # Delete the file after processing
    os.remove(file_path)
    print(f"Deleted processed file: {file_path}")

def push_data_from_files():
    """Read stock data from files and push it to Prometheus."""
    while True:
        files = [f for f in os.listdir(STOCKS_FOLDER) if f.endswith(".json")]
        
        for file_name in files:
            file_path = os.path.join(STOCKS_FOLDER, file_name)
            try:
                process_file(file_path)
            except:
                continue

        time.sleep(5)  # Check for new files every 5 seconds

if __name__ == "__main__":
    # Start Prometheus HTTP server on port 8000
    print("Starting Prometheus metrics server on port 8000...")
    start_http_server(8000)
    
    # Push data to Prometheus
    push_data_from_files()
