# GenLayer AI Grant Committee

A decentralized grant committee where AI validators evaluate funding proposals and vote on approvals through Optimistic Democracy consensus. Built on GenLayer Testnet Bradbury.

---

## What is this

Grant committees are usually slow, opaque, and subject to bias from whoever sits on the committee. I wanted to see if you could replace that with an AI that evaluates proposals against a consistent set of criteria and commits the decision onchain so anyone can verify how it was reached.

The AI scores each proposal across four dimensions: impact on the ecosystem, feasibility of the plan, clarity of objectives, and value for the budget requested. Proposals that score 70 or above are automatically approved. Everything below is rejected. The decision and full reasoning are stored onchain.

---

## How it works

Anyone can submit a grant proposal with a title, description, objectives, budget, timeline, and a URL pointing to supporting evidence. The contract fetches that URL and the AI evaluates the proposal against the four criteria. Multiple validators independently run the same evaluation and must agree on both the decision and the score within a tolerance of 10 points before the result is finalized.

---

## Functions

submit_proposal takes a title, description, objectives, budget, timeline, and evidence URL and creates the proposal in pending status.

evaluate_proposal takes a proposal id and triggers the AI evaluation through Optimistic Democracy. The AI fetches the evidence URL, scores the proposal from 0 to 100, and issues an APPROVED or REJECTED decision.

get_proposal shows the full proposal including applicant, budget, status, score, decision, and reasoning.

get_summary shows total proposals submitted along with approved and rejected counts.

---

## Test results

Submitted a proposal for a GenLayer Developer Toolkit asking for 5000 USD over 3 months to build reusable contract patterns and example contracts. The AI scored it 75 out of 100 and approved it. The reasoning noted strong ecosystem impact, a reasonable budget for the deliverables, and clear objectives supported by existing activity in the GenLayer ecosystem.

---

## How to run it

Go to GenLayer Studio at https://studio.genlayer.com and create a new file called grant_committee.py. Paste the contract code and set execution mode to Normal Full Consensus. Deploy with your address as owner_address.

Follow this order and wait for FINALIZED at each step. Run get_summary first, then submit_proposal with your grant details, then evaluate_proposal with the proposal id, then get_proposal to see the score and decision.

Note: the contract in this repository uses the Address type in the constructor as required by genvm-lint. When deploying in GenLayer Studio use a version that receives str in the constructor and converts internally with Address(owner_address) since Studio requires primitive types to parse the contract schema correctly.

---

## Resources

GenLayer Docs: https://docs.genlayer.com

Optimistic Democracy: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy

Equivalence Principle: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/equivalence-principle

GenLayer Studio: https://studio.genlayer.com

Discord: https://discord.gg/8Jm4v89VAu
