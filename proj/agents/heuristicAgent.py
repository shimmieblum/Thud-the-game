
from ..agents.template import ThudAgentTemplate
from ..model.state import GameState, Action
from ..model.enums import Piece

import random
import math

class HeuristicAgent(ThudAgentTemplate):
    
    '''
    
    The goal for this agent is to chose a better move based on domain knowlege 
    Using this knowlege, a heuristic value for each state will be calculated 
    and this will be used to chose the next move.
    
    In general, the best tactic for dwarves is to group together and the best tactic 
    for trolls is to minimise the dwarves groupings and to remain spread out.
    
    Fo find a value for the dwarves we will:
        a) identify how many clusters they are organised in 
        b) identify how cohesive the clusters are
    
    For the trolls, the value will be the opposite
    
    Additionally there is always a value in capturing opponents pieces and avoiding 
    capture.
    
    This will be incorporated in the heuristic of each piece type.
    
    '''    
    'asdf'
    def __init__(self, name, agentClassName) -> None:
        
        super().__init__(name, agentClassName)
        
    def act(self, state: GameState, game_number:int, wins: dict) -> Action:
        subsequent_states = state.get_subsequent_states()
        turn = state.turn
        
        _, best_action = max(subsequent_states, key=lambda a: self.calculate_heuristic(state, a[0], turn))
        
        return best_action
        
        
        
    def calculate_heuristic(self, previous_state, state, turn) -> float:
        '''
        Calculates a heuristic value for the state which is the result of a given action 
        
        @param state: the resultant state of an action
        @param turn: which side this player is controlling
        '''
        if turn == Piece.DWARF: return self.calculate_dwarf_heuristic(previous_state, state )
        else: return self.calculate_troll_heuristic(previous_state, state)
        
    def calculate_troll_heuristic(self, prev_state, state): 
        dwarf_num_change = len(prev_state.dwarves()) -  len(state.dwarves())
        s, cluster = self.get_best_clustering(state.dwarves())
        return dwarf_num_change - s
        
        
        
    def silhouette(self, clusters):
        num_points = 0
        silhouette = 0
        for mean, cluster in clusters.items():
            other_clusters = list(clusters.keys())
            other_clusters.remove(mean)
            if len(other_clusters) == 0: ... 
            for i in cluster:
                num_points +=1
                nearest_mean = min((mean for mean in other_clusters), key= lambda mean: self.euclidean_distance(i,mean))
                silhouette += self.silhouette_of_point(i, cluster, clusters[nearest_mean])
        return silhouette / num_points 
        
        
    def calculate_dwarf_heuristic(self, previous_state:GameState, state:GameState) -> float:
        
        change_in_num = len(previous_state.trolls()) - len(state.trolls())
        dwarves = state.dwarves()
        s, best_clustering = self.get_best_clustering(dwarves)
        return change_in_num + s
    
    
    def get_best_clustering(self, points) -> 'tuple[float, dict]':
        ''' 
        find the best clustering for this set of points based on different values of n and the silhouette of the clustering
        @param points: the set of points to be placed in clusters
        @return: the silhouette value and the clusters as a dictionary
        '''
        best_silhouette = -2
        best_clusters = {}
        for n in range(2,len(points)//2):
            clusters = self.clusters(points,n)
            this_silhouette = self.silhouette(clusters)
            if this_silhouette > best_silhouette:
                best_silhouette = this_silhouette
                best_clusters = clusters
        return best_silhouette, best_clusters
           
    def cohesiveness(self, clustering):    
        # calculate cohesiveness of each cluster
        # return values based on:
            # 1) size of clusters
            # 2) number of clusters
            # 3) cohesiveness of clusters 
        
        value = ... # TODO: calculate value
        return value
        
         

        
    def calculate_troll_cohesiveness(self, state:GameState):
        trolls = state.trolls()
        # trolls will be considered a single cluster, calculate cohesiveness 
        # by finding the sum of squares of all the trolls
        mx,my = sum(i[0] for i in trolls)/len(trolls), sum(i[1] for i in trolls)/len(trolls)
        sx,sy = 0,0
        for x,y in trolls:
            sx += (x-mx) ** 2
            sy += (y-my) ** 2
            
        
    def silhouette_of_point(self, i, cluster, nearest_cluster):
        '''
        Calculate the silhouette coefficient of point i for the cluster it is currently asssigned to
        This will be used to identify the best cluster to assign
        
        @param i: the point in discussion
        @param cluster: the cluster i belongs to 
        @param nearest_cluster: the next closest cluster
        
        @return: silhouette value of i
        '''
        
        cluster.remove(i)
        # a(i) => avg distance to other points in cluster
        a = 0.01 if len(cluster) < 1 else sum(map(lambda b: self.euclidean_distance(i, b) , cluster)) / len(cluster)
        # b(i) => avg distance to opoints in nearest cluster 
        b = 10_000 if len(nearest_cluster) < 1 else sum(map(lambda b: self.euclidean_distance(i, b), nearest_cluster)) / len(nearest_cluster)
        # s(i) => silhouette coefficient
        s = (b-a) / max(a,b)
        return round(s,2)
    
    def euclidean_distance(self, a,b):
        '''
        @param a: first point
        @param b: second point
        @return: euclidean distance between a & b'''
        if len(a) != len(b): raise Exception(f'points {a} and {b} are of different sizes')
        d = len(a)
        result =  math.sqrt(sum( (a[i]-b[i])**2 for i in range(0,d)))
        return round(result,2)

    def mean(self, points):
        '''
        @return: the mean of the points in the set
        '''
        return tuple(round(sum(x)/len(x),2) for x in zip(*points))
        
    def clusters(self, points, n)-> dict:
        '''
        identify n clusters in the set of points
        @param points: list of points to cluster
        @param n: number of clusters to initialise with
        @return dictionary of {centroid -> list of associated points}  
        '''
        lbx,lby = min(a[0] for a in points), min(a[1] for a in points)
        ubx, uby = max(a[0] for a in points), max(a[1] for a in points)
        centres = random.choices(points, k=n)
        prev_centres = None
        while prev_centres != centres:
            clusters = {centre:[] for centre in centres}
            for point in points: 
                centre = min(centres, key=lambda a: self.euclidean_distance(point,a))
                clusters[centre].append(point)
            clusters = {self.mean(points): points for points in clusters.values()}
            prev_centres = clusters.keys()
            if len(clusters) < n: 
                for _ in range(0, n-len(clusters)): 
                    mean = random.randint(lbx,ubx), random.randint(lby, uby)
                    clusters[mean] = []
            centres = clusters.keys()
        return clusters
    
    