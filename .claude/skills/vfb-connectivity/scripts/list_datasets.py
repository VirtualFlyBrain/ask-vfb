"""List available connectome datasets from VFB."""
from vfb_connect.cross_server_tools import VfbConnect


def main():
    vfb = VfbConnect()
    results = vfb.nc.commit_list(
        ["MATCH (c:Connectome:Individual) RETURN c.label, c.symbol[0] ORDER BY c.label"]
    )
    print(f"{'Label':<50} Symbol")
    print("-" * 60)
    for r in results:
        for d in r.get("data", []):
            label, symbol = d["row"]
            print(f"{label:<50} {symbol}")


if __name__ == "__main__":
    main()
