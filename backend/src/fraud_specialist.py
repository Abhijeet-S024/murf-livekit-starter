# fraud_specialist.py
#
# FraudSpecialist — Cyber Fraud & Account Containment Specialist Agent
# Handles cyber fraud calls after a report/escalation has been filed.

import logging
from livekit.agents import Agent, tokenize
from livekit.plugins import murf

try:
    from specialist_prompts import FRAUD_SPECIALIST_PROMPT
except ImportError:
    from src.specialist_prompts import FRAUD_SPECIALIST_PROMPT

logger = logging.getLogger("fraud_specialist")

class FraudSpecialist(Agent):
    """Cyber Fraud & Account Containment Specialist Agent."""

    def __init__(self, user_id: str, ref_id: str, **kwargs) -> None:
        instructions = (
            f"{FRAUD_SPECIALIST_PROMPT}\n\n"
            f"IMPORTANT CALL CONTEXT:\n"
            f"- A formal cyber fraud escalation report has already been filed successfully.\n"
            f"- Escalation Reference ID: {ref_id}\n"
            f"- Inform the caller that their case reference number is {ref_id}.\n"
            f"- Reassure them that we are investigating the issue and guide them on immediate safety measures (like calling the 1930 national helpline, checking bank statements, etc.).\n"
            f"- Mirror the user's preferred language (Hindi, English, or Hinglish) based on the history.\n"
            f"- Speak in a calm, protective, and authoritative tone (Samar's voice)."
        )
        super().__init__(
            instructions=instructions,
            tts=murf.TTS(
                voice="Samar",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            ),
            **kwargs,
        )
        self.user_id = user_id
        self.ref_id = ref_id

    async def on_enter(self) -> None:
        """Introduce the specialist and reassure the user about the filed report."""
        await self.session.generate_reply(
            instructions=(
                f"The user has just been transferred to you after a cyber fraud report was filed (Ref ID: {self.ref_id}). "
                "Introduce yourself calmly as Samar, the Cyber Fraud & Account Containment Specialist. "
                f"Reassure them that their report has been successfully recorded with Reference ID {self.ref_id}. "
                "Let them know you are here to advise them on the next steps for their safety."
            )
        )
