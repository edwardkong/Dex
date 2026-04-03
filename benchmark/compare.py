"""Compare two benchmark JSON outputs and show differences.

Usage: python benchmark/compare.py before.json after.json
"""

import sys
import json
import argparse


def fmt_pct(before: float, after: float) -> str:
    """Format percentage change."""
    if before == 0:
        return "N/A"
    pct = ((after - before) / before) * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def compare_bench(before: dict, after: dict) -> None:
    """Compare two bench.py outputs."""
    print("\n  PERFORMANCE BENCHMARK COMPARISON")
    print("  " + "=" * 70)

    b_total = before["totals"]
    a_total = after["totals"]

    print(f"\n  {'Metric':<25s} {'Before':>12s} {'After':>12s} {'Change':>10s}")
    print("  " + "-" * 59)
    print(f"  {'Total nodes':<25s} {b_total['total_nodes']:>12,} {a_total['total_nodes']:>12,} "
          f"{fmt_pct(b_total['total_nodes'], a_total['total_nodes']):>10s}")
    print(f"  {'Total time (s)':<25s} {b_total['total_time_s']:>12.2f} {a_total['total_time_s']:>12.2f} "
          f"{fmt_pct(b_total['total_time_s'], a_total['total_time_s']):>10s}")
    print(f"  {'Avg NPS':<25s} {b_total['avg_nps']:>12,} {a_total['avg_nps']:>12,} "
          f"{fmt_pct(b_total['avg_nps'], a_total['avg_nps']):>10s}")

    print(f"\n  {'Position':<30s} {'Nodes Δ':>10s} {'Time Δ':>10s} {'NPS Δ':>10s} {'Move Δ':>8s}")
    print("  " + "-" * 68)

    for b_pos, a_pos in zip(before["positions"], after["positions"]):
        move_changed = " *" if b_pos["best_move"] != a_pos["best_move"] else ""
        print(f"  {b_pos['name']:<30s} "
              f"{fmt_pct(b_pos['nodes'], a_pos['nodes']):>10s} "
              f"{fmt_pct(b_pos['time_s'], a_pos['time_s']):>10s} "
              f"{fmt_pct(b_pos['nps'], a_pos['nps']):>10s} "
              f"{move_changed:>8s}")


def compare_strength(before: dict, after: dict) -> None:
    """Compare two strength.py outputs."""
    print("\n  STRENGTH BENCHMARK COMPARISON")
    print("  " + "=" * 70)

    b_total = before["totals"]
    a_total = after["totals"]

    print(f"\n  {'Metric':<25s} {'Before':>12s} {'After':>12s}")
    print("  " + "-" * 49)
    print(f"  {'Solved':<25s} {b_total['solved']:>12} {a_total['solved']:>12}")
    print(f"  {'Total':<25s} {b_total['total']:>12} {a_total['total']:>12}")
    print(f"  {'Solve rate':<25s} {b_total['solve_rate']:>11.1f}% {a_total['solve_rate']:>11.1f}%")

    print(f"\n  {'Position':<35s} {'Before':>8s} {'After':>8s}")
    print("  " + "-" * 51)

    for b_pos, a_pos in zip(before["positions"], after["positions"]):
        b_status = "PASS" if b_pos["solved"] else "FAIL"
        a_status = "PASS" if a_pos["solved"] else "FAIL"
        changed = " <<" if b_status != a_status else ""
        print(f"  {b_pos['name']:<35s} {b_status:>8s} {a_status:>8s}{changed}")


def main():
    parser = argparse.ArgumentParser(description="Compare benchmark results")
    parser.add_argument("before", help="Before benchmark JSON file")
    parser.add_argument("after", help="After benchmark JSON file")
    args = parser.parse_args()

    with open(args.before) as f:
        before = json.load(f)
    with open(args.after) as f:
        after = json.load(f)

    # Detect type by checking for "positions" with "best_move" (bench) or "solved" (strength)
    if before["positions"] and "best_move" in before["positions"][0]:
        compare_bench(before, after)
    elif before["positions"] and "solved" in before["positions"][0]:
        compare_strength(before, after)
    else:
        print("Unknown benchmark format")
        sys.exit(1)


if __name__ == "__main__":
    main()
