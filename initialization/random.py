import numpy as np
from tqdm import tqdm
from utils.datasets import DataLoader
from utils.mapping import shifted_heaviside_function


class RandomBinaryInitialization():
    """Randomly initialize subpopulations with binary representation.

    Attributes
    ----------
    subpops : list
        Individuals from all subpopulations. Each individual is represented by a binary
        n-dimensional array, where n is the number of features in the specific subcomponent. If
        there is a 1 in the i-th position of the array, it indicates that the i-th feature should
        be considered and if there is a 0, it indicates that the feature should not be considered.
    fitness : list
        Evaluation of all context vectors from all subpopulations.
    context_vectors: list
        Complete problem solutions that were randomly initialized.
    """

    def __init__(
            self,
            data: DataLoader,
            subcomp_sizes: list,
            subpop_sizes: list,
            collaborator,
            fitness_function
    ):
        """
        Parameters
        ----------
        data : DataLoader
            Container with processed data and training and test sets.
        subcomp_sizes : list
            Number of features in each subcomponent.
        subpop_sizes : list
            Subpopulation sizes, that is, the number of individuals in each subpopulation.
        collaborator : object of one of the collaboration classes.
            Responsible for selecting collaborators for individuals.
        fitness_function : object of one of the fitness classes.
            Responsible for evaluating individuals, that is, subsets of features.
        """
        # Parameters as attributes
        self.data = data
        self.subpop_sizes = subpop_sizes
        self.fitness_function = fitness_function
        self.collaborator = collaborator
        # Complete problem solutions
        self.context_vectors = list()
        # Individuals of all subpopulations
        self.subpops = list()
        # List to store the fitness of all context vectors
        self.fitness = list()
        # Number of subcomponents
        self.n_subcomps = len(subcomp_sizes)
        # Number of features in each subcomponent
        self.subcomp_sizes = subcomp_sizes

    def build_subpopulations(self):
        """Randomly initializes individuals from all subpopulations."""
        # Initialize the progress bar
        progress_bar = tqdm(total=self.n_subcomps, desc="Building subpopulations")
        # For each subcomponent with a specific number of features, build a subpopulation
        for subcomp_size, subpop_size in zip(self.subcomp_sizes, self.subpop_sizes):
            # Initialize subpop_size individuals of size subcomp_size with only 0's and 1's
            subpop = np.random.choice([0, 1], size=(subpop_size, subcomp_size))
            # Store all individuals of the current subpopulation
            self.subpops.append(subpop)
            # Update progress bar
            progress_bar.update(1)
        # Close progress bar
        progress_bar.close()

    def evaluate_individuals(self):
        """Evaluate all individuals from all subpopulations."""
        # Initialize the progress bar
        progress_bar = tqdm(total=self.n_subcomps, desc="Evaluating individuals")
        # For each subpopulation
        for i, subpop in enumerate(self.subpops):
            # List to store the context vectors in the current subpopulation
            subpop_context_vectors = list()
            # List to store the evaluations of these context vectors
            subpop_fitness = list()
            # Evaluate each individual in the subpopulation
            for j, _ in enumerate(subpop):
                # Find random collaborator(s) for the current individual
                collaborators = self.collaborator.get_collaborators(subpop_idx=i,
                                                                    indiv_idx=j,
                                                                    subpops=self.subpops)
                # Build a context vector to evaluate a complete solution
                context_vector = self.collaborator.build_context_vector(collaborators)
                # Evaluate the context vector
                fitness = self.fitness_function.evaluate(context_vector, self.data)
                # Store the complete problem solution related to the current individual
                subpop_context_vectors.append(context_vector.copy())
                # Store evaluation of the current context vector
                subpop_fitness.append(fitness)
            # Store all complete problem solutions related to the current subpopulation
            self.context_vectors.append(np.vstack(subpop_context_vectors))
            # Store evaluation of all context vectors of the current subpopulation
            self.fitness.append(subpop_fitness)
            # Update progress bar
            progress_bar.update(1)
            # Delete variables related to the current subpopulation
            del subpop_context_vectors, subpop_fitness
        # Close progress bar
        progress_bar.close()


class RandomContinuousInitialization():
    """Randomly initialize subpopulations with continuous representation.

    For certain Evolutionary Algorithms, like Differential Evolution, which operate on continuous
    solutions, an appropriate initialization is required based on this representation.

    Attributes
    ----------
    subpops : list
        Individuals from all subpopulations. Each individual is represented by a n-dimensional
        continuous array, where n is the number of features in the specific subcomponent.
    fitness : list
        Evaluation of all context vectors from all subpopulations.
    context_vectors : list
        Complete problem solutions that were randomly initialized.
    """

    def __init__(
            self,
            data: DataLoader,
            subcomp_sizes: list,
            subpop_sizes: list,
            collaborator,
            fitness_function,
            bounds: tuple[int, int] = (0, 1)
    ):
        """
        Parameters
        ----------
        data : DataLoader
            Container with processed data and training and test sets.
        subcomp_sizes : list
            Number of features in each subcomponent.
        subpop_sizes : list
            Subpopulation sizes, that is, the number of individuals in each subpopulation.
        collaborator : object of one of the collaboration classes.
            Responsible for selecting collaborators for individuals.
        fitness_function : object of one of the fitness classes.
            Responsible for evaluating individuals, that is, subsets of features.
        bounds : tuple[int, int], default (0, 1)
            Bounds of continuous variables.
        """
        # Parameters as attributes
        self.data = data
        self.subpop_sizes = subpop_sizes
        self.fitness_function = fitness_function
        self.collaborator = collaborator
        # Complete problem solutions
        self.context_vectors = list()
        # Individuals of all subpopulations
        self.subpops = list()
        # List to store the fitness of all context vectors
        self.fitness = list()
        # Number of subcomponents
        self.n_subcomps = len(subcomp_sizes)
        # Number of features in each subcomponent
        self.subcomp_sizes = subcomp_sizes
        # Bounds
        self.bounds = bounds

    def build_subpopulations(self):
        """Randomly initializes individuals from all subpopulations."""
        # Initialize the progress bar
        progress_bar = tqdm(total=self.n_subcomps, desc="Building subpopulations")
        # For each subcomponent with a specific number of features, build a subpopulation
        for subcomp_size, subpop_size in zip(self.subcomp_sizes, self.subpop_sizes):
            # Initialize 'subpop_size' individuals with 'subcomp_size' continuous values between
            # bounds
            subpop = np.random.uniform(
                low=self.bounds[0],
                high=self.bounds[1],
                size=(subpop_size, subcomp_size)
            )
            # Store all individuals of the current subpopulation
            self.subpops.append(subpop)
            # Update progress bar
            progress_bar.update(1)
        # Close progress bar
        progress_bar.close()

    def evaluate_individuals(self):
        """Evaluate all individuals from all subpopulations."""
        # Initialize the progress bar
        progress_bar = tqdm(total=self.n_subcomps, desc="Evaluating individuals")
        # For each subpopulation
        for i, subpop in enumerate(self.subpops):
            # List to store the context vectors in the current subpopulation
            subpop_context_vectors = list()
            # List to store the evaluations of these context vectors
            subpop_fitness = list()
            # Evaluate each individual in the subpopulation
            for j, _ in enumerate(subpop):
                # Find random collaborator(s) for the current individual in the abstracted space
                encoded_collaborators = self.collaborator.get_collaborators(subpop_idx=i,
                                                                            indiv_idx=j,
                                                                            subpops=self.subpops)
                # Collaborators in the continuous space is transformed into the binary space
                collaborators = [
                    shifted_heaviside_function(collaborator)
                    for collaborator in encoded_collaborators
                ]
                # Build a context vector to evaluate a complete solution
                context_vector = self.collaborator.build_context_vector(collaborators)
                # Evaluate the context vector
                fitness = self.fitness_function.evaluate(context_vector, self.data)
                # Store the complete problem solution related to the current individual
                subpop_context_vectors.append(context_vector.copy())
                # Store evaluation of the current context vector
                subpop_fitness.append(fitness)
            # Store all complete problem solutions related to the current subpopulation
            self.context_vectors.append(np.vstack(subpop_context_vectors))
            # Store evaluation of all context vectors of the current subpopulation
            self.fitness.append(subpop_fitness)
            # Update progress bar
            progress_bar.update(1)
            # Delete variables related to the current subpopulation
            del subpop_context_vectors, subpop_fitness
        # Close progress bar
        progress_bar.close()
