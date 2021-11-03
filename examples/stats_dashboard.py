import pathlib

import dff_node_stats

LOCATION = pathlib.Path(__file__).parent.resolve()
stats_file = LOCATION / "stats.csv"
stats = dff_node_stats.Stats(csv_file=stats_file)

stats.streamlit_run()
