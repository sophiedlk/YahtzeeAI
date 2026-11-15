# Yahtzee AI Agent — Evaluation Report

## 1. Introduction

This project implements an intelligent agent for the Yahtzee dice game using the Expectimax search algorithm.

The agent evaluates possible dice-keeping and reroll actions, considers probabilistic dice outcomes, and selects a scoring category based on the current game state.

The main objectives of this project are:

- Implement a complete 13-round Yahtzee game.
- Develop an Expectimax-based decision-making agent.
- Model dice outcomes using exact probabilities.
- Improve search efficiency using pruning and memoization.
- Evaluate the agent against alternative strategies.
- Analyze the effectiveness and limitations of the implemented optimizations.

## 2. System Architecture

The project is organized into several modules, each responsible for a specific part of the system.

| Module | Responsibility |
|---|---|
| `game_state.py` | Represents and validates the game state. |
| `scoring.py` | Calculates scores for all Yahtzee categories. |
| `game_engine.py` | Handles rerolls and scoring operations. |
| `dice_probability.py` | Generates possible dice outcomes and their probabilities. |
| `strategy.py` | Generates legal dice-keeping actions. |
| `expectimax.py` | Implements Expectimax search and decision-making. |
| `heuristic.py` | Estimates the value of non-terminal game states. |
| `pruning.py` | Reserved module; pruning is implemented in `expectimax.py`. |
| `greedy_agent.py` | Implements a greedy baseline agent. |
| `simulation.py` | Runs complete game simulations. |
| `json_interface.py` | Processes JSON-based requests. |
| `main.py` | Provides the main program entry point. |

### 2.1 Expectimax Search

The main decision-making algorithm is Expectimax.

It uses two types of nodes:

- **Max nodes:** Select the action with the highest expected value.
- **Chance nodes:** Calculate the expected value of possible dice outcomes using their probabilities.

The search evaluates decisions within the current turn. After selecting a scoring category, a heuristic function estimates the value of the resulting game state rather than searching the entire remaining game tree.

### 2.2 Probability Model

Dice outcomes are generated using combinations with replacement.

The implementation uses exact probabilities represented by Python's `Fraction` type. This avoids floating-point approximation errors when calculating the probabilities of unordered dice outcomes.

### 2.3 Search Optimizations

Two optimizations are implemented:

- **Pruning:** An optimistic upper bound is used to eliminate chance outcomes that cannot improve the current best decision.
- **Memoization:** Previously evaluated states are cached to avoid repeated calculations.

These optimizations aim to reduce unnecessary search work while preserving the selected action in the tested cases.

### 2.4 Heuristic Evaluation

The heuristic estimates the value of a non-terminal game state using information such as:

- Current accumulated score.
- Expected values of unfilled scoring categories.
- The possibility of obtaining the upper-section bonus.

The upper-section bonus is not counted again once it has already been earned.

## 3. Experimental Methodology

The agent was evaluated through simulation experiments.

The experiments focused on three main questions:

1. How does Expectimax perform compared with simpler agents?
2. How much computational work does pruning eliminate?
3. Does the modified heuristic improve the agent's decisions or final scores?

### 3.1 Agent Comparison

Three agents were evaluated:

- Expectimax
- Greedy
- Random

All agents played using the same set of 50 game seeds, from 3000 to 3049.

The evaluation metrics included:

- Average final score.
- Median final score.
- Minimum and maximum scores.
- Average execution time.
- Number of wins and draws.

### 3.2 Pruning Evaluation

The pruning experiment compared Expectimax with pruning enabled and disabled.

Five games were simulated using seeds 4000 to 4004.

The following metrics were recorded:

- Final game scores.
- Execution time.
- Expanded nodes.
- Evaluated chance outcomes.
- Number of pruned outcomes.

This is a preliminary evaluation based on a small sample of games.

### 3.3 Heuristic Evaluation

The baseline and modified heuristic versions were compared over 20 games using seeds 6000 to 6019.

The experiment measured:

- Average final score.
- Execution time.
- Expanded search nodes.
- Number of identical and different decisions.

A total of 730 decisions were compared.

## 4. Experimental Results

### 4.1 Expectimax vs. Greedy vs. Random

The following results were obtained over 50 games.

| Metric | Expectimax | Greedy | Random |
|---|---:|---:|---:|
| Average score | 240.58 | 218.64 | 47.82 |
| Median score | 234 | 207 | 45 |
| Minimum score | 151 | 133 | 20 |
| Maximum score | 422 | 324 | 138 |
| Average runtime (seconds) | 25.7430 | 1.0855 | 0.0023 |

Win distribution:

| Agent | Wins |
|---|---:|
| Expectimax | 35 |
| Greedy | 13 |
| Random | 0 |
| Draws | 2 |

Average score differences:

- Expectimax vs. Greedy: +21.94 points.
- Expectimax vs. Random: +192.76 points.
- Greedy vs. Random: +170.82 points.

**Analysis**

Expectimax achieved the highest average and median scores among the three agents.

It won 35 out of 50 games, while the Greedy agent won 13 games. Two games ended in draws.

These results indicate that probabilistic search provides a substantial performance advantage over the implemented greedy and random baselines in this experiment.

However, Expectimax requires significantly more computation time than the simpler agents.

### 4.2 Pruning Performance

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

**Analysis**

Pruning reduced the number of evaluated chance outcomes by 7.22%.

The average final score remained unchanged in this five-game experiment. Runtime improved slightly, with an approximate speedup of 1.04x.

The results suggest that pruning reduces search work, although the observed runtime improvement is modest.

Because the experiment contains only five games, these results should be considered preliminary rather than proof of equivalence or performance improvement for every possible game state.

### 4.3 Heuristic Comparison

The baseline and modified heuristic versions were evaluated over 20 games.

| Metric | Baseline | Modified |
|---|---:|---:|
| Average final score | 235.10 | 235.10 |
| Runtime (seconds) | 26.00 | 30.50 |
| Expanded nodes | 9,391 | 9,391 |

Decision comparison:

| Metric | Result |
|---|---:|
| Total decisions compared | 730 |
| Identical decisions | 730 |
| Different decisions | 0 |

**Analysis**

Both heuristic versions produced identical decisions in all 730 comparisons.

They also achieved the same average final score.

Therefore, the modified heuristic did not demonstrate a measurable improvement in decision quality or final score in this experiment.

The modified version also had a higher recorded runtime in this run. Runtime measurements can vary due to execution conditions, so this difference should not be interpreted as proof that the heuristic itself caused the slowdown.

The results indicate that further heuristic refinement and more diverse evaluation states may be necessary to demonstrate a measurable improvement.

## 5. Automated Testing

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

## 6. Limitations

Despite the results, the project has several limitations.

### 6.1 Limited Search Horizon

Expectimax searches decisions within the current turn rather than exploring the complete 13-round game tree.

The heuristic function estimates the future value of the game state after a category is selected.

### 6.2 Heuristic Accuracy

The heuristic uses estimated category values and bonus-related information.

These estimates do not represent an exact solution to the remaining game.

### 6.3 Computational Cost

Expectimax is substantially slower than Greedy and Random agents.

This is an expected trade-off when using probabilistic search to evaluate possible future outcomes.

### 6.4 Pruning Improvement

Although pruning reduces the number of evaluated chance outcomes, the measured runtime improvement is relatively small.

Further optimization may be necessary to achieve a more significant speedup.

### 6.5 Experimental Sample Size

The pruning experiment uses only five games, while the heuristic experiment uses 20 games.

Larger experiments and additional game states would provide stronger evidence about the general performance of these methods.

## 7. Future Improvements

Possible directions for future development include:

- Improving heuristic evaluation using additional statistical information.
- Evaluating more game seeds and a wider range of game states.
- Investigating more effective pruning bounds.
- Optimizing memoization and state representation.
- Comparing additional search strategies.
- Improving the balance between decision quality and execution time.

## 8. Conclusion

This project demonstrates the implementation of a Yahtzee-playing agent based on Expectimax search.

The experimental comparison showed that Expectimax achieved a higher average score than the implemented Greedy and Random agents over 50 games.

Pruning reduced the number of evaluated chance outcomes by 7.22% in the five-game experiment, with unchanged average scores in that sample.

The heuristic comparison did not show a measurable improvement in final scores or decisions, highlighting the importance of empirical evaluation rather than assuming that a more sophisticated heuristic is necessarily better.

Overall, the project combines game-tree search, probability modeling, heuristic evaluation, pruning, memoization, automated testing, and simulation-based benchmarking in a modular Python implementation.

---

**Project:** Yahtzee AI Agent  
**Language:** Python 3.11  
**Main Algorithm:** Expectimax  
**Evaluation:** Simulation-based benchmarking and automated testing  
**Repository:** https://github.com/sophiedlk/YahtzeeAI
