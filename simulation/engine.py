import random

from models.virus import Virus
from models.node import Node
from models.network import Network
from models.enums import AttackStrategy
from simulation.metrics import MetricsCollector
from simulation.stop_conditions import check_stop
from simulation.propagation import PropagationSystem
from simulation.mutation import (
    MutationTrigger,
)


class SimulationEngine:
    def __init__(
        self,
        network: Network,
        virus: Virus,
        llm_interface=None,
        max_steps: int = 50
    ):
        self.network = network
        self.virus = virus
        self.max_steps = max_steps
        self.current_step = 0
        self.metrics = MetricsCollector()
        self.history = []  # Stores full state snapshots per step
        self.llm = llm_interface
        self.mutation_strategy = None

        if self.llm:
             from simulation.llm_mutation_strategy import LLMMutationStrategy
             self.mutation_strategy = LLMMutationStrategy(self.llm)

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
                strategy=decision.get("strategy", AttackStrategy.EXPLOIT)
            )

            result["llm_reasoning"] = decision.get("reasoning", "")


    # single step:
    def step(self, source_node_id=None, target_node_id=None, strategy: str = AttackStrategy.EXPLOIT) -> dict:
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
                return {
                    "step": self.current_step,
                    "error": "llm_exception",
                    "llm_reasoning": f"LLM call raised exception: {e}"
                }

            if not decision or "error" in decision:
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
            strat = decision.get("strategy", AttackStrategy.EXPLOIT)

            result = self._execute_primitive_step(source_id, target_id, strat)
            result["llm_reasoning"] = decision.get("reasoning", "")
            return result
        
        return self._execute_primitive_step(source_node_id, target_node_id, strategy)

    def _execute_primitive_step(self, source_node_id: str, target_node_id: str, strategy: str = AttackStrategy.EXPLOIT) -> dict:
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

        
        # ========= MUTATION =========
        if MutationTrigger.should_mutate(self.virus):
            self.try_mutate()
            step_result["mutated"] = True

        self._take_snapshot()
        self.current_step += 1
        return step_result
        
    def try_mutate(self):
         context = {
             "metrics_obj": self.metrics,
             "step": self.current_step
         }
         
         if hasattr(self, 'mutation_strategy') and self.mutation_strategy:
             new_chars = self.mutation_strategy.mutate(self.virus, context)
             self.virus.mutate(new_chars)


    def try_infect(self, node: Node, strategy: str) -> dict:
        """
        Attempts to infect a target node using the propagation system.
        If it fails and is detected, the node increases its defense.
        """
        result = PropagationSystem.attempt_infection(self.virus, node, strategy)
        
        if not result["success"] and result.get("detected", False):
            old_sec = node.security_level
            new_sec = min(0.99, old_sec + 0.15)
            node.security_level = new_sec
            
            result["defense_boost"] = round(new_sec - old_sec, 2)
            result["msg"] = "Attack blocked and detected! Security patch applied."

        if "infection_score" in result:
             self.metrics.record_attempt(result)
             
        return result


