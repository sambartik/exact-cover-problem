# Exact Cover solver

A python implementation that solves the exact cover problem via logic.

## Problem statement

Given a set `X = { x_1, x_2, ..., x_k }` *(the universum)* and a set `S = { S_1, S_2, ..., S_l }` *(the collection)* where every `S_i` is a subset of `X`, find the subset `S*` of set `S` such that every element of `X` is an element of an **exactly** 1 element of `S*`.

___

## Encoding

Given a universum `X = { x_1, x_2, ..., x_k }` and a collection `S = { S_1, S_2, ..., S_l }`, we are looking for a collection `S*`.
Formally, we define our language as: `P = { p_1, p_2, ..., p_l }`, where the atomic proposition `p_i` translates to `"S_i is in the collection S*"`

First of all, let's define a helper set `A_i`:
`\forall x_i \in X: A_{x_i} := { r | \exists r \in {1,2,...,l}: x_i \in S_r }`

From the definition of the problem these statements must hold true:

1. `S1)` Every element of the universum `X` is in **AT LEAST** one of the subsets of the resulting collection `S*`
   - Let's say we have `x \in X`, that is element of these subsets: `{ S_a, S_b, ..., S_z } = A_x`. Then we can express that `S*` collection contains at least one of them by introducing a single CNF clause: `(p_a OR p_b OR ... OR p_z)`.


2. `S2)` Every element of universum `X` is **AT MOST** in one of the subsets of the resulting collection `S*`
    - Again, let's say we have `x \in X`, that is element of these subsets: `{ S_a, S_b, ..., S_z } = A_x`. Then we can express that `S*` collection contains at most one of them by saying that for each pair of indices `i < j`: `(NOT S_i OR NOT S_j)` holds true. That would result in multiple CNF clauses per each element of universum.

Given that `S1)` and `S2)` holds true, then every element of universum `X` is **EXACTLY** in one of the subsets of the resulting collection `S*`. Which is how was the set `S*` defined, thus giving us the solution.

## Program usage

### Dependencies

- [Glucose 4.2.1](https://github.com/audemard/glucose/tree/4.2.1) - used as a CNF solver. Compiled `glucose-syrup` binary is required.

### Installation

We assume that you do not have the glucose binary, but your system is able to compile a C++ project via CMake & Make.

1. Clone the repository together with submodules: `git clone --recurse-submodules https://github.com/sambartik/exact-cover-problem.git ExactCover`
2. Navigate into the repository: `cd ExactCover`
3. Create a new python virtual environment: `python3 -m venv venv`
4. Activate the new environment:
   - Linux bash: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
5. Install the python package: `pip install .`

Now, we need to compile the Glucose binary. Its source files are located in `libs/glucose` directory. On Linux you can simply:
1. Navigate to the folder with glucose source files: `cd libs/glucose`
2. Create a new Makefile: `cmake .`
3. Compile: `make`
4. There should be an executable `glucose-syrup` in the current directory

You could skip these compiling steps if you already have a working binary in your system. 

_Note:_ If the `glucose-syrup` binary is not in your current directory, you need to manually point the script to its location via the `-s` CLI switch.

If you have finished all steps successfully, congratulations! As long as you are in our newly created python virtual environment, you should be able to execute the command `exact-cover` from anywhere.

You can disable the virtual environment by executing `deactivate` command in the terminal.

### Usage

After successful installation, you should have `exact-cover` in your path. The script assumes an input file with a valid format is passed to it.

```
usage: exact-cover [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1,2}]

Solves the Exact Cover problem.

options:
  -h, --help           show this help message and exit
  -i, --input INPUT    The input file for the problem
  -o, --output OUTPUT  The path where computed DIMACS CNF formula should be written to
  -s, --solver SOLVER  Path to the glucose-syrup SAT solver executable
  -v, --verb {0,1,2}   Glucose SAT solver verbosity level
```

### Input file format:
The format of the input file is quite simple:
- First line contains space delimited list of elements of _the universum_ `X`
- Each subsequent line contains space delimited list of elements of `S_i`

**Beware**, if the last line is terminated by a newline, then that would be interpreted as a blank line at the end of the input file. Blank lines are always treated as sets with 0 elements.

Example:

`X = { 1, 2, 3 }`

`S = { S_1, S_2, S_3 }`

`S_1 = { }`

`S_2 = { 2 }`

`S_3 = { 2, 3 }`

Would correspond to this file:

```
1 2 3

2
2 3
```

_Note, that there is no newline at the end of the last line, otherwise, that would correspond to `S_4 = { }`._

### Output file format

It is a DIMACS CNF compatible file format. Please check it out over here: https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html

## Testing data

The testing_dataset folder contains data you can test with:
- `01_wiki_example_1_sat.in`: Easy solvable instance of the problem, easily solvable by eyeballing it
- `01_wiki_example_1_unsat.in`: Easy unsolvable instance of the problem, easily solvable by eyeballing it
- `02_wiki_example_2_sat.in`: A bit more complex solvable instance of the problem, again verifiable by eyeballing it
- `03_hard_problem_sat.in`: A large solvable instance of the problem that takes 10+ seconds to run - The universum X has 10 elements and the set S = 2^X
- `04_cpu_heater_sat.in`: It is not a problem anymore. It is a solution.... That is, if your room is cold and your heater is broken. The same as 03, but X has 20 elements.

## Benchmarks

Testing dataset tested on `Intel(R) Core(TM) i9-9880H CPU @ 2.30GHz` via `hyperfine`:

```
Benchmark 1: exact-cover-sat -i testing_dataset/01_wiki_example_1_sat.in -s /bin/glucose-syrup -v 0
  Time (mean ± σ):      91.9 ms ±   1.5 ms    [User: 64.6 ms, System: 23.6 ms]
  Range (min … max):    89.4 ms …  93.9 ms    29 runs
```

```
Benchmark 2: exact-cover-sat -i testing_dataset/02_wiki_example_2_sat.in -s /bin/glucose-syrup -v 0
  Time (mean ± σ):      93.8 ms ±   2.2 ms    [User: 66.1 ms, System: 24.3 ms]
  Range (min … max):    90.3 ms …  97.9 ms    29 runs
```

```
Benchmark 3: exact-cover-sat -i testing_dataset/03_hard_problem_sat.in -s /bin/glucose-syrup -v 0
  Time (mean ± σ):     46.708 s ±  0.346 s    [User: 46.305 s, System: 0.297 s]
  Range (min … max):   46.334 s … 47.257 s    10 runs
```

Benchmark 4 with `04_cpu_heater_sat.in` does not finish in any reasonable time and had to be terminated.

The overall speed mainly depends on the number of clauses in the CNF formula. And as we can see from the encoding section,
that depends on the number of elements, but most importantly on the number of subsets `S_i`.

## Glossary

- **a variable** - a proposition, an element of language in logic
- **our variables** - variables `p_i` as we defined in our language P in the encoding section
- **normalized variables** - transformed variables `p_i` that glucose expects based on its DIMACS_CNF format (in the 1,...,n range)
- **solution** - the set `S*` we are looking for