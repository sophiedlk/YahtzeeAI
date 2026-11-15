# Yahtzee AI Agent
## Implementation and Evaluation Report

**Programming Language:** Python 3.11  
**Main Algorithm:** Expectimax Search  
**Project Type:** Artificial Intelligence — Game-Playing Agent

---

# 1. Introduction

This project presents the design and implementation of an intelligent agent for the Yahtzee dice game using the Expectimax search algorithm.

Yahtzee is a dice game in which players roll five dice up to three times per turn and select one of thirteen scoring categories. The objective is to maximize the total score by making strategic decisions under uncertainty.

The agent evaluates possible dice-keeping and reroll actions, considers probabilistic dice outcomes, and selects a scoring category based on the current game state.

The main objectives of this project are:

- Implement a complete 13-round Yahtzee game.
- Develop an intelligent agent based on game-tree search.
- Model dice outcomes using exact probabilities.
- Implement heuristic evaluation for non-terminal game states.
- Improve search efficiency through pruning and memoization.
- Implement the Yahtzee bonus and Joker rules.
- Evaluate the agent against alternative strategies.
- Analyze the performance and limitations of the implemented methods.

# 2. System Architecture

The project follows a modular architecture. Each module is responsible for a specific part of the game or decision-making process.

## 2.1 Main Components

| Module | Responsibility |
|---|---|
| `game_state.py` | Represents and validates the current game state. |
| `scoring.py` | Calculates scores for all thirteen categories. |
| `game_engine.py` | Handles dice rerolls and scoring operations. |
| `dice_probability.py` | Generates possible dice outcomes and their probabilities. |
| `strategy.py` | Generates legal dice-keeping actions. |
| `expectimax.py` | Implements Expectimax search, pruning, and memoization. |
| `heuristic.py` | Estimates the value of non-terminal game states. |
| `greedy_agent.py` | Implements a greedy baseline agent. |
| `simulation.py` | Runs complete game simulations. |
| `json_interface.py` | Processes JSON-based requests and generates responses. |
| `main.py` | Provides the main program entry point. |

Additional directories:

- `tests/`: Automated tests for the project components.
- `benchmarks/`: Scripts for performance evaluation and agent comparison.

## 2.2 Game State Representation

The game state stores the information required to make decisions, including:

- Current dice values.
- Current turn number.
- Current roll number.
- The scorecard.
- Accumulated upper-section score.
- Accumulated Yahtzee bonus.
- Remaining scoring categories.

The scorecard contains thirteen categories. Each category can be selected only once during a game.

The implementation also validates important game-state properties, such as dice values, turn numbers, roll numbers, and scorecard values.

## 2.3 Scoring System

The implementation supports the thirteen standard Yahtzee scoring categories.

### Upper Section

- Ones
- Twos
- Threes
- Fours
- Fives
- Sixes

The upper-section bonus awards 35 additional points when the sum of the upper-section categories reaches at least 63 points.

### Lower Section

- Three of a Kind
- Four of a Kind
- Full House
- Small Straight
- Large Straight
- Yahtzee
- Chance

The scoring module calculates the score for each category according to the game rules.

## 2.4 Yahtzee Bonus and Joker Rules

The project also implements special Yahtzee rules.

A Yahtzee occurs when all five dice show the same value.

If the Yahtzee category has already been scored with 50 points, additional Yahtzees can award a 100-point bonus.

The Joker rules are also considered when determining the legal scoring categories for qualifying Yahtzee states.

# 3. Expectimax Search Algorithm

The main decision-making algorithm is Expectimax.

Unlike a simple greedy strategy, Expectimax considers possible future dice outcomes and calculates their expected values.

The search tree contains two main types of nodes.

### 3.1 Max Nodes

Max nodes represent the agent's decisions.

The agent evaluates the available actions and selects the action with the highest expected value.

These actions include:

- Keeping selected dice.
- Rerolling the remaining dice.
- Selecting a scoring category when the agent decides to end the turn.

### 3.2 Chance Nodes

Chance nodes represent random dice outcomes.

Since dice rolls are uncertain, the agent calculates the expected value of possible outcomes using their probabilities.

The expected value is calculated as:

\[
EV(s)=\sum_i P(o_i)V(o_i)
\]

Where:

- \(P(o_i)\) is the probability of outcome \(o_i\).
- \(V(o_i)\) is the estimated value of that outcome.
- \(EV(s)\) is the expected value of the current state.

### 3.3 Search Horizon

The Expectimax search evaluates decisions within the current turn.

After the agent selects a scoring category, the heuristic function estimates the value of the resulting game state.

Therefore, the implementation does not search the entire remaining 13-round game tree. It uses heuristic evaluation to estimate future game value.

# 4. Probability Model

The project models dice outcomes using combinations with replacement.

Instead of generating every ordered permutation, the implementation generates distinct unordered dice outcomes and calculates their corresponding probabilities.

The probabilities are represented using Python's `Fraction` type.

This approach provides exact rational probabilities and avoids floating-point approximation errors during probability calculations.

The probability model is used by Expectimax to evaluate possible reroll outcomes.

# 5. Heuristic Evaluation

Expectimax requires an evaluation function to estimate the value of non-terminal game states.

The project's heuristic considers information such as:

- Current accumulated score.
- Expected values of unfilled scoring categories.
- The possibility of obtaining the upper-section bonus.
- Whether the upper-section bonus has already been earned.

The heuristic provides an estimate of future scoring potential rather than an exact prediction of the final score.

An important correction in the implementation prevents the upper-section bonus from being counted again after it has already been earned.

# 6. Search Optimizations

Two main optimization techniques are implemented: pruning and memoization.

## 6.1 Pruning

The implementation uses an optimistic upper bound to eliminate chance outcomes that cannot improve the current best decision.

The remaining possible outcomes are considered in descending order of probability.

When the optimistic bound indicates that evaluating additional outcomes cannot improve the current decision, the remaining outcomes can be skipped.

The purpose of pruning is to reduce unnecessary recursive evaluations.

## 6.2 Memoization

Memoization stores previously evaluated states in a cache.

When the same state is encountered again, its previously calculated value can be reused instead of performing the same search again.

The state key includes relevant information such as:

- Sorted dice values.
- Current turn and roll.
- Scorecard.
- Upper-section total.
- Yahtzee bonus.
- Legal scoring categories.

Memoization and pruning are separate optimization techniques and are both used to improve search efficiency.

# 7. How to Run

## 7.1 Prerequisites

The following software is required:

- Python 3.11 or later.
- Git (optional, for cloning the repository).

The commands in this section are written for Windows PowerShell.

## 7.2 Clone the Repository

Clone the project from GitHub:

```powershell
git clone https://github.com/sophiedlk/YahtzeeAI.git
```

Navigate to the project directory:

```powershell
cd YahtzeeAI
```

Alternatively, download the repository as a ZIP file from GitHub and extract it.

## 7.3 Create a Virtual Environment

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use the following alternative to run Python without activating the environment:

```powershell
.\.venv\Scripts\python.exe --version
```

## 7.4 Install Dependencies

Install the packages listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

## 7.5 Run the Main Program

Start the program:

```powershell
python main.py
```

The program reads JSON requests from standard input and writes JSON responses to standard output.

It uses a JSON Lines (JSONL) interface. Each request must be provided on a separate line.

The program may wait for input after starting. This is expected behavior because it processes requests from standard input.

## 7.6 Run Automated Tests

To execute the complete test suite:

```powershell
python -m pytest -v
```

The recorded test execution produced:

**160 passed, 0 failed**

Execution time: approximately 20.72 seconds.

## 7.7 Run Benchmarks

Benchmark scripts are available in the `benchmarks/` directory.

For example, to compare the three agents:

```powershell
python benchmarks/benchmark_three_agents.py
```

To evaluate full-game pruning performance:

```powershell
python benchmarks/benchmark_full_game_pruning.py
```

To compare heuristic versions:

```powershell
python benchmarks/benchmark_heuristics.py
```

To run the pruning benchmark:

```powershell
python benchmarks/benchmark_pruning.py
```

Benchmark execution may take several minutes depending on the computer and the number of simulated games.

# 8. JSON Interface

The agent communicates through a JSON Lines (JSONL) interface.

Each input line contains one JSON request. The program processes the request and returns a JSON response on a separate output line.

## 8.1 Request Structure

The request includes information about the current game state.

The main fields are:

| Field | Description |
|---|---|
| `version` | Protocol version. |
| `turn` | Current turn number (1–13). |
| `roll` | Current roll number (1–3). |
| `dice` | Current values of the five dice. |
| `scorecard` | Scores for the thirteen categories; unfilled categories use `null`. |
| `upper_total` | Accumulated upper-section score. |
| `yahtzee_bonus` | Accumulated Yahtzee bonus. |
| `legal_categories` | Available scoring categories. |

## 8.2 Example Request

The following is an illustrative request for the first turn:

```json
{
  "version": 1,
  "turn": 1,
  "roll": 1,
  "dice": [1, 2, 3, 4, 5],
  "scorecard": {
    "ones": null,
    "twos": null,
    "threes": null,
    "fours": null,
    "fives": null,
    "sixes": null,
    "three_of_a_kind": null,
    "four_of_a_kind": null,
    "full_house": null,
    "small_straight": null,
    "large_straight": null,
    "yahtzee": null,
    "chance": null
  },
  "upper_total": 0,
  "yahtzee_bonus": 0,
  "legal_categories": [
    "ones",
    "twos",
    "threes",
    "fours",
    "fives",
    "sixes",
    "three_of_a_kind",
    "four_of_a_kind",
    "full_house",
    "small_straight",
    "large_straight",
    "yahtzee",
    "chance"
  ]
}
```

## 8.3 Response Structure

The agent can return one of two action types:

- `score`: Selects a scoring category.
- `reroll`: Specifies the dice indices that should be rerolled.

The exact action depends on the agent's evaluation of the supplied state.

For example, a scoring response has the following structure:

```json
{
  "action": "score",
  "category": "large_straight"
}
```

A reroll response has the following general structure:

```json
{
  "action": "reroll",
  "dice_indices": [0, 1]
}
```

The example responses illustrate the response format; the actual decision depends on the input state and the agent's search evaluation.

Multiple requests can be processed during one program execution, with one response generated for each valid input line.

# 9. Experimental Methodology

The agent was evaluated through simulation experiments.

Three main experiments were conducted to assess decision quality and computational efficiency.

## 9.1 Agent Comparison

Three agents were evaluated:

1. Expectimax
2. Greedy
3. Random

The experiment consisted of 50 games using seeds 3000–3049.

The same set of seeds was used for the agents to provide a reproducible comparison.

The evaluation metrics included:

- Average final score.
- Median final score.
- Minimum and maximum scores.
- Average execution time.
- Number of wins and draws.

## 9.2 Pruning Evaluation

The pruning experiment compared Expectimax with pruning enabled and disabled.

Five games were simulated using seeds 4000–4004.

The following metrics were recorded:

- Final game scores.
- Execution time.
- Expanded nodes.
- Evaluated chance outcomes.
- Number of pruned outcomes.

This experiment provides preliminary evidence about the effect of pruning.

## 9.3 Heuristic Evaluation

The baseline and modified heuristic versions were compared over 20 games using seeds 6000–6019.

The experiment measured:

- Average final score.
- Execution time.
- Expanded search nodes.
- Number of identical and different decisions.

A total of 730 decisions were compared.

# 10. Experimental Results

## 10.1 Expectimax vs. Greedy vs. Random

The following results were obtained over 50 games.

| Metric | Expectimax | Greedy | Random |
|---|---:|---:|---:|
| Average score | 240.58 | 218.64 | 47.82 |
| Median score | 234 | 207 | 45 |
| Minimum score | 151 | 133 | 20 |
| Maximum score | 422 | 324 | 138 |
| Average runtime (seconds) | 25.7430 | 1.0855 | 0.0023 |

### Win Distribution

| Agent | Wins |
|---|---:|
| Expectimax | 35 |
| Greedy | 13 |
| Random | 0 |
| Draws | 2 |

### Average Score Differences

- Expectimax vs. Greedy: +21.94 points.
- Expectimax vs. Random: +192.76 points.
- Greedy vs. Random: +170.82 points.

### Analysis

Expectimax achieved the highest average and median scores among the three agents.

It won 35 out of 50 games, while the Greedy agent won 13 games. Two games ended in draws.

These results indicate that probabilistic search provides a substantial performance advantage over the implemented greedy and random baselines in this experiment.

However, Expectimax requires significantly more computation time than the simpler agents.

## 10.2 Pruning Performance

The following results were obtained over five games.

| Metric | Without Pruning | With Pruning |
|---|---:|---:|
| Average final score | 220.80 | 220.80 |
| Runtime (seconds) | 28.41 | 27.43 |
| Expanded nodes | 9,764 | 9,535 |
| Evaluated chance outcomes | 3,330,207 | 3,089,635 |

Additional results:

- Total pruned outcomes: 1,037,044.
- Reduction in evaluated chance outcomes: 7.22%.
- Runtime speedup: approximately 1.04x.
- Expanded-node reduction: approximately 2.35%.

### Analysis

Pruning reduced the number of evaluated chance outcomes by 7.22%.

The average final score remained unchanged in this five-game experiment.

Runtime improved slightly, with an approximate speedup of 1.04x.

These results suggest that pruning reduces search work, although the observed runtime improvement is modest.

Because the experiment contains only five games, the results should be considered preliminary rather than proof of equivalence or performance improvement for every possible game state.

## 10.3 Heuristic Comparison

The baseline and modified heuristic versions were evaluated over 20 games.

| Metric | Baseline | Modified |
|---|---:|---:|
| Average final score | 235.10 | 235.10 |
| Runtime (seconds) | 26.00 | 30.50 |
| Expanded nodes | 9,391 | 9,391 |

### Decision Comparison

| Metric | Result |
|---|---:|
| Total decisions compared | 730 |
| Identical decisions | 730 |
| Different decisions | 0 |

### Analysis

Both heuristic versions produced identical decisions in all 730 comparisons.

They also achieved the same average final score.

Therefore, the modified heuristic did not demonstrate a measurable improvement in decision quality or final score in this experiment.

The modified version also had a higher recorded runtime in this run. Runtime measurements can vary due to execution conditions, so this difference should not be interpreted as proof that the heuristic itself caused the slowdown.

The results indicate that further heuristic refinement and more diverse evaluation states may be necessary to demonstrate a measurable improvement.

# 11. Automated Testing

The project includes automated tests covering the main components:

- Game-state validation.
- Dice probability calculations.
- Scoring rules.
- Game-engine operations.
- Yahtzee bonus and Joker rules.
- Expectimax decision-making.
- Heuristic evaluation.
- Pruning behavior.
- Pruning correctness.
- Greedy agent behavior.
- Strategy generation.

The recorded test execution produced:

**160 passed, 0 failed**

Execution time: approximately 20.72 seconds.

These results demonstrate that the implemented test cases passed successfully. They do not guarantee the absence of every possible defect.

# 12. Limitations

Despite the experimental results, the project has several limitations.

## 12.1 Limited Search Horizon

Expectimax searches decisions within the current turn rather than exploring the complete remaining 13-round game tree.

The heuristic function estimates the future value of the game state after a category is selected.

## 12.2 Heuristic Accuracy

The heuristic uses estimated category values and bonus-related information.

These estimates do not represent an exact solution to the remaining game.

## 12.3 Computational Cost

Expectimax is substantially slower than the Greedy and Random agents.

This is an expected trade-off when using probabilistic search to evaluate possible future outcomes.

## 12.4 Pruning Improvement

Although pruning reduces the number of evaluated chance outcomes, the measured runtime improvement is relatively small.

Further optimization may be necessary to achieve a more significant speedup.

## 12.5 Experimental Sample Size

The pruning experiment uses only five games, while the heuristic experiment uses 20 games.

Larger experiments and additional game states would provide stronger evidence about the general performance of these methods.

# 13. Future Improvements

Possible directions for future development include:

- Improving heuristic evaluation using additional statistical information.
- Evaluating more game seeds and a wider range of game states.
- Investigating more effective pruning bounds.
- Optimizing memoization and state representation.
- Comparing additional search strategies.
- Improving the balance between decision quality and execution time.
- Expanding the JSON interface documentation with additional request and response examples.

# 14. Conclusion

This project demonstrates the implementation of a Yahtzee-playing agent based on Expectimax search.

The experimental comparison showed that Expectimax achieved a higher average score than the implemented Greedy and Random agents over 50 games.

Pruning reduced the number of evaluated chance outcomes by 7.22% in the five-game experiment, with unchanged average scores in that sample.

The heuristic comparison did not show a measurable improvement in final scores or decisions, highlighting the importance of empirical evaluation rather than assuming that a more sophisticated heuristic is necessarily better.

Overall, the project combines game-tree search, probability modeling, heuristic evaluation, pruning, memoization, automated testing, and simulation-based benchmarking in a modular Python implementation.

---

## Project Information

- **Project:** Yahtzee AI Agent
- **Language:** Python 3.11
- **Main Algorithm:** Expectimax
- **Search Optimizations:** Pruning and Memoization
- **Probability Representation:** Python Fraction
- **Testing:** Pytest
- **Evaluation:** Simulation-based benchmarking
- **Repository:** https://github.com/sophiedlk/YahtzeeAI
