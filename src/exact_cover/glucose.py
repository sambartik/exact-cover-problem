import subprocess
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class GlucoseSATResponse:
    satisfied: bool = False
    model: Optional[List[int]] = None

class GlucoseSAT:
    """ Interface for the Glucose SAT solver """

    # These are the only acceptable levels for verbosity
    VERBOSE_LEVEL_LOW = 0
    VERBOSE_LEVEL_MID = 1
    VERBOSE_LEVEL_MAX = 2

    def __init__(self, exec_path: str):
        self._exec_path = exec_path

    def run_from_file(self, filepath: str, verbosity_level: int | None = 0, get_model: bool = True) -> GlucoseSATResponse:
        """
        Runs the Glucose SAT solver from a compatible file, check https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html#dimacs-cnf
        :param filepath: Path to the file to run the Glucose SAT solver from
        :param get_model: Whether to return a model in case of a SAT result
        :param verbosity_level: Either None to mute all output from the solver process or a valid verbosity level, check constants in this class
        :return: A glucose response object that has the model field filled iff get_model is True and the solver returned a model
        :exception Exception: In case satisfiability was not able to be determined or when glucose failed to execute.
        """
        glucose_args = [self._exec_path]
        if get_model: glucose_args.append("-model")
        glucose_args.append(f"-verb={verbosity_level if verbosity_level is not None else self.VERBOSE_LEVEL_LOW}")
        glucose_args.append(filepath)

        try:
            process_result = subprocess.run(glucose_args, stdout=subprocess.PIPE)
        except:
            raise Exception(f"Failed to execute Glucose SAT solver.")

        model = None
        satisfied = None
        for line in process_result.stdout.decode('utf-8').split('\n'):
            if get_model and line.startswith("v"):
                model = list(map(int, line[1:-1].strip().split(" "))) # Gets rid of first and last char and then parses ints inbetween
            if line.startswith("s SATISFIABLE"):
                satisfied = True
            if line.startswith("s UNSATISFIABLE"):
                satisfied = False

            if verbosity_level is not None: print(line)

        if satisfied is None:
            raise Exception("Unable to to discover satisfiability from the glucose process output.")

        return GlucoseSATResponse(satisfied=satisfied, model=model)
