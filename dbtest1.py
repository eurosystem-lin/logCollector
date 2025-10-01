from influxdb_client_3 import InfluxDBClient3, Point,flight_client_options
import os, time, json
from dotenv import load_dotenv
import pandas as pd
import certifi

load_dotenv()

# Read required Influx configuration from environment. No defaults allowed.
token = os.getenv("INFLUX_TOKEN")
org = os.getenv("INFLUX_ORG")
host = os.getenv("INFLUX_HOST")

missing = [k for k,v in (("INFLUX_TOKEN",token),("INFLUX_ORG",org),("INFLUX_HOST",host)) if not v]
if missing:
  raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}. Please set them in .env or environment.")

fh = open(certifi.where(), "r") 
cert = fh.read() 
fh.close() 

client = InfluxDBClient3(host=host, token=token, org=org, flight_client_options=flight_client_options(
         tls_root_certs=cert)
)

database="cowrie"

data = {
  "point1": {
    "location": "Klamath",
    "species": "bees",
    "count": 23,
  },
  "point2": {
    "location": "Portland",
    "species": "ants",
    "count": 30,
  },
  "point3": {
    "location": "Klamath",
    "species": "bees",
    "count": 28,
  },
  "point4": {
    "location": "Portland",
    "species": "ants",
    "count": 32,
  },
  "point5": {
    "location": "Klamath",
    "species": "bees",
    "count": 29,
  },
  "point6": {
    "location": "Portland",
    "species": "ants",
    "count": 40,
  },
}




query = """SELECT *
FROM 'census'
WHERE time >= now() - interval '24 hours'
AND ('bees' IS NOT NULL OR 'ants' IS NOT NULL)"""

# Execute the query
table = client.query(query=query, database="cowrie", language='sql',mode='pandas')

print(table)
