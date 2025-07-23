from decimal import Decimal
import numpy as np

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    elif isinstance(obj, (Decimal, np.float64, np.float32, np.int64, np.int32)):
        return float(obj)
    else:
        return obj