""" Classes for defining bitstring optimization problems.

    Author: Genevieve Hayes <ghayes17@gmail.com>
    License: 3-clause BSD license.
"""

import numpy as np
from sklearn.metrics import mutual_info_score
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree, depth_first_tree

class BitString: 
    """Base class for bitstring optimisation problems."""
    
    def __init__(self, length, fitness_fn):  
        """Initialize BitString object.
    
        Args:
        length: int. Length of bitstring to be used in problem
        fitness_fn: fitness function object. Object to implement fitness function 
        for optimization.
           
        Returns:
        None
        """
        self.length = length
        self.state = np.array([0]*self.length)
        self.neighbors = []
        self.fitness_fn = fitness_fn
        self.fitness = 0
        
    def reset(self):
        """Set the current bitstring to a random value and get its fitness
        
        Args:
        None
           
        Returns:
        None
        """
        self.state = np.random.randint(0, 2, self.length)
        self.fitness = self.calculate_fitness(self.state)
    
    def get_length(self):
        """ Return the bitstring length.
        
        Args: 
        None
        
        Returns:
        length: int. Length of bitstring.
        """
        length = self.length
        return length
    
    def get_fitness(self):
        """ Return the fitness of the current bitstring.
        
        Args:
        None
           
        Returns:
        fitness: float. Fitness value of current bitstring.
        """
        fitness = self.fitness
        
        return fitness
        
    def get_state(self):
        """ Return the current bitstring
        
        Args:
        None
           
        Returns:
        state: array. Current bitstring value.
        """
        state = self.state
        
        return state
        
    def set_state(self, new_bitstring):
        """ Change the current bitstring to a specified value and get its fitness
        
        Args:
        new_bitstring: array. New bitstring value.
           
        Returns:
        None
        """
        self.state = new_bitstring
        self.fitness = self.calculate_fitness(self.state)        
    
    def calculate_fitness(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        fitness = self.fitness_fn.evaluate(bitstring)
        
        return fitness
                 
    def find_neighbors(self):
        """Find all neighbors of the current bitstring
        
        Args:
        None
           
        Returns:
        None
        """
        self.neighbors = []
        
        for i in range(self.length):
            neighbor = np.copy(self.state)
            neighbor[i] = np.abs(neighbor[i] - 1)
            self.neighbors.append(neighbor)

    def best_neighbor(self):
        """Return the best neighbor of current bitstring
        
        Args:
        None
           
        Returns:
        best: array. Bitstring defining best neighbor.
        """
        fitness_list = []
        
        for n in self.neighbors:
            fitness = self.fitness_fn.evaluate(n)
            fitness_list.append(fitness)

        best = self.neighbors[np.argmax(fitness_list)]
        
        return best 
    
    def random_neighbor(self):
        """Return random neighbor of current bitstring
        
        Args:
        None
           
        Returns:
        neighbor: array. Bitstring of random neighbor.
        """
        neighbor = np.copy(self.state)
        i = np.random.randint(0, self.length)
        neighbor[i] = np.abs(neighbor[i] - 1)
        
        return neighbor

class Genetic(BitString):
    """Child class for solving bitstring optimisation problems using a genetic algorithm."""
    
    def __init__(self, length, fitness_fn):  
        """Initialize Genetic object.
    
        Args:
        length: int. Length of bitstring to be used in problem
        fitness_fn: fitness function object. Object to implement fitness function 
        for optimization.
           
        Returns:
        None
        """
        BitString.__init__(self, length, fitness_fn)
        self.population = []
        self.pop_fitness = []
        self.probs = []
    
    def random(self):
        """Return a random bitstring
        
        Args:
        None
           
        Returns:
        state: array. Randomly generated bitstring.
        """
        state = np.random.randint(0, 2, self.length)
        
        return state       
       
    def create_population(self, pop_size):
        """Create a population of random bitstrings
        
        Args:
        pop_size: int. Size of population to be created.
           
        Returns:
        None
        """
        population = []
        pop_fitness = []
        
        for i in range(pop_size):
            state = self.random()
            fitness = self.calculate_fitness(state)
            
            population.append(state)
            pop_fitness.append(fitness)
        
        self.population = np.array(population)
        self.pop_fitness = np.array(pop_fitness)
        
    def calculate_probs(self):
        """Calculate the probability of each member of the population reproducing.
        
        Args:
        None
           
        Returns:
        None
        """
        self.probs = self.pop_fitness/np.sum(self.pop_fitness)
    
    def get_population(self):
        """ Return the current population
        
        Args:
        None
           
        Returns:
        population: array. Numpy array containing current population.
        """
        population = self.population
        
        return population
    
    def set_population(self, new_population):
        """ Change the current population to a specified new population and get 
        the fitness of all members
        
        Args:
        new_population: array. Numpy array containing new population.
           
        Returns:
        None
        """
        self.population = new_population
        
        # Calculate fitness
        pop_fitness = []
        
        for i in range(len(self.population)):
            fitness = self.calculate_fitness(self.population[i])
            pop_fitness.append(fitness)
        
        self.pop_fitness = np.array(pop_fitness)
        
    def best_child(self):
        """Return the best bitstring in the current population.
        
        Args:
        None
           
        Returns:
        best: array. Bitstring defining best child.
        """
        best = self.population[np.argmax(self.pop_fitness)]
        
        return best

class ProbOpt(Genetic):
    """Child class for solving bitstring optimisation problems using a probabilistic
    optimization algorithm (i.e. MIMIC)."""
    
    def __init__(self, length, fitness_fn):  
        """Initialize ProbOpt object.
    
        Args:
        length: int. Length of bitstring to be used in problem
        fitness_fn: fitness function object. Object to implement fitness function 
        for optimization.
           
        Returns:
        None
        """
        Genetic.__init__(self, length, fitness_fn)
        self.keep_sample = []
        self.probs = np.zeros([2, self.length])
        self.parent = []

    def select_keep_sample(self, keep_pct):
        """Select samples with fitness in the top n percentile.
    
        Args:
        keep_pct: float. Proportion of samples to keep.
           
        Returns:
        None
        """
        # Determine threshold
        theta = np.percentile(self.pop_fitness, 100*(1 - keep_pct))

        # Determine samples for keeping
        keep_inds = np.where(self.pop_fitness >= theta)[0]
        
        # Determine sample for keeping
        self.keep_sample = self.population[keep_inds]
     
    def update_probs(self):
        """Update probability density estimates.
        
        Args:
        None
           
        Returns:
        None
        """
        # Create mutual info matrix
        mutual_info = np.zeros([self.length, self.length])
        for i in range(self.length -  1):
            for j in range(i + 1, self.length):
                mutual_info[i, j] = -1*mutual_info_score(self.keep_sample[:, i], \
                           self.keep_sample[:, j])
    
        # Find minimum spanning tree of mutual info matrix
        mst = minimum_spanning_tree(csr_matrix(mutual_info))
    
        # Convert minimum spanning tree to depth first tree with node 0 as root
        dft = depth_first_tree(csr_matrix(mst.toarray()), 0, directed=False)
        dft = dft.toarray()
        
        # Determine parent of each node
        parent = np.argmin(dft[:, 1:], axis = 0)
    
        # Get probs
        probs = np.zeros([2, self.length])
        
        if len(self.keep_sample) == 0:
            probs[:, 0] = 0
        else:
            probs[:, 0] = np.sum(self.keep_sample[:, 0])/len(self.keep_sample)
    
        for i in range(1, self.length):
            for j in range(2):
                subset = self.keep_sample[np.where(self.keep_sample[:, parent[i - 1]] == j)[0]]
                count = np.sum(subset[:, i])
                
                if len(subset) == 0:
                    probs[j, i] = 0
                else:
                    probs[j, i] = count/len(subset)
        
        # Update probs and parent
        self.probs = probs
        self.parent = parent
    
    def find_sample_order(self, parent):
        """Determine order in which to generate sample bits given parent node list
        
        Args:
        parent: list. List of nodes giving the parents of each node in bitstring tree
           
        Returns:
        sample_order: list. Order in which sample bits should be generated.
        """
        sample_order = []
        last = [0]
        parent = np.array(parent)
    
        while len(sample_order) < len(parent) + 1:
            inds = []
            
            for i in last:
                inds += list(np.where(parent == i)[0] + 1)
                
            sample_order += last
            last = inds
        
        return sample_order  
    
    def generate_new_sample(self, sample_size):
        """Generate new sample from probability density
        
        Args:
        sample_size: int. Size of sample to be generated.
           
        Returns:
        new_sample: array. Numpy array containing new sample.
        """
         # Initialize new sample matrix
        new_sample = np.zeros([sample_size, self.length])
        
        # Create random matrix
        rand_sample = np.random.uniform(size = [sample_size, self.length])
        
        # Get value of first bit in new samples
        new_sample[np.where(rand_sample[:, 0] < self.probs[0, 0])[0], 0] = 1
        
        # Get sample order
        sample_order = self.find_sample_order(self.parent)[1:]
    
        # Get values for remaining bits in new samples
        for i in sample_order:
            par_ind = self.parent[i-1]
            probs = np.zeros(sample_size)
            
            ind_0 = np.where(new_sample[:, par_ind] == 0)[0]
            ind_1 = np.where(new_sample[:, par_ind] == 1)[0]
            
            probs[ind_0] = self.probs[0, i]
            probs[ind_1] = self.probs[1, i]
            
            new_sample[np.where(rand_sample[:, i] < probs)[0], i] = 1
        
        return new_sample
        
        
class OneMax:
    """Fitness function for One Max bitstring optimization problem."""
        
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        
        fitness = sum(bitstring)
        return fitness


class FlipFlop:
    """Fitness function for Flip Flop bitstring optimization problem."""
        
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        fitness = 0
        
        for i in range(1, len(bitstring)):
            if bitstring[i] != bitstring[i - 1]:
                fitness += 1
        
        return fitness
    
    
def head(b, x):
    """Determine the number of leading b's in vector x
    
    Args: 
    b: int. Integer for counting at head of vector.
    x: array. Vector of integers.
    
    Returns:
    head: int. Number of leading b's in x.
    """
    
    # Initialize counter
    head = 0
    
    # Iterate through values in vector
    for i in range(len(x)):
        if x[i] == b:
            head += 1
        else:
            break

    return head

def tail(b, x):
    """Determine the number of trailing b's in vector x
    
    Args: 
    b: int. Integer for counting at tail of vector.
    x: array. Vector of integers.
    
    Returns:
    tail: int. Number of trailing b's in x.
    """
    
    # Initialize counter
    tail = 0
    
    # Iterate backwards through values in vector
    for i in range(len(x)):
        if x[len(x) - i - 1] == b:
            tail += 1
        else:
            break

    return tail

def max_run(b, x):
    """Determine the length of the maximum run of b's in vector x
    
    Args: 
    b: int. Integer for counting.
    x: array. Vector of integers.
    
    Returns:
    max_run: int. Length of maximum run of b's
    """
    # Initialize counter
    max_run = 0
    run = 0
    
    # Iterate through values in vector
    for i in range(len(x)):
        if x[i] == b:
            run += 1
        else:
            if run > max_run:
                max_run = run
                
            run = 0

    return max_run
    

class FourPeaks:
    """Fitness function for Four Peaks bitstring optimization problem."""
    
    def __init__(self, t_pct = 0.1):
        """Initialize FourPeaks object.
        
        Args:
        t_pct: float. Threshold parameter (T) for four peaks fitness function.
        
        Returns:
        None            
        """
        self.t_pct = t_pct
        
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        n = len(bitstring)
        t = np.ceil(self.t_pct*n)
        
        # Calculate head and tail values
        tail_0 = tail(0, bitstring)
        head_1 = head(1, bitstring)

        # Calculate R(X, T)
        if (tail_0 > t and head_1 > t):
            r = n
        else:
            r = 0
        
        # Evaluate function
        fitness = max(tail_0, head_1) + r
    
        return fitness
    
    
class SixPeaks:
    """Fitness function for Six Peaks bitstring optimization problem."""
    
    def __init__(self, t_pct = 0.1):
        """Initialize SixPeaks object.
        
        Args:
        t_pct: float. Threshold parameter (T) for six peaks fitness function.
        
        Returns:
        None            
        """
        self.t_pct = t_pct
        
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        n = len(bitstring)
        t = np.ceil(self.t_pct*n)
        
        # Calculate head and tail values
        head_0 = head(0, bitstring)
        tail_0 = tail(0, bitstring)
        head_1 = head(1, bitstring)
        tail_1 = tail(1, bitstring)
        
        # Calculate R(X, T)
        if (tail_0 > t and head_1 > t) or (tail_1 > t and head_0 > t):
            r = n
        else:
            r = 0
        
        # Evaluate function
        fitness = max(tail_0, head_1) + r
    
        return fitness

class ContinuousPeaks:
    """Fitness function for Continuous Peaks bitstring optimization problem."""
    
    def __init__(self, t_pct = 0.1):
        """Initialize ContinuousPeaks object.
        
        Args:
        t_pct: float. Threshold parameter (T) for continuous peaks fitness function.
        
        Returns:
        None            
        """
        self.t_pct = t_pct
        
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        n = len(bitstring)
        t = np.ceil(self.t_pct*n)
        
        # Calculate length of maximum runs of 0's and 1's
        max_0 = max_run(0, bitstring)
        max_1 = max_run(1, bitstring)
        
        # Calculate R(X, T)
        if (max_0 > t and max_1 > t):
            r = n
        else:
            r = 0
        
        # Evaluate function
        fitness = max(max_0, max_1) + r
    
        return fitness
   
class Knapsack:
    """Fitness function for Knapsack bitstring optimization problem."""

    def __init__(self, weights, values, max_weight_pct = 0.35):
        """Initialize Knapsack object.
        
        Args:
        weights: array. Array of weights for each of the possible items. 
        values: array. Array of values for each of the possible items. Must be same
        length as weights array.
        max_weight_pct: float. Parameter used to set maximum capacity of knapsack (W)
        as a percentage of the total weight of all items (W = max_weight_pct*total_weight)
        
        Returns:
        None            
        """
        self.weights = weights
        self.values = values
        self.W = np.ceil(sum(self.weights)*max_weight_pct)
    
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation. Must be same length as
        weights and values arrays.
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        # Calculate total weight and value of knapsack
        total_weight = np.sum(bitstring*self.weights)
        total_value = np.sum(bitstring*self.values)

        # Allow for weight constraint
        if total_weight <= self.W:
            fitness = total_value       
        else:
            fitness = 0
        
        return fitness

class TravellingSales:
    """Fitness function for Travelling Salesman bitstring optimization problem."""
    
    def __init__(self, distances):
        """Initialize TravellingSales object.
        
        Args:
        distances: matrix. n x n matrix giving the distances between pairs of cities.
        In most cases, we would expect the lower triangle to mirror the upper triangle 
        and the lead diagonal to be zeros.
        
        Returns:
        None            
        """
        self.distances = distances
    
    def evaluate(self, bitstring):
        """Evaluate the fitness of a bitstring
        
        Args:
        bitstring: array. Bitstring value for evaluation. Must contain the same number
        of elements as the distances matrix
           
        Returns:
        fitness: float. Value of fitness function. 
        """
        # Reshape bitstring to match distance matrix
        bitmat = np.reshape(bitstring, np.shape(self.distances))
        
        # Determine upper limit on distances
        max_dist = np.max(self.distances[self.distances < np.inf])*np.shape(bitmat)[0]
        
        # Replace invalid values with very large values (i.e. max_dist)
        bitmat[bitmat == -1] = max_dist 
        
        # Calculate total distance and constraint values
        total_dist = np.sum(self.distances*bitmat)

        row_sums = np.sum(bitmat, axis = 1)
        col_sums = np.sum(bitmat, axis = 0)
        diag_sum = np.sum(np.diag(bitmat))
        
        # Determine fitness
        if (np.max(row_sums) == 1 and np.min(row_sums) == 1) and \
            (np.max(col_sums) == 1 and np.min(col_sums) == 1) and \
            diag_sum == 0:
                
            fitness = max_dist - total_dist
        
        else:
            fitness = 0

        return fitness