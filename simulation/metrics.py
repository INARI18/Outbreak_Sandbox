class MetricsCollector:
    def __init__(self):
        self.attempts: list[dict] = []

    def record_attempt(self, data: dict):
        self.attempts.append(data)

    def last_n(self, n: int) -> list[dict]:
        return self.attempts[-n:]

    def summary(self) -> dict:
        total = len(self.attempts)
        successes = sum(1 for a in self.attempts if a["success"])
        failures = total - successes

        avg_score = (
            sum(a["infection_score"] for a in self.attempts) / total
            if total > 0 else 0
        )

        return {
            "total_attempts": total,
            "successes": successes,
            "failures": failures,
            "avg_infection_score": round(avg_score, 4)
        }
