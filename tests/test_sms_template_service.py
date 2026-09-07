from src.sms_template_service import AssetRequest, publish_asset


class StubClient:
    def __init__(self):
        self.calls = []

    def create_signature(self, name, content):
        self.calls.append(("signature", name, content))
        return {"id": "sig-1"}

    def create_template(self, name, content, signature):
        self.calls.append(("template", name, content, signature))
        return {"id": "tpl-1"}


def test_unapproved_player_asset_stays_in_moderation_queue():
    client = StubClient()
    result = publish_asset(
        AssetRequest(game_id="g-7", name="player-text", content="Join now", signature="Arcade", approved=False),
        client,
    )
    assert result == {"published": False, "reason": "moderation_required", "game_id": "g-7"}
    assert client.calls == []
