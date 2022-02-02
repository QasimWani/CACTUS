import sqlite3
import requests
import pandas as pd

con = sqlite3.connect("data/local.db")
cur = con.cursor()

data = list(cur.execute("SELECT * FROM wifi_capture"))
# create a pandas dataframe object with keys = dnsrr, src, dst and values = data
df = pd.DataFrame(data, columns=["dns", "source_ip", "destination_ip"])
# convert dataframe to json
json_data = df.to_json(orient="records")
response = requests.get('http://localhost:5000/', params=json_data)
print(response.status_code)
