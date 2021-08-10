


from proj.userInterfaces.userInterface import QuietUI
from proj.model.match import play_match
from proj.agents.randomAgent import RandomAgent
from proj.agents.MCTSAgent import UnfairMCTSAgent

# state = GameState()

# grid = state.grid

# grid.get_representation()

# state.get_representation()


def run_test():
    for t in (50,40,30,20,10):

        player1 = UnfairMCTSAgent('p1', 'UnfairMCTSAgent')
        player2 = RandomAgent('p2', 'RandomAgent')

        player1.MAX_TIME = t
        wins = play_match(1, player1, player2, QuietUI(), game_length=70, delay=0)
        # winner,_ = filter(lambda a,b: b > 0, wins.items())[0] 
        with open('results.txt', 'a') as f:
            f.write(f'time = {t}s, wins: {wins}\n')
        
        
if __name__ == '__main__':
    run_test()
    






    