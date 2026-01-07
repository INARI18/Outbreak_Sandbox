import random

class DeterministicPolicy:
    """
    Manages the entropy source for the simulation.
    If a seed is provided (Deterministic Mode), it uses a seeded generator.
    Otherwise (Stochastic Mode), it relies on system entropy.
    """
    _instance = None
    
    def __init__(self):
        self._seed = None
        self._rng = random.Random()
        self._is_deterministic = False

    @staticmethod
    def get():
        if DeterministicPolicy._instance is None:
            DeterministicPolicy._instance = DeterministicPolicy()
        return DeterministicPolicy._instance

    def configure(self, seed=None):
        """
        Configure the policy.
        :param seed: If provided, enables deterministic mode with this seed.
                     If None, enables stochastic mode.
        """
        if seed is not None:
            try:
                s = int(seed)
                self._seed = s
                self._is_deterministic = True
                self._rng = random.Random(s)
            except ValueError:
                # If seed is string but not integer convertible, use hash or valid string seed
                self._seed = seed
                self._is_deterministic = True
                self._rng = random.Random(seed)
        else:
            self._seed = None
            self._is_deterministic = False
            self._rng = random.Random() # System time/entropy

    @property
    def is_deterministic(self) -> bool:
        return self._is_deterministic

    # --- Random Primitives ---

    def random(self) -> float:
        """Return the next random floating point number in the range [0.0, 1.0)."""
        return self._rng.random()

    def uniform(self, a: float, b: float) -> float:
        """Return a random floating point number N such that a <= N <= b."""
        return self._rng.uniform(a, b)

    def choice(self, seq):
        """Return a random element from the non-empty sequence seq."""
        return self._rng.choice(seq)
    
    def shuffle(self, x):
        """Shuffle list x in place, and return None."""
        self._rng.shuffle(x)

    def randint(self, a: int, b: int) -> int:
        """Return random integer in range [a, b], including both end points."""
        return self._rng.randint(a, b)
