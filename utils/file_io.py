import pandas as pd
import os

def load_stock_pool_from_csv(file_path):
    """
    Load stock codes from a CSV file.
    Expects a column named 'code'.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path)
    if 'code' not in df.columns:
        raise ValueError("CSV file must contain a 'code' column.")
    
    return df['code'].tolist()

def save_results_to_csv(results, filename):
    """
    Save analysis results to a CSV file.
    """
    if not results:
        print("No results to save.")
        return

    df = pd.DataFrame(results)
    # Reorder columns for better readability
    cols = ['date', 'code', 'strategy'] + [c for c in df.columns if c not in ['date', 'code', 'strategy']]
    df = df[cols]
    
    df.to_csv(filename, index=False)
    print(f"\nResults saved to: {filename}")
