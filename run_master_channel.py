#!/usr/bin/env python3
"""
Master Runner Script
====================
Entry point to run the full melody system.
"""

from melody_structure.master_channel import MasterChannel


def main():
    master = MasterChannel()

    # Example workflow
    input_data = {"phase": "test", "alignment": 0.8}

    # Process
    compressed = master.compress_and_glue(input_data)
    routed = master.route_to_master(compressed)
    final = master.finalize(routed)

    print(final)


if __name__ == "__main__":
    main()
