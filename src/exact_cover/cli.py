import argparse
import sys
from pathlib import Path
from typing import List

from exact_cover_sat.exact_cover import ExactCoverProblem, ExactCoverSolver, load_problem_from_file
from exact_cover_sat.glucose import GlucoseSAT

def print_formated_solution(problem: ExactCoverProblem, solution: List[int] | None) -> None:
    print("#####################")
    print("###### RESULTS ######")
    print("#####################\n")
    if solution is None:
        print("No solution found. There does not exist such set S* that would satisfy the problem's requirements.")
        return
    print(f"Hurray! Successfully found the set:")
    names_of_subsets: str = ", ".join([f"S_{i+1}" for i in solution])
    print(f"S* = {{ {names_of_subsets} }}, where: ")
    for i in solution:
        subset_elements: str = ", ".join(map(str, problem.collection[i]))
        print(f"  S_{i+1} = {{ {subset_elements} }}")

def main():
    parser = argparse.ArgumentParser(description="Solves the Exact Cover problem.")
    parser.add_argument("-i", "--input", default="problem.in", type=str, help="The input file for the problem")
    parser.add_argument("-o", "--output", default="dimacs_cnf.out", type=str, help="The path where computed DIMACS CNF formula should be written to")
    parser.add_argument("-s", "--solver", default="glucose-syrup", type=str, help="Path to the glucose-syrup SAT solver executable")
    parser.add_argument("-v", "--verb", default=1, type=int, choices=[0, 1, 2], help="Glucose SAT solver verbosity level")
    args = parser.parse_args()

    try:
        glucose_sat = GlucoseSAT(args.solver)
        problem = load_problem_from_file(args.input)
        problem_solver = ExactCoverSolver(problem)

        solution = problem_solver.solve(glucose_sat, args.output, solver_verbosity=args.verb)
        print_formated_solution(problem, solution)
    except Exception as e:
        print(f"An unrecoverable error occurred: {e}", file=sys.stderr)
        exit(1)

if __name__ == "__main__":
    main()
