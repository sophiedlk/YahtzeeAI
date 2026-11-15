# Yahtzee AI Agent

An intelligent agent for the Yahtzee dice game, implemented in Python.

The agent uses the Expectimax search algorithm to decide which dice to keep, which dice to reroll, and which scoring category to select. It also uses heuristic evaluation, pruning, and memoization to improve decision-making efficiency.

## 1. Project Overview

The goal of this project is to implement an autonomous agent that can play a complete 13-turn game of Yahtzee without human intervention.

The agent is responsible for:

- Maintaining the game state and scorecard.
- Selecting dice to keep or reroll.
- Choosing a scoring category.
- Calculating scores according to Yahtzee rules.
- Handling Yahtzee bonuses and Joker rules.
- Maximizing the expected final score.

## 2. Algorithms and Techniques

### Expectimax

The main decision-making algorithm is Expectimax.

It handles two types of nodes:

- **Max nodes:** Represent the agent's decisions.
- **Chance nodes:** Represent random dice outcomes.

The agent evaluates possible keep and reroll actions and selects the action with the highest expected value.

The search focuses on the current turn. After scoring a category, a heuristic function estimates the value of the remaining game rather than expanding the complete 13-turn game tree.

### Probability Calculation

Possible unordered dice outcomes are generated using combinations with replacement.

The `Fraction` class is used to represent probabilities exactly during outcome generation. This avoids floating-point rounding errors in individual outcome probabilities.

### Pruning and Memoization

The Expectimax implementation uses an optimistic upper-bound method to skip chance outcomes that cannot improve the current best action.

The implementation also uses memoization to avoid evaluating identical states repeatedly.

Pruning and memoization are separate optimizations.

### Heuristic Evaluation

The heuristic estimates the value of a non-terminal game state using:

- Current accumulated score.
- Expected scores of unfilled categories.
- Estimated probability of earning the upper-section bonus.

The upper-section bonus is 35 points when the upper-section total reaches at least 63 points. The heuristic avoids adding this bonus again when it has already been earned.

## 3. Project Structure

```text
YahtzeeAI/
|
|-- main.py
|-- json_interface.py
|-- game_state.py
|-- game_engine.py
|-- scoring.py
|-- yahtzee_rules.py
|-- dice_probability.py
|-- strategy.py
|-- expectimax.py
|-- heuristic.py
|-- heuristic_baseline.py
|-- greedy_agent.py
|-- simulation.py
|-- requirements.txt
|-- README.md
|
|-- tests/
|   |-- test_dice_probability.py
|   |-- test_expectimax.py
|   |-- test_game_engine.py
|   |-- test_game_state.py
|   |-- test_greedy_agent.py
|   |-- test_heuristic.py
|   |-- test_pruning.py
|   |-- test_pruning_correctness.py
|   |-- test_scoring.py
|   |-- test_strategy.py
|   |-- test_yahtzee_rules.py
|
|-- benchmarks/
    |-- benchmark_comparison.py
    |-- benchmark_full_game_pruning.py
    |-- benchmark_games.py
    |-- benchmark_heuristics.py
    |-- benchmark_pruning.py
    |-- benchmark_three_agents.py
    |-- compare_heuristic_values.py
    |-- run_json_interface_game.py
```

## 4. Installation

Python 3.11 or later is recommended.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 5. Running the Agent

Run the main program:

```bash
python main.py
```

The program reads JSON requests from standard input, one request per line, and writes JSON responses to standard output.

Multiple requests can be processed in one execution.

## 6. Running Tests

Run all tests:

```bash
python -m pytest -v
```

The current test suite contains 160 tests.

Latest recorded result:

- Passed: 160
- Failed: 0
- Execution time: 20.72 seconds

## 7. Running Benchmarks

Benchmark scripts are located in the `benchmarks/` directory.

Examples:

```bash
python benchmarks/benchmark_three_agents.py
python benchmarks/benchmark_comparison.py
python benchmarks/benchmark_pruning.py
python benchmarks/benchmark_full_game_pruning.py
python benchmarks/benchmark_heuristics.py
```

These experiments compare the Expectimax agent with simpler agents and evaluate the effects of pruning and heuristic changes.

## 8. Experimental Results

The following results were obtained from reproducible experiments using fixed random seeds.

### Agent Comparison

A 50-game comparison was performed using the same reproducible dice seeds for all three agents.

| Metric | Expectimax | Greedy | Random |
|---|---:|---:|---:|
| Average score | 240.58 | 218.64 | 47.82 |
| Median score | 234 | 207 | 45 |
| Minimum score | 151 | 133 | 20 |
| Maximum score | 422 | 324 | 138 |
| Average runtime | 25.7430 s | 1.0855 s | 0.0023 s |

Win counts:

- Expectimax: 35 wins
- Greedy: 13 wins
- Random: 0 wins
- Draws: 2

Average score differences:

- Expectimax vs. Greedy: +21.94
- Expectimax vs. Random: +192.76
- Greedy vs. Random: +170.82

These results show that Expectimax achieved the highest average score and won most of the paired comparisons. However, it required considerably more computation time than the simpler agents.

### Pruning Comparison

A paired full-game experiment was performed using five reproducible seeds.

| Metric | Without Pruning | With Pruning |
|---|---:|---:|
| Average score | 220.80 | 220.80 |
| Average runtime | 28.41 s | 27.43 s |
| Average expanded nodes | 9,764 | 9,535 |
| Average evaluated outcomes | 3,330,207 | 3,089,635 |

Additional results:

- Evaluated outcome reduction: 7.22%
- Runtime speedup: 1.04x
- Total pruned outcomes: 1,037,044

The final score was identical in all five paired games. Pruning reduced the number of evaluated chance outcomes, while its measured improvement in total runtime remained modest.

### Heuristic Comparison

A 20-game paired comparison was performed between the baseline and modified heuristic versions, using seeds 6000 to 6019.

Results:

- Baseline average score: 235.10
- Modified heuristic average score: 235.10
- Average score difference: 0.00
- Total compared decisions: 730
- Identical decisions: 730
- Different decisions: 0

The experiment did not demonstrate a measurable improvement in agent decisions or final scores from the modified heuristic.

## 9. Limitations

- Expectimax searches within the current turn rather than expanding the complete 13-turn game tree.
- The heuristic estimates future category values instead of calculating the exact optimal value of the remaining game.
- Pruning reduces the number of evaluated chance outcomes, but its measured improvement in total runtime is modest.
- The full-game pruning experiment used only five games, so its results should be considered preliminary.
- The heuristic comparison did not show a measurable improvement over the baseline version.
- Benchmark results depend on the selected seeds and experimental conditions.
- Expectimax requires substantially more computation time than Greedy and Random agents.

## 10. Technologies

- Python
- Expectimax Search
- Probability Modeling
- Heuristic Evaluation
- Pruning
- Memoization
- Pytest
- JSON Interface
