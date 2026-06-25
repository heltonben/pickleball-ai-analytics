# Pickleball Shot & Rally Analysis

An end-to-end analytics pipeline using data from over 300,000 professional and competitive pickleball shots, combining SQL, predictive modeling, and AI-generated insights. Built as a portfolio project tied to my former role as Treasurer of the University of Tennessee Pickleball Club, applying the same exploratory-to-predictive workflow used in financial analysis (data validation, trend analysis, predictive modeling, stakeholder-ready reporting) to a new domain.

Built using Claude as a coding and analysis tool; all modeling decisions, validation, and data interpretation below are my own.

**Live Dashboard:** [Tableau Public](https://public.tableau.com/app/profile/ben.helton/viz/PickleballShotRallyAnalysis/PickleballShotRallyAnalysis?publish=yes)

## Data Source

[Kaggle's PKLMarts Competitive Pickleball Extracts](https://www.kaggle.com/datasets/cakesofspan/pklmarts-competitive-pickleball-extracts/data), a relational dataset of 7 tables covering 936 games, 40,703 rallies, and 304,650 shots across skill levels from 2.5 through Pro.

## Project Structure

| File | Purpose |
|---|---|
| `load_data.py` | Loads the 7 raw CSVs into a queryable SQLite database (`pickleball.db`) |
| `explore.sql` | Exploratory SQL queries used to investigate rally length, outcome distribution, and shot type patterns |
| `heatmap.py` | Generates shot location heatmaps (all shots and winning shots only) using matplotlib |
| `make_court.py` | Generates a to-scale pickleball half-court diagram, used as a background reference image for the Tableau heatmap |
| `model.py` | Builds and evaluates a logistic regression model predicting rally outcome (winner vs. error) |
| `export_for_tableau.py` | Exports cleaned, query-ready CSVs for the Tableau dashboard |
| `scouting_report.py` | Generates a single AI scouting report for one shot type via the Anthropic API (accepts a shot type as a command-line argument) |
| `scouting_report_batch.py` | Generates and saves AI scouting reports for every shot type in the dataset |
| `scouting_reports/` | Output folder containing the generated scouting reports |

## Setup

1. Clone this repository and install dependencies:
   ```
   pip install pandas matplotlib scikit-learn python-dotenv anthropic
   ```
2. Download the dataset from the Kaggle link above and place the CSVs in a `pickleballdata/` folder.
3. Create a `.env` file in the project root with your own Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```
4. Run `load_data.py` first to build the database, then run any of the other scripts.

## What I Built

- **Data Pipeline**: Loaded and joined a 7-table relational dataset into a queryable SQLite database.
- **Exploratory Analysis**: Identified rally length and outcome trends by skill level using SQL, including multi-table joins, subqueries, and window functions.
- **Spatial Analysis**: Built shot location heatmaps in Python and Tableau, validated against real court dimensions. Caught and corrected a data interpretation error: shot coordinates are recorded from the hitting player's perspective rather than fixed court position, which initially made the heatmap look asymmetric until traced back to the dataset's data dictionary.
- **Predictive Modeling**: Built a logistic regression model predicting whether a rally ends in a winner or an error, using rally length, shot type, and shot location as features (80/20 train/test split). Applied class weighting after the initial model favored the majority class.
- **AI Integration**: Used the Anthropic API to generate natural language scouting reports from shot statistics. Revised the prompt after the first version presented all skill levels with equal confidence regardless of sample size; the final version explicitly flags any group under 30 shots as statistically unreliable.

## Key Findings

- Average rally length increases steadily with skill level, from 4.2 shots at the 2.5 level to 10.1 shots at the Pro level.
- A naive baseline (always predicting the majority outcome) achieves 66% accuracy. The initial model reached 71% accuracy but caught only 41% of actual winning shots. Applying class weighting traded overall accuracy for recall, catching 78% of winning shots at lower precision, a tradeoff worth understanding before treating headline accuracy as the right metric.
- Defensive Reset shots end rallies in a winner 48% of the time, nearly matching aggressive Speed Up shots (54%), suggesting that neutralizing an opponent's attack can be as effective as attacking directly.
- A concentrated cluster of shots struck 1 to 2 feet from the net, dominated by Hand Battle and Dink shots, reflects the close-quarter net exchanges that decide many competitive points.

## Known Data Limitations

- The dataset's shot type reference table includes a defined category for "Overhead" shots, but no shots in the actual dataset (n=304,650) were tagged with this type, despite overhead smashes being common in real competitive play. This likely reflects a labeling gap or that these shots were captured under an adjacent category.
- Shot coordinates are recorded relative to the hitting player's own perspective (net and baseline distance), not as absolute court position. This is documented in the dataset's data dictionary but is easy to misinterpret without it.

## Reflection

This project let me apply SQL, Python, predictive modeling, and AI-assisted development to a real, messy dataset from start to finish. I used Claude to accelerate the coding work, but the analytical judgment was mine: deciding which baseline to check the model against, catching the coordinate system error before it undermined the spatial analysis, and rewriting the AI prompt after spotting that it was treating small and large samples with equal confidence. That habit of validating results and checking claims against a baseline, rather than accepting the first output, whether from the data or from an AI tool, is the same instinct I'd bring to financial analysis work.
