from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = FastAPI()


def fetch_table_json(url):
    #url = "https://www.skysports.com/football/tables"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
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


@app.get("/premier-league-table")
def premier_league_table():
    table_json = fetch_table_json("https://www.skysports.com/football/tables")
    return {"table": table_json}

@app.get("/NBA-stats")
def NBA_stats():
    table_json = fetch_table_json("https://www.nba.com/standings")
    return {"table": table_json}





