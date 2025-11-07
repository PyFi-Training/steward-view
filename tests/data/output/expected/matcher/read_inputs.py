from decimal import Decimal
from pathlib import Path
import pandas as pd

input_data_dir = Path(__file__).resolve().parents[3] / 'input'/ 'matcher'
pmts           = pd.read_csv(input_data_dir / 'payments.csv'         , converters={'amount': Decimal, 'date': lambda x: pd.to_datetime(x).date()})
pmts_filtered  = pd.read_csv(input_data_dir / 'payments_filtered.csv', converters={'amount': Decimal, 'date': lambda x: pd.to_datetime(x).date()})
prods          = pd.read_csv(input_data_dir / 'products.csv'         , converters={'amount': Decimal, 'date': pd.to_datetime                    })