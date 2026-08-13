import logging
import os

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    tokenize,
    room_io,
    function_tool,
)
from livekit.plugins import murf, silero, openai, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

try:
    from prompt import SYSTEM_PROMPT
except ImportError:
    from src.prompt import SYSTEM_PROMPT

try:
    import db
except ImportError:
    import src.db as db


class Assistant(Agent):
    def __init__(self, user_id: str, instructions: str = SYSTEM_PROMPT) -> None:
        super().__init__(instructions=instructions)
        self.user_id = user_id
        # Analytics: set to True when eligibility check returns a valid result
        self._call_succeeded: bool = False
        self._success_trigger: str | None = None

    @function_tool
    async def lookup_caller(self) -> str:
        """Looks up the current caller's details and saved facts in the database.
        Always execute this tool at the very beginning of the call to check if they are a returning caller.
        """
        logger.info(f"Tool lookup_caller called for current user: {self.user_id}")
        user_info = db.get_caller(self.user_id)
        if user_info:
            import json
            return json.dumps(user_info)
        return f"No record found for user ID: {self.user_id}"

    @function_tool
    async def create_escalation(
        self,
        caller_name: str,
        reason: str,
        situation_summary: str,
        what_agent_checked: str,
        urgency: str,
        caller_language: str,
        preferred_followup: str,
    ) -> str:
        """Creates a human escalation request when the caller reports fraud or needs a decision beyond the agent's scope.
        IMPORTANT: Only call this tool AFTER the caller has explicitly given verbal permission to share their information.
        NEVER include OTP, PIN, CVV, passwords, or full account numbers in any field.

        Args:
            caller_name: The caller's name (first name or full name). Use 'Unknown' if not known.
            reason: Category of escalation. Must be exactly one of: 'fraud_report' or 'out_of_scope_decision'.
            situation_summary: A brief, plain-language summary of what happened (max 2-3 sentences). No sensitive data.
            what_agent_checked: What the agent already provided or verified during this call (e.g., 'Advised caller about 1930 helpline, confirmed no OTP was shared').
            urgency: How urgent the situation is. Must be exactly one of: 'high', 'medium', 'low'.
            caller_language: The language the caller used during this call (e.g., 'Hindi', 'English', 'Hinglish').
            preferred_followup: How the caller prefers to be contacted. Must be exactly one of: 'call', 'sms', 'whatsapp'.
        """
        import random
        import string
        import json

        logger.info(f"Tool create_escalation called for user_id: {self.user_id}, reason: {reason}")

        # Generate a unique 6-digit numeric reference ID
        ref_suffix = "".join(random.choices(string.digits, k=6))
        ref_id = f"REF-{ref_suffix}"

        # Save to database (db helpers apply sanitisation internally)
        db.save_escalation(
            ref_id=ref_id,
            caller_id=self.user_id,
            caller_name=caller_name,
            reason=reason,
            situation_summary=situation_summary,
            what_agent_checked=what_agent_checked,
            urgency=urgency,
            caller_language=caller_language,
            preferred_followup=preferred_followup,
        )

        logger.info(f"Escalation created: {ref_id} for user_id: {self.user_id} with urgency: {urgency}")

        return json.dumps({
            "success": True,
            "ref_id": ref_id,
            "message": (
                f"Escalation request created successfully. "
                f"Reference ID: {ref_id}. "
                f"A human specialist will follow up via {preferred_followup}. "
                f"Tell the caller to note down their reference number {ref_id} and that no immediate callback time can be promised."
            ),
            "dashboard_url": "http://localhost:5050"
        })


    @function_tool
    async def save_caller_facts(self, name: str, language_preference: str, facts: dict) -> str:
        """Saves current caller's details and facts (e.g. checked schemes, eligibility answers) to the database.
        Always verify the caller has given verbal permission/consent before calling this.
        
        Args:
            name: The caller's name.
            language_preference: The caller's preferred language (e.g., Hindi, English, Hinglish).
            facts: A dictionary of key-value pairs representing facts about the caller (e.g., eligibility, schemes checked). Do not store account or ID numbers.
        """
        logger.info(f"Tool save_caller_facts called for user_id: {self.user_id}, name: {name}")
        # Clean facts from any ID numbers or account numbers
        cleaned_facts = {}
        for k, v in facts.items():
            if "id" in k.lower() or "account" in k.lower() or "number" in k.lower():
                continue
            cleaned_facts[k] = v
        
        db.save_caller(self.user_id, name, language_preference, cleaned_facts)
        return f"Successfully saved details for user {name} (ID: {self.user_id})."

    @function_tool
    async def check_scheme_eligibility(
        self,
        scheme_name: str,
        age: int,
        is_income_tax_payer: bool = False,
        girl_child_age: int = -1,
        is_indian_resident: bool = True
    ) -> str:
        """Checks the eligibility of a caller for a specific Indian government financial scheme and returns the required document checklist.
        
        Only call this tool when the caller explicitly asks about their eligibility, required documents, or interest rates/premiums for one of the supported schemes: PMJDY, PMSBY, PMJJBY, APY, or SSY, AND you have gathered the necessary parameters (such as age, tax payer status, or girl child details). Do NOT call this tool for general conversations or if you don't know which scheme they are interested in.
        
        Args:
            scheme_name: The abbreviation of the scheme name to check. Must be exactly one of: "PMJDY", "PMSBY", "PMJJBY", "APY", "SSY".
            age: The beneficiary's age in years.
            is_income_tax_payer: True if the beneficiary pays income tax, False otherwise. (Important for APY eligibility).
            girl_child_age: The age of the girl child in years. (Mandatory when checking Sukanya Samriddhi Yojana / SSY). Use -1 if not applicable.
            is_indian_resident: True if the beneficiary is a resident of India, False otherwise.
        """
        import json
        from datetime import datetime
        
        today_str = datetime.now().strftime("%B %d, %Y")
        
        try:
            # SIMULATE TRANSIENT FAILURE (Step 4 & user request)
            # The first call to this tool in the session will fail, and subsequent retries will succeed.
            attempts = getattr(self, "_eligibility_attempts", 0) + 1
            self._eligibility_attempts = attempts
            if attempts == 1:
                raise Exception("API Connection Timeout (Simulated Transient Error)")
            
            logger.info(f"Tool check_scheme_eligibility called (Attempt {attempts}) for scheme: {scheme_name}, user_id: {self.user_id}")
            name_upper = scheme_name.upper().strip()
            supported_schemes = ["PMJDY", "PMSBY", "PMJJBY", "APY", "SSY"]
            
            if name_upper not in supported_schemes:
                return json.dumps({
                    "eligible": False,
                    "reason": f"Scheme '{scheme_name}' is not supported. Supported schemes are: {', '.join(supported_schemes)}.",
                    "document_checklist": [],
                    "scheme_benefits": {},
                    "data_last_updated": today_str,
                    "error": f"Unsupported scheme: {scheme_name}"
                })
                
            if not is_indian_resident:
                return json.dumps({
                    "eligible": False,
                    "reason": f"Only Indian residents are eligible for {name_upper}.",
                    "document_checklist": [],
                    "scheme_benefits": {},
                    "data_last_updated": today_str
                })
                
            if name_upper == "PMJDY":
                # Pradhan Mantri Jan Dhan Yojana
                is_eligible = age >= 10
                reason = "Eligible. Open to any resident Indian citizen aged 10 or above. (Designed for individuals who do not have any other bank account)." if is_eligible else "Ineligible. Min age to open PMJDY account is 10 years."
                docs = ["Aadhaar Card (primary KYC)", "PAN Card (if available)", "Or other officially valid document (Voter ID, driving license, NREGA card)"]
                benefits = {
                    "benefits_and_interest": "Basic savings account with zero minimum balance requirement, earn interest on savings deposit (approx 2.70% to 3.00% p.a. depending on bank), free Rupay debit card with built-in Rs 2 Lakh accidental insurance cover, and overdraft facility up to Rs 10,000 for eligible accounts."
                }
                
            elif name_upper == "PMSBY":
                # Pradhan Mantri Suraksha Bima Yojana
                is_eligible = 18 <= age <= 70
                reason = "Eligible. Open to individuals aged between 18 and 70 years." if is_eligible else f"Ineligible. Age must be between 18 and 70 years. Provided age: {age}."
                docs = ["Aadhaar Card (primary KYC)", "Savings bank account details", "Consent form for auto-debit of premium"]
                benefits = {
                    "premium": "Rs 20 per annum (auto-debited from savings account)",
                    "insurance_cover": "Rs 2 Lakh for accidental death or total permanent disability, and Rs 1 Lakh for partial permanent disability.",
                    "validity": "1 year (June 1 to May 31), auto-renewed annually."
                }
                
            elif name_upper == "PMJJBY":
                # Pradhan Mantri Jeevan Jyoti Bima Yojana
                is_eligible = 18 <= age <= 50
                reason = "Eligible. Open to individuals aged between 18 and 50 years." if is_eligible else f"Ineligible. Age must be between 18 and 50 years. Provided age: {age}."
                docs = ["Aadhaar Card (primary KYC)", "Savings bank account details", "Consent form for auto-debit of premium", "Self-declaration of good health (if enrolling late)"]
                benefits = {
                    "premium": "Rs 436 per annum (auto-debited from savings account)",
                    "insurance_cover": "Rs 2 Lakh life insurance cover for death due to any cause.",
                    "validity": "1 year (June 1 to May 31), auto-renewed annually. Risk cover continues up to age 55 if enrolled by 50."
                }
                
            elif name_upper == "APY":
                # Atal Pension Yojana
                if is_income_tax_payer:
                    is_eligible = False
                    reason = "Ineligible. Income tax payers are not eligible to join Atal Pension Yojana (rule effective since October 1, 2022)."
                else:
                    is_eligible = 18 <= age <= 40
                    reason = "Eligible. Open to all non-taxpaying citizens aged between 18 and 40 years." if is_eligible else f"Ineligible. Age must be between 18 and 40 years to enroll. Provided age: {age}."
                docs = ["Aadhaar Card (primary KYC)", "Mobile number", "Savings bank account details", "Auto-debit authorization form"]
                benefits = {
                    "premium": "Varies based on entry age and selected pension slab.",
                    "pension_benefit": "Guaranteed minimum pension of Rs 1,000, Rs 2,000, Rs 3,000, Rs 4,000, or Rs 5,000 per month after age 60, depending on contributions.",
                    "co_contribution": "Government co-contribution is not available for new subscribers, but the pension amount is fully guaranteed by the Government of India."
                }
                
            elif name_upper == "SSY":
                # Sukanya Samriddhi Yojana
                if girl_child_age == -1:
                    return json.dumps({
                        "eligible": "uncertain",
                        "reason": "Please provide the age of the girl child using the 'girl_child_age' parameter.",
                        "document_checklist": [],
                        "scheme_benefits": {},
                        "data_last_updated": today_str
                    })
                is_eligible = 0 <= girl_child_age <= 10
                reason = "Eligible. Open for girl child aged 10 years or below." if is_eligible else f"Ineligible. The account can only be opened for a girl child aged 10 years or below. Provided girl child age: {girl_child_age}."
                docs = ["Birth certificate of the girl child (mandatory)", "Aadhaar Card and PAN Card of the parent/guardian", "Photograph of the girl child and parent", "Proof of address"]
                benefits = {
                    "interest_rate": f"8.2% per annum (compounded annually, tax-free interest, interest rate updated for fiscal year 2025-2026 as of {today_str})",
                    "tax_benefits": "Triple tax exemption under Section 80C of the Income Tax Act.",
                    "maturity": "Matures after 21 years from account opening or upon marriage of the girl child after she reaches 18 years."
                }

            else:
                # Unknown scheme name
                return json.dumps({
                    "eligible": "unknown",
                    "reason": f"'{name_upper}' is not a recognized scheme. Supported schemes are: PMJDY, PMSBY, PMJJBY, APY, SSY.",
                    "document_checklist": [],
                    "scheme_benefits": {},
                    "data_last_updated": today_str
                })

            result = json.dumps({
                "eligible": is_eligible,
                "reason": reason,
                "document_checklist": docs,
                "scheme_benefits": benefits,
                "data_last_updated": today_str
            })
            # Mark call as successful — caller received eligibility result + document list
            self._call_succeeded = True
            self._success_trigger = "check_scheme_eligibility"
            return result

        except Exception as e:
            logger.error(f"Error checking scheme eligibility: {e}")
            return json.dumps({
                "eligible": "error",
                "reason": "The eligibility checker system is temporarily experiencing technical issues. Please check the inputs or try again shortly.",
                "document_checklist": [],
                "scheme_benefits": {},
                "data_last_updated": today_str,
                "error": str(e)
            })



server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="dhan-rakshak")
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Initialize SQLite database
    db.init_db()

    # Retrieve the participant's identity and detect if it is a SIP call
    user_id = "unknown_user"
    is_sip = ctx.room.name.startswith("outbound_call_room")
    for p_identity, p_info in ctx.room.remote_participants.items():
        user_id = p_identity
        if p_info.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            is_sip = True
        break

    logger.info(f"Active connection with user_id: {user_id}, is_sip: {is_sip}")

    # ── Analytics: record call start ──────────────────────────────────────────
    db.record_call_start(
        call_id=ctx.room.name,
        user_id=user_id,
        call_type="sip" if is_sip else "browser",
    )
    logger.info(f"Call analytics started for room: {ctx.room.name}")

    import random
    schemes_list = [
        "Pradhan Mantri Jan Dhan Yojana",
        "Pradhan Mantri Suraksha Bima Yojana",
        "Pradhan Mantri Jeevan Jyoti Bima Yojana",
        "Atal Pension Yojana",
        "Sukanya Samriddhi Yojana"
    ]
    selected_scheme = random.choice(schemes_list)

    if is_sip:
        instructions = (
            f"{SYSTEM_PROMPT}\n\n"
            "OUTBOUND CALL SCENARIO:\n"
            "- Ignore any default returning caller logic. Do NOT check for returning caller facts or greet them by name at the start.\n"
            "- IMPORTANT: You MUST strictly open the conversation with these first two sentences in English:\n"
            "  1. 'Hello, this is Shreya calling from Dhan Rakshak.'\n"
            f"  2. 'We found you eligible for the {selected_scheme} scheme, and the deadline is on August 15th, so hurry up! If you want to know more, say yes, and if you want to stop these calls, say no.'\n"
            f"- If the user says 'yes', you must explain the eligibility criteria for ONLY the {selected_scheme} scheme in EXACTLY ONE SHORT SENTENCE (under 15 words). Do NOT explain any other schemes and do NOT use long paragraphs.\n"
            "- IMPORTANT: To avoid speaking all at once, you MUST speak slowly and keep your responses extremely short (under 15 words).\n"
            "- If the user says 'no', you must wrap up the call. If they ask how to stop these types of calls, reply exactly: 'To stop these calls, press or say 1.'\n"
            "- Do not ask any questions during the main explanation.\n"
            "- Do not say anything else in your opening turn. Wait for the user's response after this opening."
        )
    else:
        instructions = f"{SYSTEM_PROMPT}\n\nCURRENT USER CALL INFO:\n- Current Caller User ID: {user_id}\n- IMPORTANT: You MUST immediately call `lookup_caller` at the very start of the conversation. If a record is returned, welcome the user back by name and reference their previous interaction (e.g. 'नमस्ते Ramesh जी, पिछली बार हमने आपके Atal Pension Yojana के बारे में बात की थी। क्या उससे जुड़ा कोई सवाल है?'). If no record is found, greet them as a new user."



    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        stt=deepgram.STT(model="nova-3", language="multi"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # Using OpenRouter as proxy for Gemini — avoids the tight free-tier daily quota on the Gemini API directly
        llm=openai.LLM(
                model=os.environ.get("OPENROUTER_MODEL", "google/gemini-3.6-flash"),
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ["OPENROUTER_API_KEY"],
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        tts=murf.TTS(
                voice="Anisha", # make sure locale key is not hardcoded
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=False,
    )

    # Start the session, which initializes the voice pipeline and warms up the models
    assistant = Assistant(user_id=user_id, instructions=instructions)
    await session.start(
        agent=assistant,
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
        ),
    )

    # ── Analytics: record call outcome when room closes ────────────────────────
    room_name = ctx.room.name

    @ctx.room.on("disconnected")
    def _on_room_disconnected(*_args):
        outcome = "success" if assistant._call_succeeded else "failed"
        trigger = assistant._success_trigger
        logger.info(
            f"Call ended for room {room_name}: outcome={outcome}, trigger={trigger}"
        )
        db.record_call_end(room_name, outcome, trigger)

    # Join the room and connect to the user
    await ctx.connect()

    if is_sip:
        # Trigger the compliant 2-sentence opening greeting automatically for the outbound call
        await session.say(
            f"Hello, this is Shreya calling from Jan Sahay. "
            f"We found you eligible for the {selected_scheme} scheme, and the deadline is on August 15th, so hurry up! "
            f"If you want to know more, say yes, and if you want to stop these calls, say no.",
            allow_interruptions=True
        )



if __name__ == "__main__":
    cli.run_app(server)
