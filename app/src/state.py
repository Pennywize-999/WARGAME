import time
from enum import IntEnum
from src.database.models import (
    get_state,
    start_simulation as db_start_sim,
    abort_simulation as db_abort_sim,
    get_defcon
)

class DefconLevel(IntEnum):
    DEFCON_1 = 1
    DEFCON_2 = 2
    DEFCON_3 = 3
    DEFCON_4 = 4
    DEFCON_5 = 5

class GameState:
    """
    Compatibility wrapper delegating exclusively to SQLite models.
    The single authoritative timer source is SQLite countdown_deadline.
    """
    @property
    def defcon(self) -> int:
        return get_defcon()

    @property
    def countdown_active(self) -> bool:
        st = get_state()
        return bool(st and st.get('simulation_active', 0))

    @property
    def simulation_started(self) -> bool:
        return self.countdown_active

    def start_simulation(self) -> bool:
        return db_start_sim()

    def abort_simulation(self) -> bool:
        return db_abort_sim()

    def get_remaining_time(self) -> int:
        st = get_state()
        if not st or not st.get('simulation_active', 0):
            return 0
        deadline = st.get('countdown_deadline', 0)
        remaining = deadline - int(time.time())
        return max(0, remaining)

# Global singleton for compatibility
state = GameState()
