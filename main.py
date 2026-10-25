import os
import sqlite3
import pandas as pd
import requests

def fetch_exchange_rates():
    """EXTRACT: We get up-to-date currency exchange rates to PLN from public API NBP """
    print("Fetching exchange rates...")
    url = "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rates = data[0]["rates"]
        effective_date = data[0]["effectiveDate"]
        return rates, effective_date
    else:
        raise Exception(f"Data fetching error: {response.status_code}")
def process_data(rates, effective_date):
    """TRANSFORM: Cleaning up the data with Pandas. """
    print("Processing and filtrating data...")
    df = pd.DataFrame(rates)

    df = df.rename(
        columns={
            "code": "Currency_Code",
            "currency": "Currency_Name",
            "mid": "Rate_PLN",
        }
    )
    df["Fetch_Date"] = effective_date

    main_currencies = ["EUR","USD","GBP","CHF"]
    df_filtered = df[df["Currency_Code"].isin(main_currencies)].copy()

    return df_filtered

def save_data(df):
    """LOAD: Save results in SQLite and CSV """
    print("Saving data...")

    csv_file = "currency_rates.csv"
    df.to_csv(csv_file, index=False)

    db_file = "data_pipeline.db"
    conn  = sqlite3.connect(db_file)
    df.to_sql("currency_rates", conn, if_exists = "append", index=False)
    conn.close()

    print(f"Data saved in {csv_file} and {db_file}")

if __name__ == "__main__":
    try:
        raw_rates, date_str = fetch_exchange_rates()
        processed_df = process_data(raw_rates, date_str)

        print("Final data table")
        print(processed_df)
        print(" ")

        save_data(processed_df)
    except Exception as e:
        print(f"Process error: {e}")