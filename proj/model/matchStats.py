from dataclasses import dataclass
@dataclass
class MatchStats:

    """
    This class is used to store the following stats about a match which is then saved to a designated text file:

    - total games (int)
    - total moves made for each player
    - total nodes searched for each player (int)
    - time per move for each player (float)
    - agent type for each player
    - wins for each player as each type
    - total score for each player
    """
    
    total_games: int = 0
    player1: str = 0 
    player2: str = 0 
    
    total_time_player1: float = 0 
    total_time_player2: float = 0 
    
    total_moves_player1: int = 0 
    total_moves_player2: int = 0 

    total_score_player1: int = 0
    total_score_player2: int = 0

    total_nodes_searched_player1: int = 0
    total_nodes_searched_player2: int = 0
    
    dwarf_wins_player1: int = 0
    troll_wins_player1: int = 0
    dwarf_wins_player2: int = 0
    troll_wins_player2: int = 0
    
    

    def __init__(self, total_games:int, player1:str, player2:str, ) -> None:
        self.total_games = total_games
        self.player1 = player1
        self.player2 = player2

    def update_stats(self, player_name:str, add_time=0, add_nodes=0, add_score=0, 
                     add_wins_dwarf=0, add_wins_troll=0, add_move=0):
        if player_name == 'player1':
            self.__update_player1(add_time, add_nodes, add_score, add_wins_dwarf, add_wins_troll, add_move)
        elif player_name == 'player2': 
            self.__update_player2(add_time, add_nodes, add_score, add_wins_dwarf, add_wins_troll, add_move)
    
    def __update_player1(self, add_time, add_nodes, add_score, add_wins_dwarf, add_wins_troll, add_move):
        self.total_time_player1 += add_time
        self.total_nodes_searched_player1 += add_nodes
        self.total_score_player1 += add_score
        self.dwarf_wins_player1 += add_wins_dwarf
        self.troll_wins_player1 += add_wins_troll
        self.total_moves_player1 += add_move
    
    def __update_player2(self, add_time, add_nodes, add_score, add_wins_dwarf, add_wins_troll, add_move):
        self.total_time_player2 += add_time
        self.total_nodes_searched_player2 += add_nodes
        self.total_score_player2 += add_score
        self.dwarf_wins_player2 += add_wins_dwarf
        self.troll_wins_player2 += add_wins_troll
        self.total_moves_player2 += add_move
        
    @property
    def avg_nodes_player1(self) -> float:
        return round(self.total_nodes_searched_player1 / self.total_moves_player1,2)

    @property
    def avg_nodes_player2(self) -> float:
        return round(self.total_nodes_searched_player2 / self.total_moves_player2,2)

    @property
    def avg_move_time_player1(self) -> float:
        return round(self.total_time_player1 / self.total_moves_player1,2)
    
    @property
    def avg_move_time_player2(self) -> float:
        return round(self.total_time_player2 / self.total_moves_player2,2)

    def __repr__(self) -> str:
        ret_strings = [
            f'total games played= {self.total_games}',
            f'{self.player1} {self.total_score_player1} vs {self.total_score_player2} {self.player2}',
            f'\n{self.player1}\n',
            f'\tavg move time= {self.avg_move_time_player1}s, avg nodes per turn= {self.avg_nodes_player1}\n'
            f'\tdwarf wins= {self.dwarf_wins_player1}, troll_wins={self.troll_wins_player1}',  
            f'\n{self.player2}\n',
            f'\tavg move time= {self.avg_move_time_player2}s, avg nodes per turn= {self.avg_nodes_player2}\n'
            f'\tdwarf wins= {self.dwarf_wins_player2}, troll_wins={self.troll_wins_player2}'  
        ]
        return '\n'.join(ret_strings)