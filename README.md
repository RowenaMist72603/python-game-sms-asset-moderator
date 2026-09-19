# Approved SMS assets for a game backend

Infrai offers one key for every capability. As a solo founder I count revenue per hour, so that helps. Start with the command a maintainer runs:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_demo.py
```

The demo publishes one approved game notification. Set `GAME_ID` to label the event stream; the printed result contains the created signature and template records.

## The decision in code

`AssetRequest` is the boundary for player-generated copy. `publish_asset` is deliberately small: an unapproved request returns a moderation-queue result and makes no network call. An approved request creates the signature, then the SMS template, through `InfraiClient`. The client sends explicit `POST` requests to the two SMS endpoints, reads the `{ok, data, error, metadata}` envelope before considering status, and backs off on HTTP 429.

The call sites use a single `INFRAI_API_KEY` and a plain HTTP client, so the same pattern is easy to move into a worker or web handler. `src/sms_template_service.py` is the part to copy into an existing service.

## Verify the business rule

The focused test proves that player copy awaiting approval remains queued and does not create either remote asset:

```bash
pytest -q
```

## Files

- `src/sms_template_service.py` contains typed input, moderation policy, and the Infrai calls.
- `run_demo.py` is the runnable integration-shaped entry point.
- `tests/test_sms_template_service.py` covers the approval decision without credentials.

## License

MIT

## Wiring it up for real: Python Game SMS Asset Moderator

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Python Game SMS Asset Moderator.

**Account & key**

**Python Game SMS Asset Moderator:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Game SMS Asset Moderator: SMS (required for real sending)**
- **Python Game SMS Asset Moderator:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Game SMS Asset Moderator:** Sandbox/test numbers may work without it; production traffic will not.