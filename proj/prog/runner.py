import cProfile
import os
import pstats

from proj.agents.GUIAgent import GUIAgent
from proj.prog.match import play_match
from proj.userInterfaces.GUI import GUI
from proj.userInterfaces.userInterface import TerminalUI, QuietUI
from optparse import OptionParser


def CLI():
    
    # logging.basicConfig(filename=r"C:\Users\User\Desktop\proj_info.txt")
    """ read options from command line to instantiate match """
    usage_string = """
    USAGE:      python -m proj <options>
    """
    parser = OptionParser(usage_string)
    parser.add_option('-n', '--bestOf', dest='bestOf', type=int, default=1,
                      help='number of GAMES in match', metavar='games')
    # parser.add_option('-a', '--agents', dest='list_agents', action='store_true', default=False,
    #                   help='print a list of available agents [default: %default')
    parser.add_option('-o', '--player1', dest='player1', type=str, default='default',
                      help='class NAME of player1 agent', metavar='player')
    parser.add_option('-t', '--player2', dest='player2', type=str, default='default',
                      help='class NAME of player2 agent', metavar='player')
    parser.add_option('-u', '--ui', dest='ui', action='store_true', default=False,
                      help='enable pygame GUI', metavar='UI')
    parser.add_option('-l', '--gameLength', dest='gameLength', type=int, default=70,
                      help='how many TURNS per game', metavar='length')
    parser.add_option('-q', '--quiet', dest='quiet', action='store_true', default=False,
                      help='quiet setting will minimise board displays from the terminal UI ')
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

    
    Player1 = GUIAgent if options.player1 == 'default' else load_agent(options.player1)  # class object
    Player2 = GUIAgent if options.player2 == 'default' else load_agent(options.player2)  # class object
    
    if GUIAgent in (Player1, Player2) or options.ui: 
        ui = GUI()
    else: 
        ui = QuietUI() if options.quiet else TerminalUI()
    
    args1,args2 = get_params(options.parameters)


    player1 = Player1('player1', Player1.__name__, **args1)
    player2 = Player2('player2', Player2.__name__, **args2)
    
    for player in (player1,player2):
        if isinstance(player, GUIAgent):
            player.set_gui(ui)
              
    profiler = cProfile.Profile()
    profiler.enable()
    # cProfile.run('play_match(best_of, player1, player2, ui, delay)')
    wins = play_match(total_games=best_of, player1=player1,
                      player2=player2, ui=ui, game_length=game_length)
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
    if parameter_string == '': return {},{}
    agent1params = agent2params = {}
    parameter_string.strip()
    params = parameter_string.split(';')
    for param in params:
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
