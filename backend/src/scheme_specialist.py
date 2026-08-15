# scheme_specialist.py
#
# YojanaVisheshagya — Government Scheme Specialist Agent
# Handles deep-dive questions on Indian government financial schemes:
#   PMJDY, PMSBY, PMJJBY, APY, SSY, Mudra Loan
#
# Invoked via handoff from the main Dhan Rakshak agent.

import logging
import json
import os
from datetime import datetime

from livekit.agents import Agent, RunContext, function_tool
from livekit.plugins import murf
from livekit.agents import tokenize

try:
    import db
except ImportError:
    import src.db as db

logger = logging.getLogger("scheme_specialist")

SPECIALIST_PROMPT = """
IDENTITY:
- Name: Yojana Visheshagya (योजना विशेषज्ञ)
- Role: You are a dedicated Government Financial Scheme Specialist. Your only job is to help users understand Indian government financial schemes in full detail — eligibility, required documents, application steps, benefits, and comparisons.
- You were connected from Dhan Rakshak, the main banking assistant. The user's previous conversation context has been passed to you, so you know what they were asking about.

SCOPE — what you handle:
- Eligibility checks for PMJDY, PMSBY, PMJJBY, APY, Sukanya Samriddhi Yojana (SSY), and Mudra Loan.
- Full document checklists for applying to any of the above schemes.
- Step-by-step application guidance (how to apply at a bank, Common Service Centre, or online portal).
- Scheme comparisons (e.g., "Which is better for me — PMSBY or PMJJBY?").
- Benefit calculations (APY pension slabs, insurance cover amounts, premium amounts).
- Scheme-specific FAQ.

SCOPE — what you do NOT handle (redirect politely):
- Fraud awareness, cybercrime, scam warnings — say "Dhan Rakshak can help you with that. Please reconnect to the main assistant."
- Account access, balance, or transaction queries.
- Loan or scheme approval — you can explain eligibility but never guarantee approval.
- Legal or tax advice.
- OTP, PIN, CVV, passwords, or any sensitive credentials — never ask for these.

SCHEME ELIGIBILITY INSTRUCTIONS:
- Supported schemes and basic rules:
  1. Atal Pension Yojana (APY): Age 18 to 40. Non-income-tax payers only. Requires savings bank account.
  2. PM Jan Dhan Yojana (PMJDY): Age 10+. No existing bank account. Basic savings account.
  3. PM Jeevan Jyoti Bima Yojana (PMJJBY): Age 18 to 50. Requires savings bank account.
  4. PM Suraksha Bima Yojana (PMSBY): Age 18 to 70. Requires savings bank account.
  5. Sukanya Samriddhi Yojana (SSY): Girl child age 0 to 10. Only for female children.
  6. Mudra Loan: Age 18+. Requires a business idea or existing micro-enterprise.
- When the user asks about eligibility or documents:
  1. Ask for the necessary parameters (age, income tax status, girl child age) if not already in the conversation context.
  2. Call `check_scheme_eligibility` with the collected parameters.
  3. Present results clearly: eligibility status, reason, document checklist, and benefits.
  4. Explicitly mention that data is accurate as of "August 2026".
  5. If the tool fails, say: "I am facing a temporary issue fetching the details. Please try again in a moment."
- After giving the eligibility and document results, proactively offer: "Would you like me to explain the step-by-step application process as well?"

APPLICATION GUIDANCE (step-by-step, if user asks):
- PMJDY: Visit nearest bank branch or Business Correspondent (BC) point → Fill Form A → Submit KYC documents → Account opened same day.
- PMSBY / PMJJBY: Visit bank branch or use net banking / mobile banking → Fill enrollment form → Auto-debit consent → Enrolled.
- APY: Visit bank branch or use net banking → Fill APY enrollment form → Choose pension slab → Auto-debit authorization.
- SSY: Visit Post Office or authorized bank branch → Fill SSY account opening form → Submit girl child's birth certificate and parent KYC → Minimum deposit Rs 250.
- Mudra Loan: Visit bank / NBFC / MFI → Fill Mudra loan application → Submit business plan and KYC → Loan processed (Shishu up to Rs 50,000; Kishore up to Rs 5 Lakh; Tarun up to Rs 10 Lakh).

LANGUAGE:
- Mirror the user's language (Hindi, English, or Hinglish).
- Speak in simple, warm, conversational language — as if explaining to a family member.
- Keep responses concise and split into short sentences.
- Do NOT use Markdown formatting, asterisks, bullet symbols, emojis, or hashtags in voice responses. Use plain conversational text.
- IMPORTANT: Keep the tone polite, warm and highly respectful (e.g., using 'aap').

GUARDRAILS:
- NEVER ask for: OTP, ATM PIN, UPI PIN, CVV, Debit/Credit Card Number, Internet Banking Password, Aadhaar Number, PAN Number, Full Bank Account Number.
- NEVER promise or guarantee scheme approval, loan sanction, or subsidy.
- If the user shares sensitive information, say: "Aapki suraksha ke liye, kripya apna OTP, PIN, ya khata sankhya kisi ke saath share na karein."

ON GREETING (first turn):
- Acknowledge the user's prior context briefly.
- Introduce yourself as the Scheme Specialist.
- Immediately pick up from where Dhan Rakshak left off — the user should not need to repeat themselves.
- Example: "Namaste! Main Yojana Visheshagya hoon — sarkari yojanaon ka visheshagya. Main aapko [scheme name] ke baare mein poori jankari dunga. Chaliye shuru karte hain."
"""


class YojanaVisheshagya(Agent):
    """Government Scheme Specialist Agent — handles deep-dive scheme questions."""

    def __init__(self, user_id: str, **kwargs) -> None:
        super().__init__(
            instructions=SPECIALIST_PROMPT,
            tts=murf.TTS(
                voice="Pooja",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            ),
            **kwargs,
        )
        self.user_id = user_id

    async def on_enter(self) -> None:
        """Introduce the specialist and pick up the conversation context."""
        await self.session.generate_reply(
            instructions=(
                "The user has just been transferred to you from Dhan Rakshak, the main banking assistant. "
                "Review the conversation history above to understand what the user was asking about. "
                "Introduce yourself warmly as 'Yojana Visheshagya' — the Government Scheme Specialist. "
                "Acknowledge what the user was asking about (scheme name or topic) so they know you are already "
                "informed and they do not need to repeat themselves. "
                "Then immediately offer to help with their specific scheme question. "
                "Keep the introduction to two short sentences. Speak in the user's preferred language "
                "(Hindi, English, or Hinglish based on the conversation history)."
            )
        )

    @function_tool
    async def check_scheme_eligibility(
        self,
        scheme_name: str,
        age: int,
        is_income_tax_payer: bool = False,
        girl_child_age: int = -1,
        is_indian_resident: bool = True,
    ) -> str:
        """Checks eligibility for an Indian government financial scheme and returns the document checklist and benefits.

        Call this when the user asks about their eligibility, required documents, premiums, or
        benefits for any of the supported schemes: PMJDY, PMSBY, PMJJBY, APY, SSY, or Mudra Loan.

        Args:
            scheme_name: Abbreviation of the scheme. Must be exactly one of:
                         "PMJDY", "PMSBY", "PMJJBY", "APY", "SSY", "MUDRA".
            age: The beneficiary's age in years.
            is_income_tax_payer: True if the beneficiary pays income tax (relevant for APY).
            girl_child_age: Age of the girl child in years (mandatory for SSY; use -1 if not applicable).
            is_indian_resident: True if the beneficiary is an Indian resident.
        """
        today_str = datetime.now().strftime("%B %d, %Y")

        try:
            logger.info(
                f"YojanaVisheshagya.check_scheme_eligibility: scheme={scheme_name}, "
                f"age={age}, user_id={self.user_id}"
            )
            name_upper = scheme_name.upper().strip()
            supported_schemes = ["PMJDY", "PMSBY", "PMJJBY", "APY", "SSY", "MUDRA"]

            if name_upper not in supported_schemes:
                return json.dumps({
                    "eligible": False,
                    "reason": f"Scheme '{scheme_name}' is not supported. Supported schemes: {', '.join(supported_schemes)}.",
                    "document_checklist": [],
                    "scheme_benefits": {},
                    "data_last_updated": today_str,
                })

            if not is_indian_resident:
                return json.dumps({
                    "eligible": False,
                    "reason": f"Only Indian residents are eligible for {name_upper}.",
                    "document_checklist": [],
                    "scheme_benefits": {},
                    "data_last_updated": today_str,
                })

            if name_upper == "PMJDY":
                is_eligible = age >= 10
                reason = (
                    "Eligible. Open to any resident Indian citizen aged 10 or above "
                    "(designed for individuals without an existing bank account)."
                    if is_eligible
                    else "Ineligible. Minimum age to open a PMJDY account is 10 years."
                )
                docs = [
                    "Aadhaar Card (primary KYC)",
                    "PAN Card (if available)",
                    "Or other officially valid document (Voter ID, Driving License, NREGA card)",
                    "Two passport-size photographs",
                ]
                benefits = {
                    "type": "Basic Savings Account",
                    "zero_balance": "Yes — no minimum balance required",
                    "interest_rate": "Approx 2.70% to 3.00% per annum (varies by bank)",
                    "debit_card": "Free RuPay Debit Card with Rs 2 Lakh accidental insurance cover",
                    "overdraft": "Up to Rs 10,000 for eligible accounts",
                    "application": "Visit nearest bank branch or Business Correspondent (BC) point",
                }

            elif name_upper == "PMSBY":
                is_eligible = 18 <= age <= 70
                reason = (
                    "Eligible. Open to individuals aged 18 to 70 years with a savings bank account."
                    if is_eligible
                    else f"Ineligible. Age must be between 18 and 70 years. Provided age: {age}."
                )
                docs = [
                    "Aadhaar Card (primary KYC)",
                    "Savings bank account details",
                    "Consent form for auto-debit of annual premium",
                ]
                benefits = {
                    "type": "Accidental Insurance",
                    "premium": "Rs 20 per annum (auto-debited from savings account every June 1)",
                    "accidental_death_or_total_disability": "Rs 2 Lakh",
                    "partial_permanent_disability": "Rs 1 Lakh",
                    "validity": "1 year (June 1 to May 31), auto-renewed annually",
                    "application": "Visit bank branch, or enroll via net banking / mobile banking",
                }

            elif name_upper == "PMJJBY":
                is_eligible = 18 <= age <= 50
                reason = (
                    "Eligible. Open to individuals aged 18 to 50 years with a savings bank account."
                    if is_eligible
                    else f"Ineligible. Age must be between 18 and 50 years. Provided age: {age}."
                )
                docs = [
                    "Aadhaar Card (primary KYC)",
                    "Savings bank account details",
                    "Consent form for auto-debit of annual premium",
                    "Self-declaration of good health (if enrolling after the initial open period)",
                ]
                benefits = {
                    "type": "Life Insurance",
                    "premium": "Rs 436 per annum (auto-debited from savings account every June 1)",
                    "life_cover": "Rs 2 Lakh for death due to any cause",
                    "validity": "1 year (June 1 to May 31), auto-renewed annually. Risk cover continues up to age 55 if enrolled by age 50.",
                    "application": "Visit bank branch, or enroll via net banking / mobile banking",
                }

            elif name_upper == "APY":
                if is_income_tax_payer:
                    is_eligible = False
                    reason = "Ineligible. Income tax payers are not eligible for Atal Pension Yojana (rule effective since October 1, 2022)."
                else:
                    is_eligible = 18 <= age <= 40
                    reason = (
                        "Eligible. Open to all non-taxpaying citizens aged 18 to 40 years."
                        if is_eligible
                        else f"Ineligible. Age must be between 18 and 40 years to enroll. Provided age: {age}."
                    )
                docs = [
                    "Aadhaar Card (primary KYC)",
                    "Mobile number registered with bank",
                    "Savings bank account details",
                    "Auto-debit authorization form",
                ]
                benefits = {
                    "type": "Pension Scheme",
                    "pension_slabs": "Rs 1,000 / Rs 2,000 / Rs 3,000 / Rs 4,000 / Rs 5,000 per month after age 60",
                    "premium": "Varies by entry age and chosen pension slab (lower premium if enrolled younger)",
                    "guarantee": "Pension amount fully guaranteed by the Government of India",
                    "spouse_benefit": "Same pension to spouse on subscriber's death",
                    "nominee_benefit": "Accumulated corpus returned to nominee on death of both subscriber and spouse",
                    "application": "Visit bank branch or enroll via net banking / mobile banking",
                }

            elif name_upper == "SSY":
                if girl_child_age == -1:
                    return json.dumps({
                        "eligible": "uncertain",
                        "reason": "Please provide the age of the girl child to check SSY eligibility.",
                        "document_checklist": [],
                        "scheme_benefits": {},
                        "data_last_updated": today_str,
                    })
                is_eligible = 0 <= girl_child_age <= 10
                reason = (
                    "Eligible. The account can be opened for a girl child aged 10 years or below."
                    if is_eligible
                    else f"Ineligible. The account can only be opened for a girl child aged 10 or below. Provided girl child age: {girl_child_age}."
                )
                docs = [
                    "Birth certificate of the girl child (mandatory)",
                    "Aadhaar Card and PAN Card of the parent/guardian",
                    "Passport-size photographs of the girl child and parent",
                    "Proof of address of the parent/guardian",
                ]
                benefits = {
                    "type": "Small Savings Scheme for Girl Child",
                    "interest_rate": f"8.2% per annum (compounded annually, tax-free, as of {today_str})",
                    "tax_benefits": "Triple tax exemption under Section 80C of the Income Tax Act",
                    "minimum_deposit": "Rs 250 per year",
                    "maximum_deposit": "Rs 1.5 Lakh per year",
                    "maturity": "21 years from account opening, or on marriage of the girl after she turns 18",
                    "application": "Visit nearest Post Office or authorized bank branch",
                }

            elif name_upper == "MUDRA":
                is_eligible = age >= 18
                reason = (
                    "Eligible (age criteria met). You must also have a non-farm business idea or an existing micro-enterprise."
                    if is_eligible
                    else f"Ineligible. Minimum age is 18 years. Provided age: {age}."
                )
                docs = [
                    "Proof of Identity (Aadhaar, Voter ID, PAN, Passport)",
                    "Proof of Residence",
                    "Business identity and address proof (licenses, registration certificates)",
                    "Business plan or project report",
                    "Quotations for machinery or equipment (if applicable)",
                    "Passport-size photographs of applicant and partners",
                ]
                benefits = {
                    "type": "Business Loan for Micro-Enterprises",
                    "shishu": "Up to Rs 50,000 — for very new / early-stage businesses",
                    "kishore": "Rs 50,001 to Rs 5 Lakh — for established businesses needing funds to grow",
                    "tarun": "Rs 5,00,001 to Rs 10 Lakh — for larger micro enterprises",
                    "collateral": "No collateral required for Shishu and Kishore categories",
                    "application": "Apply at any bank, NBFC (Non-Banking Financial Company), or MFI (Micro Finance Institution)",
                }

            else:
                return json.dumps({
                    "eligible": "unknown",
                    "reason": f"'{name_upper}' is not recognized. Supported: PMJDY, PMSBY, PMJJBY, APY, SSY, MUDRA.",
                    "document_checklist": [],
                    "scheme_benefits": {},
                    "data_last_updated": today_str,
                })

            return json.dumps({
                "eligible": is_eligible,
                "reason": reason,
                "document_checklist": docs,
                "scheme_benefits": benefits,
                "data_last_updated": today_str,
            })

        except Exception as e:
            logger.error(f"YojanaVisheshagya.check_scheme_eligibility error: {e}")
            return json.dumps({
                "eligible": "error",
                "reason": "The eligibility system is temporarily experiencing technical issues. Please try again in a moment.",
                "document_checklist": [],
                "scheme_benefits": {},
                "data_last_updated": today_str,
                "error": str(e),
            })
