import argparse
import json
from typing import Optional
from .service import InventoryService


def main(argv: Optional[list] = None):
    parser = argparse.ArgumentParser(prog="atlas", description="ATLAS Inventory CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add inventory item")
    p_add.add_argument("--sku", required=True)
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--qty", type=int, required=True)
    p_add.add_argument("--loc", required=True)
    p_add.add_argument("--min", type=int, default=0)
    p_add.add_argument("--max", type=int, default=0)

    p_list = sub.add_parser("list", help="List items")
    p_list.add_argument("--category")
    p_list.add_argument("--location")

    p_adj = sub.add_parser("adjust", help="Adjust quantity by delta")
    p_adj.add_argument("--sku", required=True)
    p_adj.add_argument("--delta", type=int, required=True)

    p_move = sub.add_parser("move", help="Move item to a new location")
    p_move.add_argument("--sku", required=True)
    p_move.add_argument("--to", required=True)

    p_rep = sub.add_parser("report", help="Inventory report")
    p_rep.add_argument("--type", choices=["summary", "low", "over"], default="summary")

    args = parser.parse_args(argv)
    svc = InventoryService()

    if args.cmd == "add":
        item = svc.add_item(
            sku=args.sku,
            name=args.name,
            category=args.category,
            quantity=args.qty,
            location=args.loc,
            min_stock=args.min,
            max_stock=args.max,
        )
        print(json.dumps(item.to_dict(), indent=2))
        return

    if args.cmd == "list":
        items = svc.list_items(category=args.category, location=args.location)
        print(json.dumps([i.to_dict() for i in items], indent=2))
        return

    if args.cmd == "adjust":
        item = svc.adjust_quantity(args.sku, args.delta)
        print(json.dumps(item.to_dict(), indent=2))
        return

    if args.cmd == "move":
        item = svc.move_item(args.sku, args.to)
        print(json.dumps(item.to_dict(), indent=2))
        return

    if args.cmd == "report":
        rep = svc.report(args.type)
        print(json.dumps(rep, indent=2))
        return
