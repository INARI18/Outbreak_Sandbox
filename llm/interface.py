from llm.formatter import PromptFormatter
from llm.parsers.decision_parser import DecisionParser, DecisionParseError
from llm.parsers.mutation_parser import MutationParser, MutationParseError
from llm.prompt_context import (
    build_decision_context,
    build_mutation_context
)


class LLMInterface:
    def __init__(self, client):
        self.client = client

    def decide(self, step, network, virus, metrics):
        result = self.decide_spread(step, network, virus, metrics)

        if "error" in result:
            return None

        return result["source_node"], result["target_node"]

    def decide_spread(self, step, network, virus, metrics) -> dict:
        context = build_decision_context(
            step=step,
            network=network,
            virus=virus,
            metrics=metrics
        )

        messages = PromptFormatter.decision(context)
        raw_response = self.client.complete(messages)

        try:
            decision = DecisionParser.parse(raw_response)
        except DecisionParseError as e:
            return {
                "error": "decision_parse_failed",
                "details": str(e),
                "raw_response": raw_response
            }

        # If llm returned null for source/target == invalid decision
        if decision.get("source_node_id") is None or decision.get("target_node_id") is None:
            return {
                "error": "invalid_decision",
                "details": "LLM returned null for source or target node",
                "raw_response": raw_response
            }

        source = decision["source_node_id"]
        target = decision["target_node_id"]

        src_node = network.get_node(source)
        if not src_node:
            return {"error": "invalid_source_node"}

        if target not in src_node.connected_nodes:
            for neighbor_id in src_node.connected_nodes:
                neighbor = network.get_node(neighbor_id)
                if neighbor and not neighbor.is_infected:
                    return {
                        "source_node": source,
                        "target_node": neighbor_id,
                        "reasoning": f"fallback: original target {target} not connected; choosing neighbor {neighbor_id}"
                    }

            for node in network.infected_nodes():
                for neighbor_id in node.connected_nodes:
                    neighbor = network.get_node(neighbor_id)
                    if neighbor and not neighbor.is_infected:
                        return {
                            "source_node": node.id,
                            "target_node": neighbor_id,
                            "reasoning": f"fallback: original choice invalid; choosing {node.id}->{neighbor_id}"
                        }

            return {
                "error": "no_valid_targets",
                "details": "LLM suggested a non-connected target and no fallback available",
                "raw_response": raw_response
            }

        return {
            "source_node": source,
            "target_node": target,
            "reasoning": decision.get("reasoning", "")
        }

    # ==========================================================
    # MUTATION DECISION
    # ==========================================================
    def decide_mutation(self, virus, metrics):
        """
        Consults the LLM to decide if the virus should mutate
        and which characteristics to alter.
        """

        context = build_mutation_context(
            virus=virus,
            metrics_summary=metrics.summary(),
            recent_attempts=metrics.last_n(10)
        )

        messages = PromptFormatter.mutation(context)
        raw_response = self.client.complete(messages)

        try:
            return MutationParser.parse(raw_response)
        except MutationParseError as e:
            return {
                "error": "mutation_parse_failed",
                "details": str(e),
                "raw_response": raw_response
            }
