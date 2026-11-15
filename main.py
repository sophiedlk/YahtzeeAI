
"""Competition entry point for the Yahtzee AI agent."""

import json
import sys
import traceback

from expectimax import ExpectimaxAgent
from json_interface import process_request


def main():
    agent = ExpectimaxAgent()

    for line_number, line in enumerate(sys.stdin, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            request = json.loads(line)

            response = process_request(
                request,
                agent,
            )

            output = json.dumps(
                response,
                separators=(",", ":"),
            )

            if len(output.encode("utf-8")) > 65536:
                raise ValueError("Response exceeds 65536 bytes.")

            print(output, flush=True)

        except Exception:
            print(
                f"Error processing input line {line_number}:",
                file=sys.stderr,
            )
            traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
