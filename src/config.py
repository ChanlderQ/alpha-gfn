import torch
import pandas as pd
import warnings
import duckdb
from datetime import datetime, timedelta
warnings.filterwarnings("ignore")


duck_db_path=r"D:\GitHub\CryptoDune\hyperliq\Qlib_Strategy\crypto_features.duckdb"

# Connect to DuckDB
db_con = duckdb.connect(duck_db_path)

#end_date = datetime(2025, 5, 12)
#timestamp_ms = int(end_date.timestamp() * 1000)
end_date="2025-05-12 00:00:00"

raw_data= db_con.execute(f"SELECT * FROM factor_data where date < TIMESTAMP '{end_date}'").fetchdf()
raw_data.rename(columns={"date":"Date"},inplace=True)
db_con.close()

def compute_forward_return(group):
    # Create a copy to avoid modifying the original
    group = group.copy()
    # Compute forward return
    group["forward_return"] = group["close"].shift(-1) / group["open"].shift(-1) - 1
    return group

def compute_standardized_return(group):
    std = group.std()
    if (std == 0).any():
        return group - group.mean()
    else:
        return (group - group.mean()) / std
    
def generate_forward_data(raw_data,st=True):
    # compute forward ret
    close_data=raw_data[["Date","instrument","close","open"]]
    forward_ret_data=close_data.groupby("instrument", group_keys=False).apply(compute_forward_return)
    forward_ret_data.fillna(0.000001,inplace=True)

    # transfer standardized ret
    forward_ret_data["standardized_forward_return"]=forward_ret_data.groupby('Date', group_keys=False)[["forward_return"]].apply(compute_standardized_return)
    if st:
        FOWARD_RETURN=forward_ret_data.pivot(index="Date",columns="instrument",values="standardized_forward_return")
        
    else:
        FOWARD_RETURN=forward_ret_data.pivot(index="Date",columns="instrument",values="forward_return")
    FOWARD_RETURN.index.name="Date"
    return FOWARD_RETURN

# generate FEATURES and FEATURE_DATA
def generate_feature_data(raw_data):
    features_list=raw_data.drop(columns=["Date","instrument"],axis=1).columns.tolist()
    FEATURES=[]
    FEATURE_DATA={}

    for factor_name in features_list:
        factor_data=raw_data[[factor_name,"Date","instrument"]]
        factor_data.replace(0,0.00000001,inplace=True)
        factor_pivot=factor_data.pivot(index="Date",columns="instrument",values=factor_name)
        factor_pivot.index.name=None
        factor_pivot.reset_index(inplace=True)
        factor_pivot.rename(columns={"index":"Date"},inplace=True)
        factor_pivot.set_index("Date",inplace=True)
        
        FEATURE_DATA[f"${factor_name}"]=factor_pivot
        FEATURES.append(f"${factor_name}")
    return FEATURES,FEATURE_DATA
           
FOWARD_RETURN=generate_forward_data(raw_data)
FEATURES,FEATURE_DATA=generate_feature_data(raw_data)


# Fixed hyperparameters
n_hid_units = 512
n_episodes = 10_000
learning_rate = 3e-3

WINDOW_SIZE = 5 # FUTURE TODO: include window size in action space
MAX_EXPR_LENGTH = 20 # Maximum number of tokens in sequence
RESCALE_FACTOR = 100 # Rescaling factor for reward computation

DEVICE = torch.device('cpu')
'''
if torch.cuda.is_available():
    DEVICE = torch.device('cuda')
else:
    DEVICE = torch.device('cpu')
print(f"Using device: {DEVICE}")
'''
## Action Space
# Begin
BEG = ["BEG"] # encoded as 0
# Operator names
UNARY = ["ops_abs", "ops_log", "ops_roll_std",
         "ops_ts_max","ops_ts_min","ops_ts_rank","ops_decay_linear","ops_prod"] # encoded as 1-3
BINARY = ["ops_add", "ops_subtract", "ops_multiply", "ops_divide", "ops_roll_corr"] # encoded as 4-8
# Features
#FEATURES = ["$open", "$close", "$high", "$low", "$volume"] # encoded as 9-13

# End
SEP = ["SEP"] # encoded as 14

# Complete action space
ACTION_SPACE = BEG + UNARY + BINARY + FEATURES + SEP

## Size of action subspace
SIZE_BEG = len(BEG)
SIZE_UNARY = len(UNARY)
SIZE_BINARY = len(BINARY)
SIZE_FEATURE = len(FEATURES)
SIZE_SEP = len(SEP)

SIZE_ACTION = SIZE_BEG + SIZE_UNARY + SIZE_BINARY + SIZE_FEATURE + SIZE_SEP # = 14

# Start indices of each action subset
OFFSET_BEG = 0
OFFSET_UNARY = OFFSET_BEG + SIZE_BEG # = 1
OFFSET_BINARY = OFFSET_UNARY + SIZE_UNARY # = 4
OFFSET_FEATURE = OFFSET_BINARY + SIZE_BINARY # = 9
OFFSET_SEP = OFFSET_FEATURE + SIZE_FEATURE # = 14

## Import data
'''
FOWARD_RETURN = pd.read_csv("../data/processed/ForwardReturn.csv", index_col=0)

OPEN = pd.read_csv("../data/processed/OPEN.csv", index_col=0)
CLOSE = pd.read_csv("../data/processed/CLOSE.csv", index_col=0)
HIGH = pd.read_csv("../data/processed/HIGH.csv", index_col=0)
LOW = pd.read_csv("../data/processed/LOW.csv", index_col=0)
VOLUME = pd.read_csv("../data/processed/VOLUME.csv", index_col=0)
FEATURE_DATA = {"$open": OPEN, "$close": CLOSE, "$high": HIGH, "$low": LOW, "$volume": VOLUME}
'''
# import from file
