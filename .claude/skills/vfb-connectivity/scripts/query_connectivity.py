"""Query synaptic connectivity between Drosophila neuron types via VFB."""
import argparse
import sys

import pandas as pd
from vfb_connect.cross_server_tools import VfbConnect


def main():
    parser = argparse.ArgumentParser(
        description="Query neuron connectivity from VirtualFlyBrain"
    )
    parser.add_argument("--upstream", default=None, help="Upstream (presynaptic) neuron type label")
    parser.add_argument("--downstream", default=None, help="Downstream (postsynaptic) neuron type label")
    parser.add_argument("--weight", type=int, default=5, help="Minimum synapse count threshold (default: 5)")
    parser.add_argument("--group-by-class", action="store_true", help="Aggregate results by neuron class")
    parser.add_argument("--exclude-dbs", nargs="*", default=["hb", "fafb"],
                        help="Databases to exclude (default: hb fafb). Pass none with --exclude-dbs")
    args = parser.parse_args()

    if args.upstream is None and args.downstream is None:
        print("ERROR: at least one of --upstream or --downstream must be specified")
        sys.exit(1)

    # Treat empty exclude list from `--exclude-dbs` (no args) as []
    exclude_dbs = args.exclude_dbs if args.exclude_dbs else []

    vfb = VfbConnect()

    df = vfb.get_connected_neurons_by_type(
        weight=args.weight,
        upstream_type=args.upstream,
        downstream_type=args.downstream,
        query_by_label=True,
        group_by_class=args.group_by_class,
        exclude_dbs=exclude_dbs,
        return_dataframe=True,
    )

    if isinstance(df, int):
        print("ERROR: query failed (returned error code). Check neuron type labels.")
        sys.exit(1)
    elif df is None or (hasattr(df, "__len__") and len(df) == 0):
        print("No connections found.")
    else:
        print(f"{len(df)} connections found")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
