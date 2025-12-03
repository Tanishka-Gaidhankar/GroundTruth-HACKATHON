import pandas as pd
import os
from typing import List, Dict, Tuple

class DataPipeline:
    """
    Step 1: Load and combine multiple CSV files into standardized format
    Flexible: Works with any CSV filename
    """
    
    def __init__(self, upload_paths: Dict[str, str]):
        """
        Initialize with upload paths from Flask
        upload_paths: dict like {"any_name.csv": "/path/to/file.csv", ...}
        """
        self.upload_paths = upload_paths
        self.dataframes = {}
        self.combined_df = None
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load a single CSV file"""
        try:
            df = pd.read_csv(file_path)
            print(f"✓ Loaded {file_path}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            print(f"✗ Error loading {file_path}: {e}")
            return None
    
    def load_multiple_csvs(self, file_paths: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """Load multiple CSV files from upload_paths dict"""
        for name, file_path in file_paths.items():
            df = self.load_csv(file_path)
            if df is not None:
                self.dataframes[name] = df
        
        return self.dataframes
    
    def merge_all_data(self) -> pd.DataFrame:
        """
        Load and merge all uploaded CSV files
        Works with ANY filename - just uses first CSV uploaded
        """
        # Load all CSVs
        self.load_multiple_csvs(self.upload_paths)
        
        if not self.dataframes:
            raise ValueError("No CSV files loaded successfully")
        
        # Use first CSV file (works with any name)
        self.combined_df = list(self.dataframes.values())[0]
        
        self.combined_df.columns = self.combined_df.columns.str.lower()
        
        # Ensure date column is datetime if it exists
        if 'date' in self.combined_df.columns:
          self.combined_df['date'] = pd.to_datetime(
          self.combined_df['date'], 
          format='mixed', 
          dayfirst=True,
          errors='coerce'
    )
        
        print(f"\n✓ Combined dataframe: {len(self.combined_df)} rows")
        print(f"✓ Columns: {list(self.combined_df.columns)}")
        
        return self.combined_df
    
    def get_info(self) -> Dict:
        """Get summary of loaded data"""
        return {
            'files_loaded': list(self.dataframes.keys()),
            'total_rows': len(self.combined_df) if self.combined_df is not None else 0,
            'columns': list(self.combined_df.columns) if self.combined_df is not None else []
        }
    
    def standardize_columns(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Rename columns to standard schema
        column_mapping: {'old_name': 'new_name', ...}
        """
        df = df.rename(columns=column_mapping)
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare data:
        - Convert date to datetime
        - Fill NaN with 0 for numeric columns
        - Remove completely empty rows
        """
        # Find date columns and convert
        date_cols = ['date', 'Date', 'DATE']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Fill NaN in numeric columns with 0
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        return df
    
    def combine_dataframes(self, join_key: str = 'date') -> pd.DataFrame:
        """
        Merge all dataframes on a common key (usually 'date')
        """
        if not self.dataframes:
            print("✗ No dataframes to combine")
            return None
        
        dfs_list = list(self.dataframes.values())
        
        # Start with first dataframe
        combined = dfs_list[0].copy()
        
        # Left join all subsequent dataframes
        for df in dfs_list[1:]:
            if join_key in df.columns and join_key in combined.columns:
                combined = combined.merge(df, on=join_key, how='left')
            else:
                # If no common key, just concatenate
                combined = pd.concat([combined, df], axis=1)
        
        # Remove duplicate columns
        combined = combined.loc[:, ~combined.columns.duplicated()]
        
        self.combined_df = combined
        print(f"✓ Combined dataset: {len(combined)} rows, {len(combined.columns)} columns")
        
        return combined
    
    def get_data_summary(self) -> Dict:
        """
        Get basic stats about the combined dataset
        """
        if self.combined_df is None:
            return None
        
        summary = {
            'total_rows': len(self.combined_df),
            'total_columns': len(self.combined_df.columns),
            'columns': list(self.combined_df.columns),
            'dtypes': self.combined_df.dtypes.to_dict(),
            'missing_values': self.combined_df.isnull().sum().to_dict(),
            'numeric_summary': self.combined_df.describe().to_dict()
        }
        
        return summary
    
    def save_combined_csv(self, output_path: str = 'combined_data.csv') -> str:
        """
        Save combined dataframe to CSV
        """
        if self.combined_df is None:
            print("✗ No combined data to save")
            return None
        
        self.combined_df.to_csv(output_path, index=False)
        print(f"✓ Saved combined data to {output_path}")
        
        return output_path
