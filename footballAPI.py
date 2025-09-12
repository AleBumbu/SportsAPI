from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

app = FastAPI()

def fetch_table_json(url):
    #url = "https://www.skysports.com/football/tables"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "lxml")
    table = soup.find_all("table")
    #table = None
    #for th in soup.find_all("th"):
        #if "Date" in th.get_text():
            #table = th.find_parent("table")
            #break
    df = pd.read_html(str(table))[0]  # convert HTML table to pandas DataFrame
    return df.to_dict(orient="records")

def fetch_table_json_NBA(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    table = soup.find_all('table', {'class': 'Crom_body__UYOcU'})[1]
    #table = None
    #for th in soup.find_all("th"):
        #if "Eastern" in th.get_text():
            #table = th.find_parent("table")
            #break
    df = pd.read_html(str(table))[0]  # convert HTML table to pandas DataFrame
    return df.to_dict(orient="records")

def fetch_boxing_tables(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "lxml")

    # Get ALL tables on the page
    tables = soup.find_all("table")

    results = {}
    for i, table in enumerate(tables):
        try:
            df = pd.read_html(str(table))[0]
            results[f"table_{i+1}"] = df.to_dict(orient="records")
        except ValueError:
            continue  # skip if pandas can't parse

    return results

from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = FastAPI()

def parse_html_table(table):
    """Parse a single <table> into a clean DataFrame."""
    rows = []
    headers = []

    # headers
    for th in table.find("tr").find_all(["th", "td"]):
        headers.append(th.get_text(strip=True))

    # rows
    for tr in table.find_all("tr")[1:]:
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)

    return pd.DataFrame(rows, columns=headers)


from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

app = FastAPI()


def fetch_table_json(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "lxml")
    table = soup.find_all("table")
    df = pd.read_html(str(table))[0]
    df = df.replace({np.nan: ""})
    return df.to_dict(orient="records")



def fetch_boxing_rankings(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")
    tables = soup.find_all("table", {"class": "wikitable"})

    results = {}

    for i, table in enumerate(tables):
        try:
            df = pd.read_html(str(table))[0]

            # Replace NaN with empty strings
            df = df.replace({np.nan: ""})

            # Normalize headers manually
            expected_cols = ["Rank", "BoxRec", "TBRB", "The Ring", "WBA", "WBC", "IBF", "WBO"]
            df_cols = df.columns.tolist()
            if len(df_cols) > len(expected_cols):
                df = df.iloc[:, :len(expected_cols)]
            df.columns = expected_cols

            # Ensure all data is string
            df = df.astype(str)
            df = df.reset_index(drop=True)

            results[f"division_{i+1}"] = df.to_dict(orient="records")
        except Exception as e:
            print(f"Error parsing table {i}: {e}")
            continue

    return results

@app.get("/boxing-rankings")
def boxing_rankings():
    try:
        tables_json = fetch_boxing_rankings("https://en.wikipedia.org/wiki/List_of_current_boxing_rankings")
        if not tables_json:
            return {"boxing_rankings": "No tables found or failed to parse."}
        return {"boxing_rankings": tables_json}
    except Exception as e:
        return {"error": str(e)}
# --- API routes ---
@app.get("/premier-league-table")
def premier_league_table():
    table_json = fetch_table_json("https://www.skysports.com/football/tables")
    return {"table": table_json}

@app.get("/NBA-stats")
def NBA_stats():
    table_json = fetch_table_json("https://www.nba.com/standings")
    return {"table": table_json}






