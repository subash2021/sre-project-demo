# simulator/main.py

import time
import random
import logging
import os
import psycopg2
from prometheus_client import start_http_server, Counter, Histogram

# --- 1. UPDATED Configuration ---
# Create a logs directory if it doesn't exist
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Set up logging to write to a file
log_file_path = os.path.join(LOGS_DIR, 'simulator.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path), # Log to a file
        logging.StreamHandler()             # Also log to the console
    ]
)

# Prometheus metrics
PROCESSED_TRADES_COUNTER = Counter('trades_processed_total', 'Total number of trades processed', ['status']) # status can be 'success' or 'failed'
TRADE_LATENCY_HISTOGRAM = Histogram('trade_processing_duration_seconds', 'Time taken to process a trade')

# --- 2. The Core Simulation Function ---
@TRADE_LATENCY_HISTOGRAM.time() # This decorator automatically measures the execution time of the function
def process_trade(db_conn):
    """
    Simulates processing a single trade.
    It will randomly succeed or fail.
    """

  # --- START OF CHAOS MODE LOGIC ---
    chaos_mode_enabled = os.path.exists('chaos.flag')
    # Normal failure rate is 5%, in chaos mode it's 60%
    failure_rate = 0.60 if chaos_mode_enabled else 0.05
    # --- END OF CHAOS MODE LOGIC ---

    # Simulate generating a trade order
    trade = {
        'ticker': random.choice(['GTSX', 'AAPL', 'GOOG', 'MSFT']),
        'side': random.choice(['BUY', 'SELL']),
        'quantity': random.randint(10, 1000),
        'price': round(random.uniform(50.0, 500.0), 2)
    }
    logging.info(f"Received trade: {trade}")

    

    try:
        # Use the dynamic failure_rate
        if random.random() < failure_rate:
            raise ValueError("CHAOS: Forced connection failure to exchange")

        # --- If successful, write to database ---
        with db_conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trades (ticker, side, quantity, price)
                VALUES (%s, %s, %s, %s)
                """,
                (trade['ticker'], trade['side'], trade['quantity'], trade['price'])
            )
        db_conn.commit()

        # --- Update metrics and logs for SUCCESS ---
        PROCESSED_TRADES_COUNTER.labels(status='success').inc()
        logging.info(f"Successfully processed and stored trade for {trade['ticker']}")

    except Exception as e:
        # --- Update metrics and logs for FAILURE ---
        db_conn.rollback() # Rollback any partial transaction
        PROCESSED_TRADES_COUNTER.labels(status='failed').inc()
        logging.error(f"Failed to process trade for {trade['ticker']}: {e}")

# --- 3. Main Application Loop ---
if __name__ == '__main__':
    logging.info("Starting trade simulator...")

    # Start the Prometheus metrics server on port 8000
    start_http_server(8000)
    logging.info("Prometheus metrics server started on http://localhost:8000")

      # --- UPDATED DATABASE CONNECTION ---
    # Get database connection details from environment variables
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "trading_db")
    db_user = os.getenv("DB_USER", "user")
    db_pass = os.getenv("DB_PASS", "password")

    # Retry connecting to the database
    conn = None
    while conn is None:
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=db_host,
                port="5432"
            )
            logging.info("Database connection established.")
        except psycopg2.OperationalError as e:
            logging.warning(f"Database connection failed, retrying in 5 seconds... Error: {e}")
            time.sleep(5)
    # --- END OF UPDATED SECTION ---

    # The main loop that generates and processes trades
    loop_count = 0
    while True:
        process_trade(conn)
        time.sleep(random.uniform(0.1, 1.5))

        # --- ADD A LOG MESSAGE FOR CHAOS MODE ---
        if loop_count % 20 == 0: # Check for chaos mode every 20 trades
            if os.path.exists('chaos.flag'):
                logging.warning("CHAOS MODE IS ACTIVE. System instability is expected.")
        loop_count += 1