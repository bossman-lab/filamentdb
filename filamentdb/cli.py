"""
FilamentDB CLI — search, recommend, and compare 3D printing filament settings.
"""
from __future__ import annotations

import argparse
import json
import sys
from tabulate import tabulate

from . import __version__
from .database import (
    search, recommend, compare, list_brands, list_types, get_alternatives
)


def main():
    parser = argparse.ArgumentParser(
        prog="filamentdb",
        description="Open-source 3D printing filament parameter database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  filamentdb search PLA+
      Search for PLA+ filaments from all brands

  filamentdb recommend --brand "Bambu Lab" --model "PLA Basic"
      Get recommended settings for a specific filament

  filamentdb compare "Bambu Lab PLA Basic" "eSun PLA+"
      Compare two filaments side by side

  filamentdb alternatives PETG
      Find PETG alternatives from different brands

  filamentdb list brands
      List all available brands

  filamentdb list types
      List all material types
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # search
    sp = subparsers.add_parser("search", help="Search filaments")
    sp.add_argument("query", type=str, help="Search query (brand, model, or type)")
    sp.add_argument("--limit", type=int, default=10, help="Max results")
    sp.add_argument("--json", action="store_true", help="Output as JSON")

    # recommend
    sp = subparsers.add_parser("recommend", help="Get recommended settings")
    sp.add_argument("--brand", "-b", type=str, help="Brand name")
    sp.add_argument("--model", "-m", type=str, help="Model name")
    sp.add_argument("--type", "-t", type=str, dest="material_type", help="Material type")
    sp.add_argument("--json", action="store_true", help="Output as JSON")

    # compare
    sp = subparsers.add_parser("compare", help="Compare two filaments")
    sp.add_argument("a", type=str, help="First filament (brand model)")
    sp.add_argument("b", type=str, help="Second filament (brand model)")
    sp.add_argument("--json", action="store_true", help="Output as JSON")

    # alternatives
    sp = subparsers.add_parser("alternatives", help="Find alternative filaments")
    sp.add_argument("type", type=str, help="Material type (e.g. PLA, PETG)")
    sp.add_argument("--exclude", type=str, help="Brand to exclude")
    sp.add_argument("--json", action="store_true", help="Output as JSON")

    # list
    sp = subparsers.add_parser("list", help="List brands or types")
    sp.add_argument("what", choices=["brands", "types"], help="What to list")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "search":
            _cmd_search(args)
        elif args.command == "recommend":
            _cmd_recommend(args)
        elif args.command == "compare":
            _cmd_compare(args)
        elif args.command == "alternatives":
            _cmd_alternatives(args)
        elif args.command == "list":
            _cmd_list(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _cmd_search(args):
    results = search(args.query, args.limit)
    if args.json:
        print(json.dumps(results, indent=2))
        return

    if not results:
        print(f"No results for '{args.query}'")
        return

    print(f"\n{'='*55}")
    print(f"  Search results for: {args.query}")
    print(f"{'='*55}")
    for r in results:
        s = r["settings"]
        nt = s.get("nozzle_temp", {}).get("recommended", "?")
        bt = s.get("bed_temp", {}).get("recommended", "?")
        rating = s.get("rating", "?")
        stars = "★" * int(rating) + "☆" * (5 - int(rating)) if isinstance(rating, (int, float)) else ""
        print(f"\n  {r['brand']} {r['model']}")
        print(f"  Type: {r['type']}  |  Nozzle: {nt}°C  |  Bed: {bt}°C  |  {stars}")
        print(f"  → {s.get('notes', '')}")


def _cmd_recommend(args):
    result = recommend(args.brand, args.model, args.material_type)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    if result.get("source") == "not_found":
        print(f"\n❌ {result.get('error', 'Not found')}")
        return

    nt = result.get("nozzle_temp", {})
    bt = result.get("bed_temp", {})
    drying = result.get("drying", {})

    print(f"\n{'='*55}")
    print(f"  Recommended Settings: {result['brand']} {result['model']}")
    print(f"  Source: {result.get('source', 'unknown')}")
    print(f"{'='*55}")
    print(f"\n  🔥 Nozzle temperature:  {nt.get('recommended', '?')}°C  (range: {nt.get('min', '?')}-{nt.get('max', '?')}°C)")
    print(f"  🔥 Bed temperature:     {bt.get('recommended', '?')}°C  (range: {bt.get('min', '?')}-{bt.get('max', '?')}°C)")
    print(f"  ⚡ Max volumetric:      {result.get('max_volumetric_speed', 'N/A')} mm³/s")
    print(f"  ↩  Retraction:          {result.get('retraction_distance', '?')}mm @ {result.get('retraction_speed', '?')}mm/s")
    print(f"  🌬️ Fan speed:           {result.get('fan_speed', '?')}%")
    print(f"  🛏️ Bed adhesion:        {result.get('bed_adhesion', '?')}")
    if drying:
        print(f"  💧 Drying:              {drying.get('temp', '?')}°C for {drying.get('time_hours', '?')}h")
    if result.get("enclosure_required"):
        print(f"  🏠 Enclosure:          REQUIRED")
    if result.get("notes"):
        print(f"\n  💡 {result['notes']}")


def _cmd_compare(args):
    result = compare(args.a, args.b)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    if "error" in result:
        print(f"❌ {result['error']}")
        return

    a = result["a"]
    b = result["b"]
    nt = result["nozzle_temp"]
    bt = result["bed_temp"]
    ret = result["retraction"]
    ratings = result["ratings"]

    print(f"\n{'='*55}")
    print(f"  Filament Comparison")
    print(f"{'='*55}")
    print(f"\n  {'':20} {'A':>15} {'B':>15}")
    print(f"  {'─'*52}")
    print(f"  {'Brand':20} {a['brand']:>15} {b['brand']:>15}")
    print(f"  {'Model':20} {a['model']:>15} {b['model']:>15}")
    print(f"  {'Type':20} {a['type']:>15} {b['type']:>15}")
    print(f"  {'Nozzle °C':20} {str(nt['a_rec'])+'°C':>15} {str(nt['b_rec'])+'°C':>15}")
    print(f"  {'Bed °C':20} {str(bt['a_rec'])+'°C':>15} {str(bt['b_rec'])+'°C':>15}")
    print(f"  {'Retract dist':20} {str(ret['a_dist'])+'mm':>15} {str(ret['b_dist'])+'mm':>15}")
    print(f"  {'Rating':20} {str(ratings['a'])+' ★':>15} {str(ratings['b'])+' ★':>15}")

    if nt.get("difference", 0) > 15:
        print(f"\n  ⚠️  Nozzle temp differs by {nt['difference']}°C — check compatibility!")


def _cmd_alternatives(args):
    results = get_alternatives(args.type, args.exclude)
    if args.json:
        print(json.dumps(results, indent=2))
        return

    if not results:
        print(f"No alternatives found for {args.type}")
        return

    print(f"\n{'='*55}")
    print(f"  Alternatives for {args.type}")
    if args.exclude:
        print(f"  Excluding: {args.exclude}")
    print(f"{'='*55}")
    for r in results:
        rating = r.get("rating", 0)
        stars = "★" * int(rating) + "☆" * (5 - int(rating))
        print(f"\n  {r['brand']} {r['model']}  {stars}")
        print(f"  → {r.get('notes', '')}")


def _cmd_list(args):
    if args.what == "brands":
        brands = list_brands()
        print(f"\n  📦 Available brands ({len(brands)}):")
        for b in brands:
            print(f"     • {b}")
    elif args.what == "types":
        types = list_types()
        print(f"\n  🧪 Available material types ({len(types)}):")
        for t in types:
            print(f"     • {t}")
    print()


if __name__ == "__main__":
    main()
