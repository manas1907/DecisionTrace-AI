import json
import uuid
from datetime import datetime
from typing import Literal, List
from openai import OpenAI
from pydantic import BaseModel, Field

# ================= CONFIG =================

MODEL_NAME = "gpt-4o-mini"
CONFIDENCE_HIGH = 0.75
CONFIDENCE_MEDIUM = 0.5
LOG_FILE = "decision_logs.jsonl"

client = OpenAI()

# ================= DATA SCHEMA =================

class DecisionOutput(BaseModel):
    final_answer: str = Field(..., description="The final decision or answer")
    assumptions: List[str] = Field(..., description="Key assumptions used")
    evidence_type: Literal["retrieved", "inferred", "prior"] = Field(
        ..., description="Source of reasoning"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low", "Medium", "High"]

    decision_id: str
    timestamp: str

# ================= CORE ENGINE =================

class DecisionTraceEngine:
    def __init__(self):
        self.client = client

    def generate_decision(self, user_prompt: str) -> DecisionOutput:
        system_prompt = 

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw = json.loads(response.choices[0].message.content)

        confidence = float(raw["confidence"])
        risk = self.assess_risk(confidence, raw["evidence_type"])

        return DecisionOutput(
            final_answer=raw["final_answer"],
            assumptions=raw["assumptions"],
            evidence_type=raw["evidence_type"],
            confidence=confidence,
            risk_level=risk,
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
        )

    def assess_risk(self, confidence: float, evidence_type: str) -> str:
        if confidence < CONFIDENCE_MEDIUM:
            return "High"

        if evidence_type == "inferred":
            return "Medium"

        if confidence >= CONFIDENCE_HIGH:
            return "Low"

        return "Medium"

# ================= LOGGING =================

def log_decision(decision: DecisionOutput):
    with open(LOG_FILE, "a") as f:
        f.write(decision.model_dump_json() + "\n")

# ================= CLI =================

def main():
    engine = DecisionTraceEngine()

    print("\nDecisionTrace AI — Auditable GenAI Decisions\n")

    while True:
        query = input("Enter decision query (or exit): ")
        if query.lower() == "exit":
            break

        decision = engine.generate_decision(query)
        log_decision(decision)

        print("\n--- DECISION TRACE ---")
        print("Answer:", decision.final_answer)
        print("Assumptions:", decision.assumptions)
        print("Evidence Type:", decision.evidence_type)
        print("Confidence:", decision.confidence)
        print("Risk Level:", decision.risk_level)
        print("Decision ID:", decision.decision_id)

if __name__ == "__main__":
    main()
