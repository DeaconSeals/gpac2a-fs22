
# GPac primitives
# internal_nodes = {'+','-','*','/','RAND'}
# leaf_nodes = {'G','P','W','F','#.#'}

class TreeGenotype():
    def __init__(self):
        self.fitness = None
        self.gene = None

    def recombine(self, mate, **kwargs):
        child = self.__class__()

        # TODO: recombine genes of self and mate and assign to child's gene member variable
        pass

        return child

    def mutate(self, **kwargs):
        copy = self.__class__()

        # TODO: copy self.gene to copy.gene
        pass

        # TODO: mutate gene of copy
        pass

        return copy

    def print(self):
        # TODO: return a string representation of self.gene
        #       (see assignment description doc for more info)
        pass

    @classmethod
    def initialization(cls, mu, *args, **kwargs):
        population = [cls() for _ in range(mu)]
        depth_limit = kwargs['depth_limit']
        # TODO: initialize gene member variables of individuals in 
        # population using ramped half-and-half
        pass

        return population