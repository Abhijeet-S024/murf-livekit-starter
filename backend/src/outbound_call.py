import argparse
import asyncio
import os
import sys
from dotenv import load_dotenv
from livekit import api

# Load environment variables from .env.local
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")
load_dotenv(env_path)

async def main():
    parser = argparse.ArgumentParser(description="Trigger an outbound SIP call using LiveKit.")
    parser.add_argument("--phone", required=True, help="The target phone number to dial (e.g., +1234567890)")
    parser.add_argument("--trunk", required=True, help="The LiveKit SIP Outbound Trunk ID (ST_xxxxxx)")
    parser.add_argument("--room", default="outbound_call_room", help="The LiveKit room name to connect to (default: outbound_call_room)")
    args = parser.parse_args()

    # Retrieve LiveKit credentials from environment
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([url, api_key, api_secret]):
        print("Error: LiveKit credentials (LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET) not found in .env.local")
        sys.exit(1)

    print(f"Connecting to LiveKit API server: {url}")
    lk_api = api.LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret)

    try:
        print(f"Initiating outbound call to {args.phone} using trunk {args.trunk} into room '{args.room}'...")
        participant = await lk_api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id=args.trunk,
                sip_call_to=args.phone,
                room_name=args.room,
                participant_identity=f"sip_{args.phone}",
                participant_name="Outbound Call Participant"
            )
        )
        print("Success! Call initiated successfully.")
        print(f"SIP Participant Details:\n{participant}")
    except Exception as e:
        print(f"Failed to initiate outbound call: {e}")
        sys.exit(1)
    finally:
        await lk_api.aclose()

if __name__ == "__main__":
    asyncio.run(main())
