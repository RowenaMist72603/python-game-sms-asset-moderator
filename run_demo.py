import os
import uuid

from src.sms_template_service import AssetRequest, client_from_env, publish_asset


if __name__ == "__main__":
    destination = os.environ.get("GAME_ID", "arcade-demo")
    request = AssetRequest(
        game_id=destination,
        name="match-ready",
        content="Your match is ready. Open the game to join.",
        signature=f"Arcade Studio {uuid.uuid4().hex[:10]}",
        approved=True,
    )
    print(publish_asset(request, client_from_env()))
