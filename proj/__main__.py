import cProfile
import logging
import os
import pstats
import random

from proj.agents.GUIAgent import GUIAgent
from .agents.randomAgent import BetterRandomAgent
from .model.match import play_match
from .userInterfaces.GUI import GUI
from .userInterfaces.userInterface import TerminalUI, QuietUI


def main():
    # logging.basicConfig(filename=r"C:\Users\User\Desktop\proj_info.txt")
    """ read options from command line to instantiate match """
    from optparse import OptionParser
    usage_string = """
    USAGE:      python -m proj <options>
    """
    parser = OptionParser(usage_string)
    parser.add_option('-n', '--bestOf', dest='bestOf', type=int,
                      help='max number of GAMES in match (best of x games)', metavar='games')
    # parser.add_option('-a', '--agents', dest='list_agents', action='store_true', default=False,
    #                   help='print a list of available agents [default: %default')
    parser.add_option('-o', '--player1', dest='player1', type=str, default='default',
                      help='class NAME of player1 agent', metavar='player')
    parser.add_option('-t', '--player2', dest='player2', type=str, default='default',
                      help='class NAME of player2 agent', metavar='player')
    parser.add_option('-u', '--ui', dest='ui', action='store_true', default=False,
                      help='use GUI or not', metavar='UI')
    parser.add_option('-l', '--gameLength', dest='gameLength', type=int,
                      help='how many TURNS per game', metavar='length')
    parser.add_option('-d', '--delay', dest='delay', type=int,
                      help='min time per move (s) [default: %default]', default=0)
    parser.add_option('-q', '--quit', dest='quiet', action='store_true', default=False,
                      help='quit setting will disable all print outs')
    parser.add_option('-p', '--parameters', dest='parameters', type=str, default='',
                      help=("Add parameters for agents. agent 1 using '1: x=1 ...' & agent 2 using '2: y=2 ... '. Seperate agents with ';'."
                            + " Seperate parameters with ','. Please note: only numbers can be input with this option"))
    options, other = parser.parse_args()
    if len(other) != 0:
        raise Exception(f"""CLI can't understand {str(other)}""")
    # elif options.list_agents:
    #     list_agents()
    #     return

    best_of = options.bestOf
    game_length = options.gameLength


    # agent1param = agent2param = ''
    # params = str(options.parameters).split(',')
    # for param_set in params:
    #     details = param_set.split(':')
    #     if details[0].trim() == '2':
    #         agent1param = details[1]
    #     elif details[0].trim() == '1':
    #         agent2param = details[1]
    Player1 = Player2 = None

    if options.player1 == 'default' and options.player2 == 'default':
        choice = random.choice((1, 2))
        Player1 = BetterRandomAgent if choice == 1 else GUIAgent
        Player2 = GUIAgent if choice == 1 else BetterRandomAgent
    elif options.player1 == 'default':
        Player1 = GUIAgent
        Player2 = load_agent(options.player2)
    elif options.player2 == 'default':
        Player1 = load_agent(options.player1)  # class object
        Player2 = GUIAgent
    else:
        Player1 = load_agent(options.player1)  # class object
        Player2 = load_agent(options.player2)  # class object
    
    if GUIAgent in (Player1, Player2): ui = GUI()
    else: ui = QuietUI() if options.quiet else GUI() if options.ui else TerminalUI()

    args1,args2 = get_params(options.parameters)

    player1 = Player1('player1', Player1.__name__, **args1)
    player2 = Player2('player2', Player2.__name__, **args2)
    
    for player in (player1,player2):
        if isinstance(player, GUIAgent):
            player.set_gui(ui)
              

    delay = options.delay
    profiler = cProfile.Profile()
    profiler.enable()
    # cProfile.run('play_match(best_of, player1, player2, ui, delay)')
    wins = play_match(total_games=best_of, player1=player1,
                      player2=player2, ui=ui, game_length=game_length, delay=delay)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats()
    print(f'winner is: {max(wins, key=wins.get)}')


def list_agents():
    print("""Here's a list of agents:""")
    # TODO learn how to list all classes ending in 'Agents' in the proj.agents package

    pass


def load_agent(agentClassName: str):
    """
    load agent from agents module and return the class object
    @param agentClassName: the class to be used as the agent 
    @return: the agent class object to be instantiated
    """
    # s is name of the class
    prefix = 'proj.agents'
    # path_prefix = 'C:\Users\User\Desktop\proj_folder\proj\agents'
    for filename in os.listdir(r'proj\agents'):
        # print(filename)
        mod = f'{prefix}.{filename}'
        try:
            if mod.endswith('.py'):
                full_import_statement = f'{mod[:-3]}.{agentClassName}'
                parts = full_import_statement.split('.')
                module = ".".join(parts[:-1])
                m = __import__(module)
                for comp in parts[1:]:
                    m = getattr(m, comp)
                return m
        except AttributeError:
            continue
    raise Exception(f'No agent name {agentClassName} found in {prefix} module')


def get_params(parameter_string):
    # print(parameter_string)
    if parameter_string == '': return {},{}
    agent1params = agent2params = {}
    parameter_string.strip()
    params = parameter_string.split(';')
    # print(params)
    for param in params:
        # param = param.strip()
        split_params = param.split(':')
        if split_params[0].replace(' ', '') == '1':
            agent1params = string_to_kwargs(split_params[1])
        elif split_params[0].replace(' ', '') == '2':
            agent2params = string_to_kwargs(split_params[1])
    
    return agent1params, agent2params
    
def string_to_kwargs(string):
    kwargs = {}
    if string == '': return kwargs
    params = string.split(',')
    for param in params:
        name,p = tuple(param.split('='))
        name = name.strip()
        p = p.strip()
        kwargs[name] = float(p)
    return kwargs


if __name__ == '__main__':
    main()
