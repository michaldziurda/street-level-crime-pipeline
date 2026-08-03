from pathlib import Path
import pandas as pd
import numpy as np

from utils.config import Config
from utils.function_timer import function_timer
from utils.ensure_paths import ensure_paths

@function_timer
def preprocess_eurostat_data(config: Config):
    df_codes = pd.read_csv(config.iccs_code_table, sep='\t')
    dfc = df_codes[['Code', 'Label']].set_index('Code')
    iccs_lookup_dict = dfc['Label'].to_dict()

    for f in Path(config.output_dir_raw).iterdir():
        if '.tsv' in str(f) or '.csv' in str(f):
            separator = "\t" if ".tsv" in str(f) else ","
            df = pd.read_csv(f, sep=separator)
            
            # Initial columns are merged into 1. Therefore splitting and dropping useless freq
            cols = ["freq", "iccs", "unit", "geo"]
            df[cols] = df['freq,iccs,unit,geo'].str.split(pat=",", expand=True)
            cols.extend(df.filter(regex="[0-9]{4}").columns)
            cols.remove('freq')
            df = df[cols]
            df.columns = [c.strip() for c in df.columns] # there is tailing space included in some values
            df = df.replace(": *", np.nan, regex=True)
            
            # Initial file contains consecutive years as seaparate column. Reshaping df to have years as a single column
            df = pd.melt(df, id_vars=['iccs', 'unit', 'geo'], value_vars=df.filter(regex="[0-9]{4}").columns, var_name='year', value_name='crime_count')
            df['crime_count'] = pd.to_numeric(df['crime_count'], errors='coerce')

            # Assign an id for unique tracking
            df['id'] = df[['iccs', 'unit', 'geo', 'year']].apply(lambda row: "_".join(row), axis=1)

            # Recoding values into more meaningful strings
            df['unit'] = df['unit'].apply(lambda x: 'Absolute numbers' if x == 'NR' else 'Per 100000 inhabitants' if x == 'P_HTHAB' else "Unknown")

            # Decoding iccs codes 
            df['iccs'] = df['iccs'].apply(lambda x: iccs_lookup_dict[x.replace('ICCS', '')])

            df['year'] = df['year'].astype(int)

            # Rename geo for easier understanding
            df.rename({'geo': 'country'}, axis=1, inplace=True)
            
            save_path = Path(config.output_dir_processed, f"{str(f.name).split('.')[0]}.parquet")
            
            df.to_parquet(save_path)


if __name__ == '__main__':
    config = Config(Path("config/eu_crime/config_eurostat.yml"))
    ensure_paths(config.output_dir_processed)
    preprocess_eurostat_data(config)
    