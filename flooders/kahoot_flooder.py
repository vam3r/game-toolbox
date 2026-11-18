"""Authorized Kahoot-compatible websocket load-test client.

This script targets a websocket URL that you control.  It does not contain or
bypass Kahoot authentication and should only be used with permission.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from dataclasses import dataclass
from typing import Iterable

import websockets


ANSWER_NAMES = ("Triangle", "Diamond", "Circle", "Square")


def parse_answer_choice(value: str) -> int:
    """Convert an answer name or zero-based index into an integer 0-3."""
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
    prompt = "Choose an answer (Triangle/Diamond/Circle/Square or 0-3): "
    while True:
        try:
            return parse_answer_choice(input(prompt))
        except (EOFError, KeyboardInterrupt):
            raise
        except argparse.ArgumentTypeError as exc:
            print(f"Invalid choice: {exc}")


def bot_names(prefix: str, count: int) -> Iterable[str]:
    for number in range(1, count + 1):
        yield f"{prefix}{number}"


@dataclass
class Config:
    pin: str
    count: int
    endpoint: str
    name_prefix: str
    answer_mode: str
    answer_choice: int
    delay: float


async def run_bot(config: Config, name: str) -> None:
    try:
        async with websockets.connect(
            config.endpoint, open_timeout=10, ping_interval=20
        ) as websocket:
            await websocket.send(
                json.dumps({"type": "join", "pin": config.pin, "name": name})
            )
            async for raw_message in websocket:
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    continue
                if message.get("type") != "question":
                    continue
                choice = (
                    config.answer_choice
                    if config.answer_mode == "manual"
                    else random.randint(0, 3)
                )
                await websocket.send(
                    json.dumps(
                        {
                            "type": "answer",
                            "pin": config.pin,
                            "name": name,
                            "choice": choice,
                        }
                    )
                )
    except (OSError, asyncio.TimeoutError) as exc:
        print(f"Bot {name}: connection error: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"Bot {name}: {exc}", file=sys.stderr)


async def run(config: Config) -> None:
    tasks = []
    for name in bot_names(config.name_prefix, config.count):
        tasks.append(asyncio.create_task(run_bot(config, name)))
        await asyncio.sleep(config.delay)
    await asyncio.gather(*tasks, return_exceptions=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a bot load test against an authorized Kahoot-compatible websocket."
    )
    parser.add_argument("--pin", required=True, help="Authorized lobby/pin identifier")
    parser.add_argument("--count", type=int, default=10, help="Number of bots (1-100)")
    parser.add_argument("--prefix", default="LoadTestBot_", help="Custom bot-name prefix")
    parser.add_argument(
        "--endpoint",
        default="ws://127.0.0.1:8765",
        help="Websocket endpoint you control",
    )
    parser.add_argument(
        "--answer-mode", choices=("manual", "random"), default="manual"
    )
    parser.add_argument("--answer", type=parse_answer_choice)
    parser.add_argument("--delay", type=float, default=0.05)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.count <= 100:
        print("--count must be from 1 to 100", file=sys.stderr)
        return 2
    if args.delay < 0:
        print("--delay cannot be negative", file=sys.stderr)
        return 2

    choice = args.answer
    if args.answer_mode == "manual":
        choice = args.answer if args.answer is not None else choose_manual_answer()

    print("Only use this tool against a lobby and endpoint you own or are authorized to test.")
    try:
        confirmation = input("Type 'authorized' to continue: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return 130
    if confirmation != "authorized":
        print("Cancelled.", file=sys.stderr)
        return 1

    config = Config(
        pin=args.pin,
        count=args.count,
        endpoint=args.endpoint,
        name_prefix=args.prefix,
        answer_mode=args.answer_mode,
        answer_choice=choice if choice is not None else 0,
        delay=args.delay,
    )
    asyncio.run(run(config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
