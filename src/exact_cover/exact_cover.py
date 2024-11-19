from itertools import combinations
from typing import Tuple, List, Dict

from exact_cover_sat.cnf import DIMACS_CNF, VariableTranslator
from exact_cover_sat.glucose import GlucoseSAT


class ExactCoverProblem:
    """
    Describes an exact cover problem: https://en.wikipedia.org/wiki/Exact_cover
    Universum (or "X") is the set of all elements. Collection (or "S") is a system of subsets of the universum.

    We are looking for a collection S*, such that the union of all of its elements is the universum X, but at the same time
    all the elements of solution S* are mutually disjunctive, i.e. share no common elements.

    :param universum: The set X
    :param collection: The set S
    :param lookup_dict: A dictionary that for each element of universum x assigns a list of indices of elements of S that contain x
    """
    def __init__(self, universum: List[str], collection: List[List[str]], lookup_dict: Dict[str, List[int]]):
        self.universum = universum
        self.collection = collection
        self._lookup_dict = lookup_dict

    def get_subset_indices_containing_element(self, x: str) -> List[int]:
        """ Returns a list of indices of the self.collection List such that the element at that index within the self.collections List is a set containing the element x from the universum"""
        return self._lookup_dict.get(x, [])

class ExactCoverSolver:
    """
    Given the ExactCoverProblem, it reduces the problem to a SAT problem that it will then solve via a SAT solver.
    """
    def __init__(self, problem: ExactCoverProblem):
        self.problem = problem

    def _encode_to_dimacs_cnf(self) -> Tuple[DIMACS_CNF, VariableTranslator]:
        """
        Encodes the problem to a DIMACS CNF format, together with a translation dictionary. For formal specifics check out README.md.

        NOTE: Encode the problem to a DIMACS compatible CNF format. Formally, we have defined our atomic variables (propositions) as p_i is TRUE <=> S_i ∈ S*.
        We would have almost a DIMACS compatible CNF format if we renamed each our literal p_i to i and ¬p_i to -i. However, the problem is that DIMACS needs all the
        variables used in clauses to be in the 1,...,n range. But in our case it could occur that we construct a CNF statement that for the sake of simplicity contains a single clause with literals p_1, ¬p_4, p_2.
        The statement contains 3 distinct variables. We would have translated it to: 1, -4, 2. The problem is that the DIMACS format requires for us to explicitly state the numbers of distinct variables "n" at the start and
        then each of the clause can contain only variables 1,...,n.

        So I decided to translate back and forth between "our variables" as defined above (just reduced to numbers: kept only the i in p_i variable) and "normalized" variables in the required 1,...,n range.

        :return: A tuple of DIMACS CNF format and a Translator that can translate variables back and forth: normalized variable <-> our variable
        """
        clauses = []
        translator = VariableTranslator()

        for x in self.problem.universum:
            subset_indices_with_x = self.problem.get_subset_indices_containing_element(x) # { i | x \in S_i }

            # S1: Just take all subset indices a,b,c,... that contain the element x, constructing a single CNF clause: (p_a OR p_b OR p_c OR ...)
            s1_clause = [translator.get_normalized_var(our_variable_number) for our_variable_number in subset_indices_with_x]
            clauses.append(s1_clause)

            # S2: Iterate over combinations of subset indices i,j that contain the element x. For such a pair we construct a CNF clause: (NOT p_i OR NOT p_j)
            for i,j in combinations(range(len(subset_indices_with_x)), 2):
                normalized_var_translation_i = translator.get_normalized_var(subset_indices_with_x[i])
                normalized_var_translation_j = translator.get_normalized_var(subset_indices_with_x[j])
                clauses.append([-normalized_var_translation_i, -normalized_var_translation_j]) # corresponds to (NOT p_i OR NOT p_j)

        return DIMACS_CNF(clauses, translator.get_var_count()), translator

    def _decode_model(self, model: List[int], translator: VariableTranslator) -> List[int]:
        """
        Decodes the SAT model into a solution of our problem.

        :param model: A model returned from a SAT solver on a normalized DIMACS CNF formula
        :param translator: Translator that translates from the 1...n SAT solver atomic variables (proposition) to our definition of variables
        :return: Indices of the self.collection set to choose in order to satisfy the exact cover problem
        """

        # Skip negative variables as they correspond to "NOT" choosing a subset from the collection
        collection_indices = [ translator.get_our_var(glucose_var) for glucose_var in model if glucose_var > 0 ]
        return collection_indices


    def solve(self, solver: GlucoseSAT, cnf_output_file: str, solver_verbosity: int = GlucoseSAT.VERBOSE_LEVEL_LOW) -> List[int] | None:
        """ Solves the problem using the passed SAT solver """
        dimacs_cnf, var_translator = self._encode_to_dimacs_cnf()
        dimacs_cnf.save_to_file(cnf_output_file)

        result = solver.run_from_file(cnf_output_file, solver_verbosity, get_model=True)

        return self._decode_model(result.model, var_translator) if result.satisfied else None

def load_problem_from_file(filepath: str) -> ExactCoverProblem:
    """
    Loads the ExactCoverProblem from a file that obides by the format described in README.md
    :param filepath: Path to the input problem file
    :return: ExactCoverProblem instance
    """
    universum = []
    subsets = []
    lookup_dict = {}
    try:
        with open(filepath, 'r') as f:
            header_line = f.readline()
            universum = header_line.split()

            subset_index = 0
            for line in f:
                subset = line.split()
                for subset_element in subset:
                    if subset_element in lookup_dict:
                        lookup_dict[subset_element].append(subset_index)
                    else:
                        lookup_dict[subset_element] = [subset_index]
                subsets.append(subset)
                subset_index += 1

        return ExactCoverProblem(universum, subsets, lookup_dict)
    except:
        raise Exception(f"A problem occurred while loading the problem from file: {filepath}")