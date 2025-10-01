# logCollector

Running dbtest.py
-----------------

The script `dbtest.py` reads `test.json` (NDJSON — one JSON object per line) and constructs InfluxDB Points from each event.

- By default the script runs in dry-run mode and will NOT write to InfluxDB. It prints a summary of the constructed points.
- To actually write to InfluxDB, set the environment variable `INFLUX_WRITE=1` before running the script.

Example (PowerShell):

```powershell
$env:INFLUX_WRITE=1; python .\dbtest.py
```

The script expects `test.json` to be located next to `dbtest.py` in the repository root.

Note about InfluxDB query results and pandas DataFrames
-----------------------------------------------------

When querying InfluxDB using the client in this repo, the resulting table may expose the timestamp
under different column names (for example `_time`, `time`) or as the DataFrame index. The
`dbtest.py` script includes a robust sorting step that looks for common time-like column names and
falls back to sorting by the DataFrame's DatetimeIndex when present. If no time column is found the
script will warn and return the unsorted DataFrame.

If you're writing points intended to be aggregated by field (for example `mean(count)`), store numeric
values under a stable field name like `count` and put categorical labels such as species or location
in tags. `dbtest.py` was updated to write the sample points this way to make queries compatible.

Quick setup
------------

1. Create a virtual environment (optional but recommended):

	python -m venv .venv

2. Activate the virtual environment (Windows PowerShell):

	.\.venv\Scripts\Activate.ps1

3. Install dependencies:

	.venv\Scripts\python.exe -m pip install -r requirements.txt

4. Run the test script:

	.venv\Scripts\python.exe dbtest.py

Notes
-----
- `dbtest.py` uses the InfluxDB v3 client (`influxdb3-python`). If you see "No module named 'influxdb_client_3'", run the install step above.
- The script writes points to your configured InfluxDB instance; update credentials in `dbtest.py` before running against a production database.
 - On some platforms gRPC expects a root certificate file at `/usr/share/grpc/roots.pem` which may not exist on Windows. The script sets
	 the environment variable `GRPC_DEFAULT_SSL_ROOTS_FILE_PATH` to the certifi bundle (if `certifi` is installed). If you see SSL/gRPC errors, install
	 certifi into your venv: `.venv\Scripts\python.exe -m pip install certifi`.
 - Converting query results to a pandas DataFrame requires `pandas`. Install it via requirements or directly: `.venv\Scripts\python.exe -m pip install pandas`.