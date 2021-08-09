
import time
from proj.model.state import GameState

# state = GameState()

# grid = state.grid

# grid.get_representation()

# state.get_representation()


state = GameState()
starttime = time.time()
for _ in range(10_000):
    state.valid_actions()
length = time.time()-starttime
print(length)





    