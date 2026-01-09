from PySide6.QtCore import QThread, Signal
from infra.factories import SimulationFactory

class EngineLoaderThread(QThread):
    finished_loading = Signal(object) # will carry the Engine instance
    error_occurred = Signal(str)

    def __init__(self, topo_key, n_count, v_name, mode, seed):
        super().__init__()
        self.topo_key = topo_key
        self.n_count = n_count
        self.v_name = v_name
        self.mode = mode
        self.seed = seed

    def run(self):
        try:
            # Heavy operation (loading model inside factory)
            engine = SimulationFactory.build_engine(
                topology_key=self.topo_key,
                node_count=self.n_count,
                virus_name=self.v_name,
                execution_mode=self.mode,
                seed=self.seed
            )
            self.finished_loading.emit(engine)
        except Exception as e:
            self.error_occurred.emit(str(e))
