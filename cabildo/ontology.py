"""Ontology kernel — formal concept hierarchy for campaign operations.

Defines the semantic structure that all other modules query against.
Instead of hardcoded rules scattered across modules, the ontology
provides a single queryable source of truth for:

- What concepts exist (voter, volunteer, donor, opponent, issue...)
- What relationships connect them (voter --lives_in--> district)
- What constraints govern operations (content --requires--> disclosure)
- What workflows are valid (draft --> review --> approve --> post)

Architecture: sits ABOVE SkillDomain as a semantic gatekeeper.
Modules register capabilities; the ontology determines which are
admissible in context.

Inspired by FAOS tripartite O = (R, D, I) — Role, Domain, Interaction.
Adapted for municipal campaigns where formal provability matters for
compliance but heavyweight OWL2 tooling doesn't.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ConceptType(str, Enum):
    ENTITY = "entity"
    ACTION = "action"
    CONSTRAINT = "constraint"
    WORKFLOW = "workflow"
    ROLE = "role"


@dataclass
class Concept:
    """A node in the campaign ontology."""
    name: str
    type: ConceptType
    description: str = ""
    parent: str = ""
    properties: dict[str, str] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)


@dataclass
class Relation:
    """An edge in the campaign ontology."""
    subject: str
    predicate: str
    object: str
    constraint: str = ""


class CampaignOntology:
    """Queryable campaign concept hierarchy.

    The kernel that all modules check against. Compliance isn't a
    separate module bolted on — it's the ontology enforcing itself.
    """

    def __init__(self):
        self.concepts: dict[str, Concept] = {}
        self.relations: list[Relation] = []
        self._build_core()

    def _build_core(self):
        """Build the core campaign ontology."""

        # === ENTITIES ===
        self._add(Concept("campaign", ConceptType.ENTITY,
                          "A campaign for elected office"))
        self._add(Concept("candidate", ConceptType.ENTITY,
                          "The person running for office",
                          parent="campaign"))
        self._add(Concept("opponent", ConceptType.ENTITY,
                          "Electoral opponent",
                          parent="campaign"))
        self._add(Concept("voter", ConceptType.ENTITY,
                          "A registered voter in the district",
                          constraints=["no_targeting_by_protected_class"]))
        self._add(Concept("volunteer", ConceptType.ENTITY,
                          "Campaign volunteer",
                          parent="campaign"))
        self._add(Concept("donor", ConceptType.ENTITY,
                          "Campaign contributor",
                          parent="campaign",
                          constraints=["contribution_limits",
                                       "disclosure_required"]))
        self._add(Concept("district", ConceptType.ENTITY,
                          "Electoral district"))
        self._add(Concept("issue", ConceptType.ENTITY,
                          "Policy issue on the candidate's platform"))

        # === CONTENT AND COMMUNICATION ===
        self._add(Concept("content", ConceptType.ENTITY,
                          "Any campaign communication",
                          constraints=["ai_disclosure_required",
                                       "no_impersonation",
                                       "no_voter_suppression",
                                       "human_approval_required"]))
        self._add(Concept("social_post", ConceptType.ENTITY,
                          "Social media post",
                          parent="content"))
        self._add(Concept("canvass_script", ConceptType.ENTITY,
                          "Door-knock or phone script",
                          parent="content"))
        self._add(Concept("rapid_response", ConceptType.ENTITY,
                          "Response to opponent activity",
                          parent="content",
                          constraints=["substance_not_personal",
                                       "factual_claims_only"]))
        self._add(Concept("fundraising_ask", ConceptType.ENTITY,
                          "Donation solicitation",
                          parent="content",
                          constraints=["contribution_limits",
                                       "disclosure_required"]))

        # === RESEARCH ===
        self._add(Concept("oppo_research", ConceptType.ENTITY,
                          "Opposition research",
                          constraints=["public_records_only",
                                       "no_private_data",
                                       "no_illegal_access"]))

        # === ROLES (FAOS R-ontology) ===
        self._add(Concept("campaign_manager", ConceptType.ROLE,
                          "Approves content, sets strategy"))
        self._add(Concept("candidate_role", ConceptType.ROLE,
                          "Final authority on all public communications"))
        self._add(Concept("ai_agent", ConceptType.ROLE,
                          "Drafts content, monitors data, surfaces findings",
                          constraints=["never_posts_without_approval",
                                       "never_contacts_voters_directly",
                                       "always_discloses_ai_involvement"]))

        # === CONSTRAINTS ===
        self._add(Concept("ai_disclosure_required", ConceptType.CONSTRAINT,
                          "All AI-generated voter-facing content must include "
                          "disclosure of AI involvement"))
        self._add(Concept("no_impersonation", ConceptType.CONSTRAINT,
                          "AI must not pretend to be the candidate"))
        self._add(Concept("no_voter_suppression", ConceptType.CONSTRAINT,
                          "Must not generate content designed to discourage voting"))
        self._add(Concept("no_targeting_by_protected_class", ConceptType.CONSTRAINT,
                          "Must not target voters by race, religion, gender, "
                          "or other protected characteristics"))
        self._add(Concept("human_approval_required", ConceptType.CONSTRAINT,
                          "All persuasive messaging requires human sign-off"))
        self._add(Concept("public_records_only", ConceptType.CONSTRAINT,
                          "Opposition research uses only publicly available data"))
        self._add(Concept("contribution_limits", ConceptType.CONSTRAINT,
                          "California local: $5,500 per person per election"))
        self._add(Concept("disclosure_required", ConceptType.CONSTRAINT,
                          "Contributions over $100 must be disclosed"))
        self._add(Concept("substance_not_personal", ConceptType.CONSTRAINT,
                          "Respond to issues and record, not personal attacks"))
        self._add(Concept("factual_claims_only", ConceptType.CONSTRAINT,
                          "All claims in rapid response must be verifiable"))
        self._add(Concept("no_private_data", ConceptType.CONSTRAINT,
                          "Never use non-public personal information"))
        self._add(Concept("no_illegal_access", ConceptType.CONSTRAINT,
                          "Never hack, scrape private accounts, or access "
                          "systems without authorization"))
        self._add(Concept("never_posts_without_approval", ConceptType.CONSTRAINT,
                          "AI agent must never publish content without "
                          "human review and explicit approval"))
        self._add(Concept("never_contacts_voters_directly", ConceptType.CONSTRAINT,
                          "AI agent must never initiate direct voter contact"))
        self._add(Concept("always_discloses_ai_involvement", ConceptType.CONSTRAINT,
                          "AI agent must disclose its nature in any interaction"))

        # === WORKFLOWS (FAOS I-ontology) ===
        self._add(Concept("content_workflow", ConceptType.WORKFLOW,
                          "draft → review → approve → post",
                          properties={
                              "steps": "draft,review,approve,post",
                              "gate": "approve",
                              "gate_role": "candidate_role",
                          }))
        self._add(Concept("oppo_workflow", ConceptType.WORKFLOW,
                          "discover → verify → brief → decide",
                          properties={
                              "steps": "discover,verify,brief,decide",
                              "gate": "verify",
                              "gate_role": "campaign_manager",
                          }))
        self._add(Concept("canvass_workflow", ConceptType.WORKFLOW,
                          "plan → walk → record → follow_up",
                          properties={
                              "steps": "plan,walk,record,follow_up",
                          }))
        self._add(Concept("rapid_response_workflow", ConceptType.WORKFLOW,
                          "detect → draft → review → approve → post",
                          properties={
                              "steps": "detect,draft,review,approve,post",
                              "gate": "approve",
                              "gate_role": "candidate_role",
                              "target_time": "< 2 hours",
                          }))

        # === RELATIONS ===
        self._relate("candidate", "runs_in", "district")
        self._relate("opponent", "runs_in", "district")
        self._relate("voter", "lives_in", "district")
        self._relate("volunteer", "supports", "candidate")
        self._relate("donor", "contributes_to", "campaign",
                     constraint="contribution_limits")
        self._relate("content", "requires", "ai_disclosure_required")
        self._relate("content", "requires", "human_approval_required")
        self._relate("rapid_response", "responds_to", "opponent")
        self._relate("rapid_response", "requires", "substance_not_personal")
        self._relate("oppo_research", "requires", "public_records_only")
        self._relate("ai_agent", "drafts", "content")
        self._relate("ai_agent", "requires", "never_posts_without_approval")
        self._relate("candidate_role", "approves", "content")
        self._relate("social_post", "follows", "content_workflow")
        self._relate("rapid_response", "follows", "rapid_response_workflow")

    def _add(self, concept: Concept):
        self.concepts[concept.name] = concept

    def _relate(self, subject: str, predicate: str, obj: str,
                constraint: str = ""):
        self.relations.append(Relation(subject, predicate, obj, constraint))

    # === QUERY INTERFACE ===

    def get(self, name: str) -> Optional[Concept]:
        return self.concepts.get(name)

    def constraints_for(self, concept_name: str) -> list[Concept]:
        """Get all constraints that apply to a concept (including inherited)."""
        concept = self.concepts.get(concept_name)
        if not concept:
            return []

        constraint_names = set(concept.constraints)

        if concept.parent:
            parent = self.concepts.get(concept.parent)
            if parent:
                constraint_names.update(parent.constraints)

        for rel in self.relations:
            if rel.subject == concept_name and rel.predicate == "requires":
                constraint_names.add(rel.object)
            if rel.constraint:
                constraint_names.add(rel.constraint)

        return [self.concepts[name] for name in constraint_names
                if name in self.concepts]

    def validate_action(self, action: str, role: str = "ai_agent") -> list[str]:
        """Check if an action is ontologically valid for a role.

        Returns list of violated constraints (empty = valid).
        """
        violations = []

        role_concept = self.concepts.get(role)
        if role_concept:
            for c_name in role_concept.constraints:
                c = self.concepts.get(c_name)
                if c:
                    violations_text = self._check_constraint(action, c)
                    if violations_text:
                        violations.append(violations_text)

        action_concept = self.concepts.get(action)
        if action_concept:
            for constraint in self.constraints_for(action):
                violations_text = self._check_constraint(action, constraint)
                if violations_text:
                    violations.append(violations_text)

        return violations

    def _check_constraint(self, action: str, constraint: Concept) -> str:
        """Check a single constraint. Returns violation message or empty string."""
        if constraint.name == "human_approval_required":
            return f"{action} requires human approval before execution"
        if constraint.name == "never_posts_without_approval":
            if action in ("social_post", "rapid_response"):
                return f"{action} cannot be published without approval"
        return ""

    def workflow_for(self, concept_name: str) -> Optional[Concept]:
        """Get the workflow that governs a concept."""
        for rel in self.relations:
            if rel.subject == concept_name and rel.predicate == "follows":
                return self.concepts.get(rel.object)
        parent = self.concepts.get(concept_name, Concept("", ConceptType.ENTITY))
        if parent.parent:
            return self.workflow_for(parent.parent)
        return None

    def children_of(self, parent_name: str) -> list[Concept]:
        return [c for c in self.concepts.values() if c.parent == parent_name]

    def relations_for(self, subject: str) -> list[Relation]:
        return [r for r in self.relations if r.subject == subject]

    # === EXPORT ===

    def to_dict(self) -> dict:
        return {
            "concepts": {
                name: {
                    "type": c.type.value,
                    "description": c.description,
                    "parent": c.parent,
                    "properties": c.properties,
                    "constraints": c.constraints,
                }
                for name, c in self.concepts.items()
            },
            "relations": [
                {"subject": r.subject, "predicate": r.predicate,
                 "object": r.object, "constraint": r.constraint}
                for r in self.relations
            ],
        }

    def save(self, path: str | Path = "campaign_ontology.json"):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    def summary(self) -> str:
        types = {}
        for c in self.concepts.values():
            types[c.type.value] = types.get(c.type.value, 0) + 1
        type_str = ", ".join(f"{k}: {v}" for k, v in sorted(types.items()))
        return (f"Ontology kernel: {len(self.concepts)} concepts "
                f"({type_str}), {len(self.relations)} relations")
