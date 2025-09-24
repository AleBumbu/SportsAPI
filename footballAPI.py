from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

app = FastAPI()

API_VERSION = "1.0.3"  # <--- update this every time you change code

@app.get("/ping")
def ping():
    return {"status": "ok", "version": API_VERSION}
    
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



'''def parse_html_table(table):
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

    return pd.DataFrame(rows, columns=headers)'''





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


URL = "https://en.wikipedia.org/wiki/List_of_current_boxing_rankings"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def parse_html_table(table_tag):
    """Parse an HTML table tag into a normalized 2D grid (handles rowspan/colspan)."""
    rows = table_tag.find_all("tr")
    spans = {}   # col_index -> (value, remaining_rows)
    grid = []

    for tr in rows:
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        row = []
        col = 0
        for cell in cells:
            # fill occupied columns by previous rowspans
            while col in spans:
                val, rem = spans[col]
                row.append(val)
                rem -= 1
                if rem <= 0:
                    del spans[col]
                else:
                    spans[col] = (val, rem)
                col += 1

            text = cell.get_text(" ", strip=True)
            try:
                colspan = int(cell.get("colspan", 1))
            except Exception:
                colspan = 1
            try:
                rowspan = int(cell.get("rowspan", 1))
            except Exception:
                rowspan = 1

            for i in range(colspan):
                row.append(text)
                if rowspan > 1:
                    spans[col + i] = (text, rowspan - 1)
            col += colspan

        # fill remaining spans at row end
        while col in spans:
            val, rem = spans[col]
            row.append(val)
            rem -= 1
            if rem <= 0:
                del spans[col]
            else:
                spans[col] = (val, rem)
            col += 1

        grid.append(row)

    if not grid:
        return pd.DataFrame()

    # normalize row lengths
    max_len = max(len(r) for r in grid)
    for r in grid:
        if len(r) < max_len:
            r.extend([""] * (max_len - len(r)))

    header = grid[0]
    data = grid[1:]
    # make header safe / unique
    seen = {}
    new_header = []
    for h in header:
        h = h.strip() or "col"
        if h in seen:
            seen[h] += 1
            new_header.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0
            new_header.append(h)
    df = pd.DataFrame(data, columns=new_header)
    return df

def normalize_columns_and_records(df):
    """
    Map parsed dataframe into expected columns:
    Rank, BoxRec, TBRB, The Ring, WBA, WBC, IBF, WBO
    """
    expected = ["Rank", "BoxRec", "TBRB", "The Ring", "WBA", "WBC", "IBF", "WBO"]
    cols = [c.strip() for c in df.columns.tolist()]
    lc = [c.lower() for c in cols]

    # helper to find column by keyword
    def find_like(keywords):
        for i, name in enumerate(lc):
            for kw in keywords:
                if kw in name:
                    return i
        return None

    indices = {}
    indices["Rank"]     = find_like(["rank"]) or 0
    indices["BoxRec"]   = find_like(["boxrec"]) or 1
    indices["TBRB"]     = find_like(["tbrb"]) or 2
    indices["The Ring"] = find_like(["ring"]) or 3
    indices["WBA"]      = find_like(["wba"])
    indices["WBC"]      = find_like(["wbc"])
    indices["IBF"]      = find_like(["ibf"])
    indices["WBO"]      = find_like(["wbo"])

    # 🔴 FIX: if WBO not found, use any leftover "Unnamed" column
    if indices["WBO"] is None:
        for i, name in enumerate(cols):
            if "unnamed" in name.lower():
                indices["WBO"] = i
                break

    # build records
    records = []
    for _, row in df.iterrows():
        rec = {}
        for col in expected:
            idx = indices.get(col)
            if idx is None or idx >= len(cols):
                rec[col] = ""
            else:
                v = row.iloc[idx]
                rec[col] = "" if pd.isna(v) else str(v).strip()
        records.append(rec)

    return records

def fetch_all_divisions():
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "lxml")

    results = {}
    # select candidate tables (use wikitable and other table tags — adjust if needed)
    tables = soup.find_all("table")
    division_count = 0

    for table in tables:
        # quick header sniff: does table include 'Rank' and 'BoxRec' in any header cell?
        header_cells = table.find_all("th")
        header_texts = [th.get_text(" ", strip=True).lower() for th in header_cells]
        if not any("rank" in t for t in header_texts) or not any("boxrec" in t for t in header_texts):
            continue

        # parse into DataFrame using robust parser
        df = parse_html_table(table)
        if df.empty:
            continue

        # normalize rows/columns
        df = df.replace({np.nan: ""})
        # drop rows that are fully empty
        df = df.loc[~(df == "").all(axis=1)]
        if df.shape[0] == 0:
            continue

        # map header to expected and produce records
        records = normalize_columns_and_records(df)

        # filter-out rows that have no sanctioning-body entries (keep only meaningful rows)
        records = [
            r for r in records
            if any(r.get(k, "").strip() for k in ("BoxRec", "TBRB", "The Ring", "WBA", "WBC", "IBF", "WBO"))
        ]
        if not records:
            continue

        # grab division name from the nearest previous heading (mw-headline inside h3/h4)
        heading = table.find_previous(["h3", "h4"])
        if heading:
            span = heading.find("span", {"class": "mw-headline"})
            division_name = span.get_text(strip=True) if span else heading.get_text(" ", strip=True)
        else:
            division_count += 1
            division_name = f"Division {division_count*100}"

        results[division_name] = records

    return results

@app.get("/boxing-rankings")
def boxing_rankings():
    try:
        data = fetch_all_divisions()
        if not data:
            return {"boxing_rankings": {}}
        return {"boxing_rankings": data}
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





