# XAGUSD H1 Trading Patterns Research

## 8-Week Research Sprint: Data → Backtesting → Optimized Settings

**Objective:** Research XAGUSD 1H patterns across 2 years of data, discover 3+ optimized settings per pattern, generate adaptive code that works on any asset/timeframe.

**Broker Specs:** Exness Cent Account (0% commission, $0.02-$0.03 friction per oz, max 3 concurrent trades, <15% max DD)

---

## Repository Structure

```
wolf/
├── data/
│   ├── XAGUSD_H1_RAW.csv          [Input: raw 1H data]
│   └── XAGUSD_H1_CLEAN.csv        [Output: cleaned & enriched]
│
├── notebooks/
│   ├── 00_DATA_FOUNDATION.ipynb   [Phase 1-2: Data load & QA]
│   ├── 01_PATTERN_DETECTION.ipynb [Phase 3-4: Pattern discovery]
│   ├── 02_REGIME_ANALYSIS.ipynb    [Phase 5: Market regimes]
│   ├── 03_OPTIMIZATION.ipynb       [Phase 6-7: Parameter optimization]
│   └── 04_RESEARCH_REPORT.ipynb    [Phase 8: Final report]
│
├── src/
│   ├── data_foundation.py          [Data QA classes & ATR calculation]
│   ├── pattern_detector.py         [Pattern A/B/C detection logic]
│   ├── regime_classifier.py        [8-regime market classification]
│   └── backtest_engine.py          [Full backtesting framework]
│
├── reports/
│   ├── 00_baseline_statistics.csv  [Data statistics]
│   ├── 01_volatility_profile.png   [ATR profile chart]
│   ├── 02_pattern_heatmaps.png     [Win rates by regime]
│   ├── 03_optimization_results.csv [Top 3 settings per pattern]
│   └── 04_final_report.ipynb       [Comprehensive findings]
│
├── requirements.txt                [Python dependencies]
└── README_RESEARCH.md              [This file]
```

---

## 8-Phase Execution Plan

### **Phase 1-2: Data Foundation (Week 1-2)**
- ✅ Load XAGUSD_H1_RAW.csv (1000+ H1 candles)
- ✅ Quality checks (OHLC logic, gaps, sessions)
- ✅ Calculate ATR(7, 14, 21, 28)
- ✅ Generate baseline statistics
- **Outputs:** `XAGUSD_H1_CLEAN.csv` + volatility profile

**Key Principle:** Pre-entry regime detection using .shift(1) to avoid lookahead bias

---

### **Phase 3-4: Pattern Detection (Week 2-3)**
- Build 3 pattern detectors (Variant D, Coil Expansion, Booster Trigger)
- Test **BOTH directions** (fade + momentum) for each
- Measure pattern overlap (non-overlapping trade lanes)
- **Outputs:** Signal counts, overlap analysis, trade lane recommendations

**Key Principle:** Separate trade lanes for different patterns (don't merge filters)

---

### **Phase 5: Regime Stratification (Week 3-4)**
- Detect 8 market regimes:
  1. HIGH_VOL_BULL
  2. HIGH_VOL_BEAR
  3. HIGH_VOL_CHOP
  4. LOW_VOL_BULL
  5. LOW_VOL_BEAR
  6. LOW_VOL_CHOP
  7. BREAKOUT_FORMING
  8. CONSOLIDATION

- Assign each signal to ONE regime
- Generate regime heatmaps (win rate per pattern × regime)
- **Outputs:** Regime distribution, heatmaps, signal stratification

**Key Principle:** Use previous 20 candles (shift(20)) for regime detection

---

### **Phase 6: Tier 1 Optimization (Week 4-5)**
- Test each pattern **independently per regime**
- Test all parameters individually:
  - ATR period: [5, 7, 9, 14, 20, 28]
  - Buffer/Band multipliers: [0.5-2.5]
  - Target multipliers: [0.5-3.0]
  - Stop multipliers: [1.5-4.0]
  - Time windows: [12h, 24h, 36h, 48h]
  - Entry timing: [close, next_open]

- Rank by Sharpe Ratio
- Eliminate bottom 20%
- **Outputs:** Parameter rankings per pattern per regime

**Key Metric:** Sharpe Ratio (primary), Profit Factor >1.2 (secondary)

---

### **Phase 7: Tier 2 Combinations & Walk-Forward (Week 5-6)**
- Build 3 settings per pattern per regime:
  1. **Aggressive:** tight stop, wide target, quick time
  2. **Balanced:** medium stop, medium target, standard time
  3. **Conservative:** wide stop, tight target, extended time

- Walk-forward validation (Q1→Q2→Q3→Q4)
- Measure parameter stability
- Stress test: 1% slippage impact
- **Outputs:** 72 configs (3 patterns × 8 regimes × 3 settings)

**Key Principle:** Out-of-sample Sharpe must stay >1.5, profit factor >1.2

---

### **Phase 8: Exhaustive Edge Testing (Week 7)**
- Test exit variations (fixed vs trailing, time vs price)
- Test independent filters (each in separate lane):
  - SMA200 filter
  - ATR median filter
  - Volatility acceleration
  - Session filters
- Measure filter impact on win rate
- **Outputs:** Filter comparison table, lane separation decision

**Key Principle:** Don't stack filters - measure each separately

---

### **Phase 9: Report & Delivery (Week 8)**
- Jupyter notebook with full analysis
- Python module (adaptive, no hard-coding)
- Settings registry (CSV with all 72 configs)
- Recommendations & next steps
- **Outputs:** Final report, code, settings

**Key Deliverables:**
1. `notebooks/04_RESEARCH_REPORT.ipynb` — Complete findings
2. `src/backtest_engine.py` — Reusable backtester
3. `reports/optimal_settings_xagusd_h1.csv` — 72 optimized settings
4. `src/parameter_optimizer.py` — Auto-optimizer (works on any asset)

---

## Critical Research Principles

### ✅ Bidirectional Testing
- Test each pattern as CONTINUATION (momentum follow)
- Test each pattern as REVERSAL (fade)
- Let data decide which works best

### ✅ Exhaustive Exit Testing
- Don't assume industry standard targets/stops are optimal
- Test TARGET × STOP × TIME_WINDOW combinations (all together, not separately)
- Exit immediately when target hit (lock profit)
- Test time-based exits (12h, 24h, 36h, 48h)

### ✅ Pre-Entry Regime Detection (No Lookahead)
- All indicators must use .shift(1) data
- Entry decision completely blind to current candle
- Regime changes don't trigger mid-candle

### ✅ Quality Safeguards
- Check for ATR=0, Volume=0 anomalies
- Validate OHLC logic (High ≥ Low, etc.)
- Stress test with realistic slippage

### ✅ Non-Overlapping Trade Lanes
- Measure pattern overlap (% signals fire together)
- If <15% overlap: keep separate lanes
- If >40% overlap: consolidate with priority rules
- Track this to ensure we don't leave money on table

### ✅ No Hard-Coding
- All parameters externalized
- Auto-detect optimal ATR from data volatility
- Auto-adjust multipliers per regime
- Same code works on EURUSD, ES, BTC, etc.

### ✅ Sharpe Ratio as North Star
- Primary metric: Sharpe Ratio (risk-adjusted)
- Secondary: Profit Factor (must be >1.2)
- Validate: Win rate (avoid 20-loss streaks)
- Check: Average Trade Profit (both absolute $ and multiples of ATR)

---

## Expected Outcomes

### By End of Phase 1-2:
- ✅ Clean dataset ready for backtesting
- ✅ Baseline volatility profile (know if silver is noisy or clean)
- ✅ Data quality report (no anomalies)

### By End of Phase 3-4:
- ✅ Total signal count per pattern
- ✅ Which patterns work best? (fade vs momentum?)
- ✅ Trade lane overlap analysis
- ✅ Decision: trade all 3 simultaneously or sequence?

### By End of Phase 5-6:
- ✅ Which market regimes favor which patterns?
- ✅ Regime frequency (which regimes occur most often?)
- ✅ Top parameter for each (Pattern, Regime)

### By End of Phase 7:
- ✅ 72 final configurations (3 × 8 × 3)
- ✅ Walk-forward degradation measured
- ✅ Parameter stability assessed
- ✅ Out-of-sample performance validated

### By End of Phase 8-9:
- ✅ Every possible edge tested (nothing left on table)
- ✅ Adaptive code that works on any asset
- ✅ Settings registry (copy-paste ready)
- ✅ Confidence: "We tested everything. No assumptions."

---

## Execution Checklist

- [ ] Phase 1: Run `00_DATA_FOUNDATION.ipynb`
- [ ] Confirm: `data/XAGUSD_H1_CLEAN.csv` created
- [ ] Confirm: `reports/01_volatility_profile.png` created
- [ ] Phase 2: Run `01_PATTERN_DETECTION.ipynb`
- [ ] Confirm: Signal counts per pattern
- [ ] Phase 3: Run `02_REGIME_ANALYSIS.ipynb`
- [ ] Confirm: 8 regimes detected, heatmaps generated
- [ ] Phase 4-5: Run `03_OPTIMIZATION.ipynb`
- [ ] Confirm: 72 configs generated
- [ ] Phase 6: Run `04_RESEARCH_REPORT.ipynb`
- [ ] Confirm: Final report generated
- [ ] Deliver: All outputs to `/reports` folder

---

## How to Run

### Setup
```bash
cd wolf
pip install -r requirements.txt
```

### Phase 1
```bash
jupyter notebook
# Open: notebooks/00_DATA_FOUNDATION.ipynb
# Run all cells (Kernel → Restart & Run All)
```

### Phase 2-8
```bash
# After Phase 1 completes, proceed to:
# notebooks/01_PATTERN_DETECTION.ipynb
# notebooks/02_REGIME_ANALYSIS.ipynb
# etc.
```

---

## Key Metrics to Track

| Metric | Calculation | Target | Why |
|--------|-------------|--------|-----|
| **Sharpe Ratio** | (Ret - RFR) / StdDev | >1.5 | Risk-adjusted; best measure of edge |
| **Profit Factor** | Wins / Losses | >1.2 | Shows if winners beat losers |
| **Win Rate %** | Wins / Total | >50% | Avoid long streaks of losses |
| **Avg Trade Profit** | Total Profit / Trades | Positive | Absolute value matters |
| **Max Drawdown** | Peak-to-Trough | <15% | Broker stop-out safety margin |
| **Expected Value** | (Win% × Avg Win) - (Loss% × Avg Loss) | Positive | Long-term profitability |

---

## Contact & Support

**Status:** Research sprint active  
**Start Date:** 2026-05-25  
**Expected Completion:** 2026-07-13 (8 weeks)

For questions or adjustments, refer to research principles above.

---

**Ready to execute Phase 1. All systems go.**
