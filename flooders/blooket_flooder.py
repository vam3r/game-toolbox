"""Authorized Blooket-compatible HTTP load-test client.

The default endpoint is local and no official Blooket API is assumed.  Point
--endpoint at a mock or staging server that you own and have permission to test.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from dataclasses import dataclass

import requests

ANSWER_NAMES = ("Triangle", "Diamond", "Circle", "Square")


def parse_answer_choice(value: str) -> int:
    text = value.strip()
    if text.isdigit():
        choice = int(text)
        if 0 <= choice <= 3:
            return choice
    for index, name in enumerate(ANSWER_NAMES):
        if text.lower() == name.lower():
            return index
    raise argparse.ArgumentTypeError(
        "answer must be one of Triangle, Diamond, Circle, Square or 0-3"
    )


def choose_manual_answer() -> int:
    while True:
        try:
            value = input(
                "Choose an answer (Triangle/Diamond/Circle/Square or 0-3): "
            )
            return parse_answer_choice(value)
        except (EOFError, KeyboardInterrupt):
            raise
        except argparse.ArgumentTypeError as exc:
            print(f"Invalid choice: {exc}")


@dataclass
class Config:
    game_id: str
    count: int
    prefix: str
    endpoint: str
    answer_mode: str
    answer_choice: int
    delay: float
    timeout: float


def run(config: Config) -> None:
    session = requests.Session()
    for number in range(1, config.count + 1):
        name = f"{config.prefix}{number}"
        try:
            response = session.post(
                f"{config.endpoint.rstrip('/')}/join",
                json={"gameId": config.game_id, "name": name},
                timeout=config.timeout,
            )
            response.raise_for_status()
            data = response.json()
            bot_id = data.get("botId") or data.get("id") or name
            print(f"Joined {name} (id={bot_id})")

            if config.answer_mode == "automated":
                choice = random.randint(0, 3)
            else:
                choice = config.answer_choice
            answer_response = session.post(
                f"{config.endpoint.rstrip('/')}/answer",
                json={
                    "gameId": config.game_id,
                    "botId": bot_id,
                    "choice": choice,
                },
                timeout=config.timeout,
            )
            answer_response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Bot {name}: request failed: {exc}", file=sys.stderr)
        except ValueError as exc:
            print(f"Bot {name}: invalid server response: {exc}", file=sys.stderr)
        time.sleep(config.delay)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a bot load test against an authorized Blooket-compatible HTTP server."
    )
    parser.add_argument("--game-id", required=True, help="Authorized game/session identifier")
    parser.add_argument("--count", type=int, default=10, help="Number of bots (1-100)")
    parser.add_argument("--prefix", default="LoadTestBot_", help="Custom username prefix")
    parser.add_argument(
        "--endpoint",
        default="http://127.0.0.1:8080",
        help="HTTP endpoint you control",
    )
    parser.add_argument(
        "--answer-mode", choices=("manual", "automated"), default="manual"
    )
    parser.add_argument("--answer", type=parse_answer_choice)
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--timeout", type=float, default=10)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.count <= 100:
        print("--count must be from 1 to 100", file=sys.stderr)
        return 2
    if args.delay < 0 or args.timeout <= 0:
        print("--delay must be non-negative and --timeout positive", file=sys.stderr)
        return 2

    choice = args.answer
    if args.answer_mode == "manual":
        choice = args.answer if args.answer is not None else choose_manual_answer()

    print("Only use this tool against a server and game you own or are authorized to test.")
    try:
        confirmation = input("Type 'authorized' to continue: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return 130
    if confirmation != "authorized":
        print("Cancelled.", file=sys.stderr)
        return 1

    run(
        Config(
            game_id=args.game_id,
            count=args.count,
            prefix=args.prefix,
            endpoint=args.endpoint,
            answer_mode=args.answer_mode,
            answer_choice=choice if choice is not None else 0,
            delay=args.delay,
            timeout=args.timeout,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
