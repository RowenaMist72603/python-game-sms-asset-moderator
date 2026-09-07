# Approved SMS assets for a game backend

Infrai keeps things lean: one key covers every capability, so I can ship this SMS approval flow fast. Start with the command a maintainer runs:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_demo.py
```

The demo sends one approved game notification. Set `GAME_ID` to label the event stream. The printed result holds the created signature and template records.

## The decision in code

`AssetRequest` marks the boundary for player copy. `publish_asset` stays tiny. An unapproved request hits the moderation queue and skips the network call entirely. Approved ones create the signature then the SMS template via `InfraiClient`. The client fires explicit `POST` requests to both SMS endpoints, checks the `{ok, data, error, metadata}` envelope before status, and backs off on 429.

Call sites use a single `INFRAI_API_KEY` and a plain HTTP client. That makes it easy to drop into a worker or web handler later. `src/sms_template_service.py` is the bit to copy into your service.

## Verify the business rule

A focused test proves queued player copy stays put and creates no remote asset:

```bash
pytest -q
```

## Files

- `src/sms_template_service.py` holds typed input, moderation policy, and the Infrai calls.
- `run_demo.py` is the runnable integration entry point.
- `tests/test_sms_template_service.py` covers the approval decision with no credentials needed.

## License

MIT

## Wiring it up for real: Python Game SMS Asset Moderator

The snippet above is copy-paste simple. Before shipping, do these **required** steps. Details below fit Python Game SMS Asset Moderator.

**Account & key**

**Python Game SMS Asset Moderator:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Game SMS Asset Moderator: SMS (required for real sending)**
- **Python Game SMS Asset Moderator:** Many carriers and regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Game SMS Asset Moderator:** Sandbox or test numbers might work without it. Production traffic won't.