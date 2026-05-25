"""
XAGUSD H1 Trading Patterns Research
Phase 1: Data Foundation & Quality Assurance

Core module for data loading, validation, ATR calculation, and session classification.
Reusable across all backtesting phases.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class DataQualityValidator:
    """Validates OHLC data for logic errors and anomalies."""
    
    def __init__(self, df):
        self.df = df.copy()
        self.report = {}
        
    def validate_ohlc_logic(self):
        """Check for fundamental OHLC errors."""
        errors = {
            'high_lt_low': (self.df['high'] < self.df['low']).sum(),
            'close_outside_hl': ((self.df['close'] > self.df['high']) | 
                                (self.df['close'] < self.df['low'])).sum(),
            'open_outside_hl': ((self.df['open'] > self.df['high']) | 
                               (self.df['open'] < self.df['low'])).sum(),
            'zero_range': ((self.df['open'] == self.df['high']) & 
                          (self.df['high'] == self.df['low']) & 
                          (self.df['low'] == self.df['close'])).sum(),
            'zero_volume': (self.df['volume'] == 0).sum()
        }
        self.report['ohlc_errors'] = errors
        return errors
    
    def detect_gaps(self):
        """Identify missing candles (gaps in timestamp sequence)."""
        gaps = []
        for i in range(1, len(self.df)):
            delta = self.df['timestamp'].iloc[i] - self.df['timestamp'].iloc[i-1]
            if delta > pd.Timedelta(hours=1):
                gaps.append({
                    'from': self.df['timestamp'].iloc[i-1],
                    'to': self.df['timestamp'].iloc[i],
                    'hours': int(delta.total_seconds() / 3600)
                })
        self.report['gaps'] = gaps
        return gaps
    
    def get_report(self):
        """Return full validation report."""
        return self.report


class ATRCalculator:
    """Calculates Average True Range for multiple periods."""
    
    @staticmethod
    def calculate_tr(df):
        """Calculate True Range."""
        df = df.copy()
        high_low = df['high'] - df['low']
        high_pc = abs(df['high'] - df['close'].shift(1))
        low_pc = abs(df['low'] - df['close'].shift(1))
        tr = high_low.combine(high_pc, max).combine(low_pc, max)
        tr.iloc[0] = high_low.iloc[0]  # First row: just high-low
        return tr
    
    @staticmethod
    def calculate_atr(df, periods=[7, 14, 21, 28]):
        """Calculate ATR for multiple periods (SMA-based)."""
        df = df.copy()
        df['true_range'] = ATRCalculator.calculate_tr(df)
        
        for period in periods:
            df[f'ATR_{period}'] = df['true_range'].rolling(window=period).mean()
        
        return df


class SessionClassifier:
    """Classifies trading sessions based on UTC hour and day of week."""
    
    @staticmethod
    def classify_session(timestamp):
        """Classify a single timestamp into a trading session."""
        hour = timestamp.hour
        dow = timestamp.weekday()  # 0=Mon, 5=Sat, 6=Sun
        
        if dow >= 5:
            return 'WEEKEND'
        elif 7 <= hour < 16:
            return 'LONDON'
        elif 12 <= hour < 21:
            return 'US'
        else:
            return 'ASIA'
    
    @staticmethod
    def add_session_column(df):
        """Add session classification to dataframe."""
        df = df.copy()
        df['session'] = df['timestamp'].apply(SessionClassifier.classify_session)
        df['hour_utc'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['is_weekend'] = df['timestamp'].dt.weekday >= 5
        return df


class DataCleaner:
    """Prepares data for backtesting by calculating derived metrics."""
    
    @staticmethod
    def enrich_candle_metrics(df):
        """Calculate candle body, wick, and range metrics."""
        df = df.copy()
        df['candle_range'] = df['high'] - df['low']
        df['candle_body'] = abs(df['close'] - df['open'])
        df['candle_wick_upper'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['candle_wick_lower'] = df[['open', 'close']].min(axis=1) - df['low']
        return df
    
    @staticmethod
    def remove_warmup(df, warmup_period=30):
        """Remove initial rows before ATR converges."""
        return df[df.index >= warmup_period].reset_index(drop=True)
    
    @staticmethod
    def select_backtest_columns(df):
        """Select essential columns for backtesting."""
        essential_cols = [
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'true_range', 'candle_range', 'candle_body',
            'candle_wick_upper', 'candle_wick_lower',
            'ATR_7', 'ATR_14', 'ATR_21', 'ATR_28',
            'session', 'hour_utc', 'day_of_week'
        ]
        available_cols = [c for c in essential_cols if c in df.columns]
        return df[available_cols]


def run_foundation_analysis(input_path, output_dir):
    """
    Complete Phase 1 data foundation pipeline.
    
    Args:
        input_path (str): Path to raw CSV file
        output_dir (str): Directory for output files
    
    Returns:
        dict: Results summary
    """
    
    print("\n" + "="*70)
    print("XAGUSD H1 DATA FOUNDATION - PHASE 1")
    print("="*70)
    
    # Step 1: Load data
    print("\n[1/5] Loading raw data...")
    df = pd.read_csv(input_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    print(f"  ✓ Loaded {len(df)} candles ({df['timestamp'].min()} to {df['timestamp'].max()})")
    
    # Step 2: Quality validation
    print("\n[2/5] Quality validation...")
    validator = DataQualityValidator(df)
    ohlc_errors = validator.validate_ohlc_logic()
    gaps = validator.detect_gaps()
    print(f"  ✓ OHLC errors: {sum(ohlc_errors.values())}")
    print(f"  ✓ Gaps detected: {len(gaps)}")
    
    # Step 3: Calculate ATR
    print("\n[3/5] Calculating ATR...")
    df = ATRCalculator.calculate_atr(df, periods=[7, 14, 21, 28])
    print(f"  ✓ ATR(7, 14, 21, 28) calculated")
    
    # Step 4: Session classification
    print("\n[4/5] Classifying sessions...")
    df = SessionClassifier.add_session_column(df)
    session_dist = df['session'].value_counts()
    print(f"  ✓ Sessions detected:")
    for session, count in session_dist.items():
        print(f"    - {session}: {count} ({100*count/len(df):.1f}%)")
    
    # Step 5: Data enrichment & cleaning
    print("\n[5/5] Enriching metrics and removing warmup...")
    df = DataCleaner.enrich_candle_metrics(df)
    df_clean = DataCleaner.remove_warmup(df, warmup_period=30)
    df_clean = DataCleaner.select_backtest_columns(df_clean)
    print(f"  ✓ {len(df_clean)} clean candles ready for backtesting")
    
    # Save clean data
    output_path = f"{output_dir}/XAGUSD_H1_CLEAN.csv"
    df_clean.to_csv(output_path, index=False)
    print(f"  ✓ Saved to {output_path}")
    
    # Summary statistics
    atr14 = df_clean['ATR_14'].dropna()
    summary = {
        'total_candles': len(df_clean),
        'date_range': f"{df_clean['timestamp'].min()} to {df_clean['timestamp'].max()}",
        'atr14_mean': atr14.mean(),
        'atr14_median': atr14.median(),
        'atr14_std': atr14.std(),
        'price_min': df_clean['low'].min(),
        'price_max': df_clean['high'].max(),
        'price_mean': df_clean['close'].mean(),
    }
    
    print("\n" + "="*70)
    print("BASELINE STATISTICS")
    print("="*70)
    print(f"Total Candles (clean)............ {summary['total_candles']}")
    print(f"Date Range....................... {summary['date_range']}")
    print(f"Price Min........................ ${summary['price_min']:.2f}")
    print(f"Price Max........................ ${summary['price_max']:.2f}")
    print(f"Price Mean....................... ${summary['price_mean']:.2f}")
    print(f"ATR(14) Mean..................... ${summary['atr14_mean']:.4f}")
    print(f"ATR(14) Median................... ${summary['atr14_median']:.4f}")
    print(f"ATR(14) Std Dev.................. ${summary['atr14_std']:.4f}")
    print("="*70)
    
    return summary


if __name__ == "__main__":
    # Example usage
    run_foundation_analysis(
        input_path='../data/XAGUSD_H1_RAW.csv',
        output_dir='../data'
    )
