# game-toolbox

A Python and JavaScript toolbox containing browser helpers and configurable
load-test clients for authorized local or staging environments.

> **Use only in games and servers you own or are explicitly authorized to
> test.** The flooder scripts do not integrate with or bypass Kahoot or
> Blooket production authentication. Their default endpoints are local.

## Requirements

- Python 3.9 or newer
- A modern browser
- Optional mock/staging websocket or HTTP server that you control

## Install

```bash
cd game-toolbox
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Kahoot-compatible websocket load test

Start an authorized websocket mock/staging server on port `8765`, then run:

```bash
python flooders/kahoot_flooder.py \
  --pin TEST123 \
  --count 10 \
  --prefix LoadTestBot_ \
  --endpoint ws://127.0.0.1:8765 \
  --answer-mode manual
```

When prompted, enter `Triangle`, `Diamond`, `Circle`, `Square`, or an index
from `0` through `3`. You can also pass `--answer 2` to avoid the prompt.
Use `--answer-mode random` to choose random answers automatically. The script
accepts at most 100 bots and asks you to type `authorized` before continuing.

## Blooket-compatible HTTP load test

Run it only against an HTTP mock/staging server that you control:

```bash
python flooders/blooket_flooder.py \
  --game-id TEST-GAME \
  --count 10 \
  --prefix LoadTestBot_ \
  --endpoint http://127.0.0.1:8080 \
  --answer-mode manual \
  --answer Square
```

The server must expose `POST /join` and `POST /answer`. `/join` should accept
JSON containing `gameId` and `name` and return a JSON object with `botId`
(or `id`). `/answer` should accept `gameId`, `botId`, and a zero-based `choice`.

Use `--answer-mode automated` for random choices. Valid manual choices are
`Triangle`, `Diamond`, `Circle`, `Square`, or indices `0`-`3`.

## Blooket browser scripts

### Answer highlighter

1. Open the browser developer console on a page or local quiz environment you
   control.
2. Paste the contents of `blooket-hacks/auto-answer.js`.
3. Alternatively, bookmark the script after prefixing its contents with
   `javascript:`.

The script highlights elements when the page supplies `data-correct="true"`,
`aria-correct="true"`, or the `.correct-answer` class. You may also supply
answer text explicitly before loading:

```javascript
window.__GAME_CORRECT_ANSWERS__ = ["One", "Two"];
```

It does not discover or query hidden production answers.

### Local visual modifier

Paste `blooket-hacks/game-modifier.js` into a browser console. It exposes:

```javascript
GameModifier.setScale(1.1);
GameModifier.setContrast(true);
GameModifier.reset();
console.log(GameModifier.getState());
```

Scale values must be between `0.5` and `2`. Changes affect only the current
page's in-memory CSS.

## Tests

```bash
python -m unittest discover -s tests -v
node --check blooket-hacks/auto-answer.js
node --check blooket-hacks/game-modifier.js
```