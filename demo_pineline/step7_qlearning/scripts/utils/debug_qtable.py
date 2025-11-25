import pickle
import json

with open('models/qtable.pkl', 'rb') as f:
    data = pickle.load(f)

q_table = data['q_table']
config = data['config']
stats = data['stats']

# ===== IN Q-TABLE =====
print("\n================ Q-TABLE ================\n")
for state, actions in q_table.items():
    print(f"State: {state}")
    for action, q_value in actions.items():
        print(f"  Action {action}: {q_value}")
    print("-" * 50)

# ===== IN CONFIG =====
print("\n================ CONFIG ================\n")
print(json.dumps(config, indent=2, ensure_ascii=False))

# ===== IN STATS =====
print("\n================ STATS ================\n")
print(json.dumps(stats, indent=2, ensure_ascii=False))