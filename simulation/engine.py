import random

from models.virus import Virus
from models.node import Node
from models.network import Network
from simulation.metrics import MetricsCollector
from simulation.stop_conditions import check_stop
from simulation.propagation import PropagationSystem
from simulation.mutation import (
    MutationTrigger,
    MutationContextBuilder
)


class SimulationEngine:
    def __init__(
        self,
        network: Network,
        virus: Virus,
        max_steps: int = 50
    ):
        self.network = network
        self.virus = virus
        self.max_steps = max_steps
        self.current_step = 0
        self.metrics = MetricsCollector()
        self.history = []  # Stores full state snapshots per step
        self.llm = None
        self.mutation_strategy = None

    def attach_llm(self, llm_interface):
        self.llm = llm_interface
        if llm_interface:
             from simulation.llm_mutation_strategy import LLMMutationStrategy
             self.mutation_strategy = LLMMutationStrategy(llm_interface)

    def _take_snapshot(self):
        nodes_state = []
        infected_count = 0
        quarantined_count = 0
        healthy_count = 0

        for node in self.network.nodes.values():
            nodes_state.append({
                "id": node.id,
                "status": node.status,
                "type": node.type
            })
            if node.status == "infected":
                infected_count += 1
            elif node.status == "quarantined":
                quarantined_count += 1
            else:
                healthy_count += 1

        self.history.append({
            "step": self.current_step,
            "stats": {
                "infected": infected_count,
                "quarantined": quarantined_count,
                "healthy": healthy_count
            },
            "nodes_snapshot": nodes_state
        })

    def run(self, llm_interface):
        if self.current_step == 0:
            self._take_snapshot()

        while True:
            should_stop, reason = check_stop(self)
            if should_stop:
                print(f"Stopping simulation: {reason}")
                break

            decision = llm_interface.decide_spread(
                step=self.current_step,
                network=self.network,
                virus=self.virus,
                metrics=self.metrics
            )

            if not decision or "error" in decision:
                print(f"[STEP {self.current_step}] LLM decision failed:", decision)
                break

            result = self.step(
                source_node_id=decision["source_node"],
                target_node_id=decision["target_node"],
                strategy=decision.get("strategy", "exploit")
            )

            # attach LLM reasoning to the step result for visibility
            result["llm_reasoning"] = decision.get("reasoning", "")
             
            # Callback or Logging hook could be here
            # print(result) -> Removed for cleaner CLI/UI usage


    # =========================
    # SINGLE STEP
    # =========================
    def step(self, source_node_id=None, target_node_id=None, strategy: str = "exploit") -> dict:
        """
        Executes a single simulation step.
        If source/target are not provided, consults the attached LLM.
        """
        if source_node_id is None and target_node_id is None:
            if not self.llm:
                return {"step": self.current_step, "error": "No LLM attached and no args provided"}
            try:
                decision = self.llm.decide_spread(
                    step=self.current_step,
                    network=self.network,
                    virus=self.virus,
                    metrics=self.metrics
                )
            except Exception as e:
                # Return structured error to the caller so UI can display it
                return {
                    "step": self.current_step,
                    "error": "llm_exception",
                    "llm_reasoning": f"LLM call raised exception: {e}"
                }

            if not decision or "error" in decision:
                # decision may be a dict containing 'error'
                if isinstance(decision, dict):
                    return {
                        "step": self.current_step,
                        "error": decision.get("error", "LLM Decision Failed"),
                        "llm_reasoning": decision.get("details", "LLM returned error.")
                    }
                return {
                    "step": self.current_step,
                    "error": "LLM Decision Failed",
                    "llm_reasoning": "LLM returned error."
                }

            source_id = decision.get("source_node")
            target_id = decision.get("target_node")
            strat = decision.get("strategy", "exploit")

            result = self._execute_primitive_step(source_id, target_id, strat)
            result["llm_reasoning"] = decision.get("reasoning", "")
            return result
        
        return self._execute_primitive_step(source_node_id, target_node_id, strategy)

    def _execute_primitive_step(self, source_node_id: str, target_node_id: str, strategy: str = "exploit") -> dict:
        """
        Internal step execution logic (without decision making).
        """
        source = self.network.get_node(source_node_id)
        target = self.network.get_node(target_node_id)

        step_result = {
            "step": self.current_step,
            "source_node": source_node_id,
            "target_node": target_node_id,
            "attempt": None,
            "mutated": False,
            "error": None
        }

        # ========= VALIDATIONS =========

        if not source:
            step_result["error"] = "invalid_source_node"
            return step_result

        if not target:
            step_result["error"] = "invalid_target_node"
            return step_result

        if not source.is_infected:
            step_result["error"] = "source_not_infected"
            return step_result

        if target.id not in source.connected_nodes:
            step_result["error"] = "target_not_connected"
            return step_result

        if target.is_infected:
            step_result["error"] = "target_already_infected"
            return step_result

        # ========= EXECUTION =========

        attempt = self.try_infect(target, strategy)
        step_result["attempt"] = attempt
        
        # Log to metrics manually since try_infect doesn't seem to pass "score" correctly yet
        # or maybe try_infect handles it? Let's check try_infect
        # Ah, try_infect below calls metrics.record_attempt. We need to enable it.
        
        # ========= MUTATION =========

        if MutationTrigger.should_mutate(self.virus):
            # print(f"🧬 MUTATION TRIGGERED at Step {self.current_step}")
            self.try_mutate()
            step_result["mutated"] = True

        self._take_snapshot()
        self.current_step += 1
        return step_result
        
    def try_mutate(self):
         """
         Executes mutation based on recent metrics.
         Uses the assigned strategy to determine the new characteristics.
         """
         # Create context wrapper including metrics object
         # Note: We pass the 'metrics object' itself because LLMMutationStrategy expects it
         # inside 'context' via .get('metrics_obj') to call interface.decide_mutation
         
         context = {
             "metrics_obj": self.metrics,
             "step": self.current_step
         }
         
         if hasattr(self, 'mutation_strategy') and self.mutation_strategy:
             new_chars = self.mutation_strategy.mutate(self.virus, context)
             self.virus.mutate(new_chars)
             # print(f"   🧬 Virus mutated! Stats: Atk={new_chars.attack_power:.1f} Stl={new_chars.stealth:.1f} Targets={new_chars.target_hosts}")

    # INFECTION
    # =========================
    def try_infect(self, node: Node, strategy: str) -> dict:
        """
        Attempts to infect a target node using the propagation system.
        If it fails and is detected, the node increases its defense.
        """
        result = PropagationSystem.attempt_infection(self.virus, node, strategy)
        
        # Defensive Reaction (Punishment for Noise)
        # If failed and detected, the Admin fixes the flaw (increases security)
        if not result["success"] and result.get("detected", False):
            old_sec = node.security_level
            # Increases defense by 15% (capped at 0.99)
            new_sec = min(0.99, old_sec + 0.15)
            node.security_level = new_sec
            
            result["defense_boost"] = round(new_sec - old_sec, 2)
            result["msg"] = "Attack blocked and detected! Security patch applied."

        # Record metrics regardless of success/fail reason
        # Only record if it was a valid attempt (e.g. not an incompatible host check only)
        # But for full metrics history, we usually record everything.
        # Based on previous code, we record the result object.
        if "infection_score" in result:
             self.metrics.record_attempt(result)
             
        return result


