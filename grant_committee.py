# { "Depends": "py-genlayer:test" }

import json
from genlayer import *


class GrantCommittee(gl.Contract):

    owner: Address
    proposal_counter: u256
    total_approved: u256
    total_rejected: u256
    proposal_data: DynArray[str]

    def __init__(self, owner_address: Address):
        self.owner = owner_address
        self.proposal_counter = u256(0)
        self.total_approved = u256(0)
        self.total_rejected = u256(0)

    @gl.public.view
    def get_proposal(self, proposal_id: str) -> str:
        title = self._get(proposal_id, "title")
        if not title:
            return "Proposal not found"
        return (
            f"ID: {proposal_id} | "
            f"Title: {title} | "
            f"Applicant: {self._get(proposal_id, 'applicant')} | "
            f"Budget: {self._get(proposal_id, 'budget')} | "
            f"Status: {self._get(proposal_id, 'status')} | "
            f"Score: {self._get(proposal_id, 'score')}/100 | "
            f"Decision: {self._get(proposal_id, 'decision')} | "
            f"Reasoning: {self._get(proposal_id, 'reasoning')}"
        )

    @gl.public.view
    def get_proposal_count(self) -> u256:
        return self.proposal_counter

    @gl.public.view
    def get_summary(self) -> str:
        return (
            f"AI Grant Committee\n"
            f"Total Proposals: {int(self.proposal_counter)}\n"
            f"Approved: {int(self.total_approved)}\n"
            f"Rejected: {int(self.total_rejected)}"
        )

    @gl.public.write
    def submit_proposal(
        self,
        title: str,
        description: str,
        objectives: str,
        budget: str,
        timeline: str,
        evidence_url: str,
    ) -> str:
        caller = str(gl.message.sender_address)
        proposal_id = str(int(self.proposal_counter))

        self._set(proposal_id, "title", title)
        self._set(proposal_id, "description", description[:500])
        self._set(proposal_id, "objectives", objectives[:300])
        self._set(proposal_id, "budget", budget)
        self._set(proposal_id, "timeline", timeline)
        self._set(proposal_id, "evidence_url", evidence_url)
        self._set(proposal_id, "applicant", caller)
        self._set(proposal_id, "status", "pending")
        self._set(proposal_id, "score", "0")
        self._set(proposal_id, "decision", "")
        self._set(proposal_id, "reasoning", "")

        self.proposal_counter = u256(int(self.proposal_counter) + 1)
        return f"Proposal {proposal_id} submitted: {title}"

    @gl.public.write
    def evaluate_proposal(self, proposal_id: str) -> str:
        assert self._get(proposal_id, "status") == "pending", "Proposal is not pending"

        title = self._get(proposal_id, "title")
        description = self._get(proposal_id, "description")
        objectives = self._get(proposal_id, "objectives")
        budget = self._get(proposal_id, "budget")
        timeline = self._get(proposal_id, "timeline")
        evidence_url = self._get(proposal_id, "evidence_url")

        def leader_fn():
            web_data = ""
            try:
                response = gl.nondet.web.get(evidence_url)
                raw = response.body.decode("utf-8")
                web_data = raw[:2000]
            except Exception:
                web_data = "No supporting evidence available."

            prompt = f"""You are an AI member of a grant committee evaluating funding proposals
for a blockchain ecosystem. Evaluate this proposal based on four criteria:

1. Impact: How much will this benefit the ecosystem?
2. Feasibility: Is the plan realistic and achievable?
3. Clarity: Are the objectives and deliverables well defined?
4. Value for money: Is the budget reasonable for the scope?

Proposal Title: {title}

Description:
{description}

Objectives:
{objectives}

Budget requested: {budget}
Timeline: {timeline}

Supporting evidence from {evidence_url}:
{web_data}

Score this proposal from 0 to 100 where proposals scoring 70 or above are APPROVED
and proposals below 70 are REJECTED.

Respond ONLY with this JSON:
{{"score": 75, "decision": "APPROVED", "reasoning": "two sentences explaining the evaluation"}}

score is an integer 0 to 100, decision is exactly APPROVED or REJECTED,
reasoning covers the main strengths or weaknesses found.
No extra text."""

            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)

            score = int(data.get("score", 0))
            decision = data.get("decision", "REJECTED")
            reasoning = data.get("reasoning", "")

            score = max(0, min(100, score))
            if decision not in ("APPROVED", "REJECTED"):
                decision = "REJECTED" if score < 70 else "APPROVED"

            return json.dumps({
                "score": score,
                "decision": decision,
                "reasoning": reasoning
            }, sort_keys=True)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                validator_raw = leader_fn()
                leader_data = json.loads(leader_result.calldata)
                validator_data = json.loads(validator_raw)
                if leader_data["decision"] != validator_data["decision"]:
                    return False
                return abs(leader_data["score"] - validator_data["score"]) <= 10
            except Exception:
                return False

        raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        data = json.loads(raw)

        score = data["score"]
        decision = data["decision"]
        reasoning = data["reasoning"]

        self._set(proposal_id, "status", "evaluated")
        self._set(proposal_id, "score", str(score))
        self._set(proposal_id, "decision", decision)
        self._set(proposal_id, "reasoning", reasoning)

        if decision == "APPROVED":
            self.total_approved = u256(int(self.total_approved) + 1)
        else:
            self.total_rejected = u256(int(self.total_rejected) + 1)

        return (
            f"Proposal {proposal_id} evaluated. "
            f"Score: {score}/100. "
            f"Decision: {decision}. "
            f"{reasoning}"
        )

    def _get(self, proposal_id: str, field: str) -> str:
        key = f"{proposal_id}_{field}:"
        for i in range(len(self.proposal_data)):
            if self.proposal_data[i].startswith(key):
                return self.proposal_data[i][len(key):]
        return ""

    def _set(self, proposal_id: str, field: str, value: str) -> None:
        key = f"{proposal_id}_{field}:"
        for i in range(len(self.proposal_data)):
            if self.proposal_data[i].startswith(key):
                self.proposal_data[i] = f"{key}{value}"
                return
        self.proposal_data.append(f"{key}{value}")
            
