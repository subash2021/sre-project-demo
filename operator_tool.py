import argparse
import psycopg2
import os
from tabulate import tabulate # A nice library for printing tables

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(
            # We connect to the DB exposed on our host machine's port 5432
            dbname=os.getenv("DB_NAME", "trading_db"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASS", "password"),
            host=os.getenv("DB_HOST_TOOL", "localhost"), # Use localhost to connect from host
            port="5432"
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: Could not connect to the database. Is the stack running? \nDetails: {e}")
        return None

def find_trade_by_id(trade_id):
    """Finds and displays a single trade by its ID."""
    conn = get_db_connection()
    if not conn: return

    with conn.cursor() as cursor:
        cursor.execute("SELECT id, ticker, side, quantity, price, created_at FROM trades WHERE id = %s", (trade_id,))
        trade = cursor.fetchone()
        if trade:
            headers = ["ID", "Ticker", "Side", "Quantity", "Price", "Timestamp"]
            print(tabulate([trade], headers=headers, tablefmt="grid"))
        else:
            print(f"No trade found with ID: {trade_id}")
    conn.close()

def get_recent_failed_trades(limit=10):
    """
    This function demonstrates a more complex operational query.
    We need to find recent failed trades. Since they aren't in the DB,
    we'll simulate this by querying our LOGS.
    (This is a placeholder to show the *kind* of tool you'd build).
    In a real scenario, you might parse log files or query Loki.
    """
    print("\n--- Note: This is a simulated log search ---")
    print("In a real SRE tool, this would query Loki or Grep logs for 'Failed to process'.")
    print(f"Finding last {limit} simulated failed trades...")
    # For now, let's just query the DB for the last few trades as a stand-in
    conn = get_db_connection()
    if not conn: return
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, ticker FROM trades ORDER BY id DESC LIMIT %s", (limit,))
        trades = cursor.fetchall()
        print("Recent successful trades (as a proxy for failed trade investigation):")
        for trade in trades:
            print(f"  - Investigated potential failure around trade ID {trade[0]} for ticker {trade[1]}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Operator tool for the trading system.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command to find a trade
    parser_find = subparsers.add_parser("find_trade", help="Find a trade by its ID")
    parser_find.add_argument("--id", type=int, required=True, help="The ID of the trade to find")

    # Sub-command to investigate failures
    parser_investigate = subparsers.add_parser("investigate_failures", help="Show recent failed trades")
    parser_investigate.add_argument("--limit", type=int, default=5, help="Number of recent failures to show")

    args = parser.parse_args()

    if args.command == "find_trade":
        find_trade_by_id(args.id)
    elif args.command == "investigate_failures":
        get_recent_failed_trades(args.limit)

if __name__ == "__main__":
    # We need to install the 'tabulate' library
    # pip install tabulate
    main()