import os, time, json
from dotenv import load_dotenv
import pandas as pd

# Ensure gRPC can find a root certificate bundle on Windows / other platforms
# Some builds of gRPC look for /usr/share/grpc/roots.pem which doesn't exist on Windows;
# point gRPC to the certifi bundle if available.
try:
  import certifi
  os.environ.setdefault("GRPC_DEFAULT_SSL_ROOTS_FILE_PATH", certifi.where())
except Exception:
  # If certifi isn't available, continue — grpc will attempt its default behavior
  pass

from influxdb_client_3 import InfluxDBClient3, Point

load_dotenv()

# Read required Influx configuration from environment. No defaults allowed.
token = os.getenv("INFLUX_TOKEN")
org = os.getenv("INFLUX_ORG")
host = os.getenv("INFLUX_HOST")

missing = [k for k,v in (("INFLUX_TOKEN",token),("INFLUX_ORG",org),("INFLUX_HOST",host)) if not v]
if missing:
  raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}. Please set them in .env or environment.")

client = InfluxDBClient3(host=host, token=token, org=org)

# Database/bucket to write to
database = "test"

# Path to the test data file (NDJSON: one JSON object per line)
testfile = os.path.join(os.path.dirname(__file__), "test.json")

# Control whether to actually write to Influx (safe default: dry-run)
do_write = os.environ.get("INFLUX_WRITE", "0") == "1"

points = []

if not os.path.exists(testfile):
  print(f"Warning: test file not found: {testfile}. Exiting.")
  raise SystemExit(1)

with open(testfile, "r", encoding="utf-8") as fh:
  for lineno, line in enumerate(fh, start=1):
    line = line.strip()
    if not line:
      continue
    try:
      obj = json.loads(line)
    except json.JSONDecodeError as e:
      print(f"Skipping invalid JSON on line {lineno}: {e}")
      continue

    # Build an Influx Point for each JSON object. Use a fixed measurement name.
    p = Point("cowrie")

    # Keep a small preview of tags/fields so we don't rely on Point internals
    preview_tags = {}
    preview_fields = {}

    # Add common tags if present
    for tag_key in ("eventid", "src_ip", "session", "sensor"):
      if tag_key in obj:
        # convert to string to avoid None issues
        val = str(obj.get(tag_key))
        p = p.tag(tag_key, val)
        preview_tags[tag_key] = val

    # Add some useful fields — store message and a few metadata fields
    if "message" in obj:
      val = str(obj.get("message"))
      p = p.field("message", val)
      preview_fields["message"] = val
    if "duplicate" in obj:
      val = bool(obj.get("duplicate"))
      p = p.field("duplicate", val)
      preview_fields["duplicate"] = val
    # include numeric fields when present
    for num_key in ("size", "duration", "src_port", "dst_port"):
      if num_key in obj:
        try:
          numval = float(obj.get(num_key))
          p = p.field(num_key, numval)
          preview_fields[num_key] = numval
        except Exception:
          # ignore non-numeric values for numeric fields
          pass

    points.append((p, obj, preview_tags, preview_fields))

# If not writing, print a summary of what would be written
if not do_write:
  print(f"Dry-run: constructed {len(points)} points from {testfile}. Set INFLUX_WRITE=1 to actually write to InfluxDB.")
  for i, (pt, src, pt_tags, pt_fields) in enumerate(points[:10], start=1):
    print(f"Point {i}: measurement=cowrie, tags={pt_tags}, fields_preview={list(pt_fields.items())[:3]}")
  if len(points) > 10:
    print("... (truncated)")
else:
  # write points with a small pause between them
  for p, _obj, _tags, _fields in points:
    client.write(database=database, record=p)
    time.sleep(0.2)
  print("Complete. Points written to InfluxDB.")

  # Run a simple query to show recent events count
  query = '''SELECT count("message")
  FROM "cowrie"
  WHERE time > now() - 10m'''

  # Execute the query
  table = client.query(query=query, database=database, language="influxql")

  # Convert to dataframe
  df = table.to_pandas()

  # Robust sorting: Influx results sometimes use '_time' or place the timestamp in the
  # DataFrame index. Try a few common names, then fall back to sorting by index if it's
  # a DatetimeIndex. If none are available, print a helpful message and leave unsorted.
  time_candidates = ["time", "_time", "Time", "timestamp", "_timestamp"]
  time_col = next((c for c in time_candidates if c in df.columns), None)

  if time_col:
    df = df.sort_values(by=time_col)
  elif isinstance(df.index, pd.DatetimeIndex):
    df = df.sort_index()
  else:
    print("Warning: no time-like column found; returning unsorted DataFrame. Columns:", list(df.columns))

  print(df)

