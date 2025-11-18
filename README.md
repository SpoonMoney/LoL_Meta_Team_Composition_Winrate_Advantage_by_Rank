# LoL_Meta_Team_Composition_Winrate_Advantage_by_Rank
This is a personal project that uses the Riot Games API and Python to analyze how much of an advantage does the team with the higher win rate champions have over a team with "less meta" champions. The data was collected during LoL Patch 25.22 and is presented with a graph made in Tableau.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Library-Pandas-150458)
![Tableau](https://img.shields.io/badge/Visualization-Tableau-E97627)
![Riot API](https://img.shields.io/badge/Data-Riot_Games_API-D32936)

### Project Overview
This project analyzes the statistical effectiveness of "Meta" team compositions across different competitive ranks in *League of Legends*.

Using the **Riot Games API**, I collected match data from **Iron to Diamond**, engineered a custom "Meta Score" for every champion, and calculated the **Net Win Rate Advantage** gained by teams with statistically stronger compositions.

**The Core Question:** *Do team compositions that consist of more "Meta" champions win games more in low ELO (Iron/Silver) or high ELO (Diamond)?*

---

### Key Findings

> **The "Meta Advantage" is real, but it diminishes with skill.**

My analysis reveals that playing a "Meta" composition provides a significant statistical edge, but that edge is not uniform across all ranks.

* **The Silver Peak:** The advantage peaks in **Silver**, where playing a Meta comp provides a **~12.6% Net Win Rate Advantage** over an off-meta comp.
* **The Diamond Drop-off:** As player skill increases, the advantage shrinks significantly (dropping to **~6.8%** in Diamond).
* **Conclusion:** In lower ranks, champion strength acts as a crutch for mechanical skill. In higher ranks, player mastery and counter-picks begin to outweigh raw statistical power.

---

### Visualization

**[Click Here to Interact with the Live Dashboard on Tableau Public](YOUR_TABLEAU_PUBLIC_LINK_HERE)**

*(Below is a static preview of the Net Advantage analysis)*

![Net Meta Advantage Chart](./image_0968f3.png)
*Figure 1: The "Net Advantage" chart normalizes win rates against a 0% baseline. A positive bar indicates how much MORE often the Meta team wins compared to the Off-Meta team.*

---

### Methodology & Feature Engineering

To avoid relying on subjective external tier lists, I derived "Meta" strictly from the performance data within the dataset.

#### 1. Defining "Meta Score" (Champion Level)
I calculated the raw win rate for every champion across the entire dataset.
$$\text{Meta Score} = \frac{\text{Total Wins}}{\text{Total Matches Played}}$$

#### 2. Defining "Team Meta Strength" (Match Level)
I aggregated the scores of all 5 champions on a team to create a composite score for that specific lineup.
$$\text{Team Score} = \sum (\text{Top} + \text{Jungle} + \text{Mid} + \text{ADC} + \text{Support})$$

#### 3. Calculating "Net Advantage" (The Metric)
Instead of plotting raw win rates (which hover around 50% due to the game's zero-sum nature), I calculated the **Net Advantage**:
$$\text{Net Advantage} = \text{Meta Team Win Rate} - \text{Off Meta Team Win Rate}$$
*Example:* If Meta teams win 56% of the time, the Off-Meta team wins 44% of the time.
56%−44%=+12% Advantage

---

### Tech Stack & Tools

* **Data Collection:** Python (`requests`) to interface with the Riot Games API (`LEAGUE-V4`, `MATCH-V5`).
* **Data Engineering:** Python (`pandas`) to clean JSON data, flatten nested structures, and handle rate limiting/error logging.
* **Analysis:** Aggregated win rates by Rank and calculated win differentials.
* **Visualization:** Tableau for the final dashboard (Calculated Fields used for Net Advantage logic).

### How to Run This Project

1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/SpoonMoney/lol-meta-analysis.git](https://github.com/SpoonMoney/lol-meta-analysis.git)
    ```
2.  **Install dependencies:**
    ```bash
    pip install pandas requests seaborn
    ```
3.  **Get an API Key:**
    Get a development key from the [Riot Developer Portal](https://developer.riotgames.com/).
4.  **Run the Script:**
    Update `API_KEY` in `data_collection.py` and run the script.
    ```bash
    python data_collection.py
    ```

---

### Future Improvements
* **Patch Versioning:** Filter data by specific patches (e.g., 14.1 vs 14.2) to see how balance changes affect the "Meta Advantage."
* **Role-Specific Analysis:** Analyze if having a "Meta" Jungler is more impactful than having a "Meta" Support.
* **Machine Learning:** Train a Logistic Regression model to predict the winner of a match based solely on the pre-game draft.
