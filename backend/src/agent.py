import logging
import json
import asyncio

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    tokenize,
    room_io,
    UserInputTranscribedEvent,
    function_tool,
    ConversationItemAddedEvent,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

import os
import sys

# Ensure the current directory is in the Python path for reliable imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompt import SYSTEM_PROMPT
import db


class Assistant(Agent):
    def __init__(self, user_id: str, caller_data: dict = None) -> None:
        instructions = SYSTEM_PROMPT
        if caller_data:
            name = caller_data.get("name", "")
            lang = caller_data.get("language_preference", "")
            facts = caller_data.get("facts", {})
            schemes = facts.get("schemes_checked", "None")
            eligibility = facts.get("eligibility_answers", "None")
            
            instructions += f"\n\nRETURNING CALLER INFO:\n- User ID: {user_id}\n- Name: {name}\n- Language Preference: {lang}\n- Schemes Checked Previously: {schemes}\n- Eligibility Details: {eligibility}\n- Last Interaction: {caller_data.get('last_interaction', '')}\n\nINSTRUCTION: Since this is a returning caller, greet them back warmly by their name ({name}) and refer to the last conversation. For example: 'Namaste {name}, last time we spoke about your schemes/eligibility. How can I help you today?'"
        else:
            instructions += f"\n\nNEW CALLER INFO:\n- User ID: {user_id}\n\nINSTRUCTION: This is a new caller. Greet them using the FIRST-TURN GREETING. Make sure to ask for their name and language preference during the call. Before saving their details, you must ask for their explicit consent."
            
        super().__init__(instructions=instructions)
        self.user_id = user_id

    @function_tool
    def lookup_caller(self, user_id: str) -> str:
        """Use this tool to look up a returning caller's records by their unique User ID or phone number.
        
        Args:
            user_id: The unique identifier or phone number of the caller.
        """
        logger.info(f"Looking up caller for user_id: {user_id}")
        caller = db.get_caller(user_id)
        if caller:
            return json.dumps(caller)
        return "No record found for this User ID."

    @function_tool
    def save_caller(self, user_id: str, name: str, language_preference: str, schemes_checked: str, eligibility_answers: str) -> str:
        """Use this tool to save or update the caller's details and learned facts.
        IMPORTANT: You must ask the user for consent ('Is it okay if I save this information to remember you next time?') before calling this tool. If they say no, do NOT call this tool.
        DO NOT store sensitive bank account numbers, PINs, OTPs, or government ID numbers.
        
        Args:
            user_id: The unique identifier or phone number of the caller.
            name: The caller's name.
            language_preference: The caller's preferred language (e.g. Hindi, Hinglish, English).
            schemes_checked: The government or banking schemes they have asked about or checked.
            eligibility_answers: Any eligibility-related answers discussed during the call.
        """
        logger.info(f"Saving caller data for user_id: {user_id}")
        facts = {
            "schemes_checked": schemes_checked,
            "eligibility_answers": eligibility_answers
        }
        db.save_caller(user_id, name, language_preference, facts)
        return "Caller information saved successfully."

    @function_tool
    def check_scheme_eligibility_and_checklist(self, scheme_name: str, age: int, gender: str = None) -> str:
        """Use this tool to check the eligibility of the caller for a specific government/financial scheme and retrieve the required document checklist.
        
        Args:
            scheme_name: The name of the scheme (e.g., 'Atal Pension Yojana', 'PM Jan Dhan Yojana', 'PM Jeevan Jyoti Bima Yojana', 'PM Suraksha Bima Yojana', 'Sukanya Samriddhi Yojana', 'Mudra Loan').
            age: The age of the applicant (in years).
            gender: The gender of the applicant ('male', 'female', 'other').
        """
        logger.info(f"Checking eligibility for scheme: {scheme_name}, age: {age}, gender: {gender}")
        try:
            data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemes_data.json")
            if not os.path.exists(data_path):
                return "Error: The schemes database file could not be found. Please inform the user that we are currently unable to retrieve scheme information due to a technical issue."
            
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            last_updated = data.get("last_updated", "unknown date")
            schemes = data.get("schemes", {})
            
            # Case insensitive lookup
            matched_key = None
            for key in schemes.keys():
                if key.lower() == scheme_name.lower():
                    matched_key = key
                    break
                    
            if not matched_key:
                supported = ", ".join(schemes.keys())
                return f"Scheme '{scheme_name}' not found. Supported schemes are: {supported}. Please ask the user to clarify which scheme they want to check."
                
            scheme = schemes[matched_key]
            
            # Check eligibility
            reasons_ineligible = []
            min_age = scheme.get("min_age")
            max_age = scheme.get("max_age")
            
            if age is not None:
                if age < min_age or age > max_age:
                    reasons_ineligible.append(f"Age {age} is outside the allowed range of {min_age} to {max_age} years.")
                    
            if scheme.get("only_female") and (gender is None or gender.lower() != "female"):
                reasons_ineligible.append("This scheme is only available for female applicants.")
                
            if reasons_ineligible:
                eligibility_status = "Not Eligible"
                explanation = " ".join(reasons_ineligible)
            else:
                eligibility_status = "Eligible"
                explanation = f"The caller meets the primary eligibility criteria (age: {age}, gender: {gender or 'any'})."
                
            response = {
                "scheme": matched_key,
                "status": eligibility_status,
                "explanation": explanation,
                "required_documents": scheme.get("documents", []),
                "description": scheme.get("description", ""),
                "data_as_of": last_updated
            }
            
            return json.dumps(response, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error checking scheme eligibility: {e}")
            return f"Error: A temporary issue occurred while processing the eligibility check: {str(e)}. Please inform the user and try again later."



server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Fetch user_id from connected participants
    user_id = "unknown_user"
    for _ in range(10):
        if ctx.room.remote_participants:
            user_id = list(ctx.room.remote_participants.values())[0].identity
            break
        await asyncio.sleep(0.5)

    caller_data = db.get_caller(user_id)

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3", language="multi"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-3.5-flash-lite",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="hi-IN-anisha", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(ev: UserInputTranscribedEvent):
        transcript = ev.transcript.strip().lower()
        if not transcript:
            return

        # Check for Devanagari script characters (native Hindi)
        has_devanagari = any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in transcript)

        # Check for common Hinglish/Hindi romanized keywords
        hindi_keywords = {
            "kya", "hai", "aur", "main", "haan", "nahin", "aap", "namaste", "shukriya", 
            "yojana", "batao", "bataiye", "samjhao", "dhan", "suraksha", "bima", "pension",
            "mein", "ke", "ki", "se", "ko", "ka", "jo", "toh", "bhi", "ho", "kar", "raha",
            "rahi", "rha", "rhi", "mujhe", "mera", "meri", "hum", "tum", "apna", "apni",
            "karke", "karo", "karna", "tha", "thi", "the", "ab", "kab", "tab", "sab"
        }
        words = set(transcript.split())
        has_hindi_words = not words.isdisjoint(hindi_keywords)

        if has_devanagari or has_hindi_words:
            logger.info(f"Detected Hindi/Hinglish speech: '{ev.transcript}'. Switching TTS to hi-IN-anisha.")
            session.tts.update_options(voice="hi-IN-anisha")
        else:
            logger.info(f"Detected English speech: '{ev.transcript}'. Switching TTS to en-IN-anisha.")
            session.tts.update_options(voice="en-IN-anisha")

    @session.on("conversation_item_added")
    def on_conversation_item_added(ev: ConversationItemAddedEvent):
        chat_message = ev.item
        if chat_message and chat_message.role == "assistant":
            content = chat_message.text_content
            if content:
                logger.info(f"Publishing agent response to chat: {content}")
                asyncio.create_task(ctx.room.local_participant.send_text(
                    message=str(content),
                    topic="lk.chat"
                ))



    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(user_id=user_id, caller_data=caller_data),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
            text_output=room_io.TextOutputOptions(sync_transcription=False),
            text_input=True,
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
