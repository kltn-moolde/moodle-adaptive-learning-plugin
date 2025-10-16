import matplotlib.pyplot as plt
import pandas as pd
import json
from pathlib import Path

def plot_training(history_path):
    with open(history_path, "r") as f:
        history = json.load(f)
    rewards = history["episode_rewards"]
    q_values = history["avg_q_values"]
    lengths = history["episode_lengths"]

    fig, axs = plt.subplots(3, 1, figsize=(8, 10))
    axs[0].plot(rewards, marker='o')
    axs[0].set_title("Episode Rewards")
    axs[0].set_ylabel("Avg Reward")
    axs[0].set_xlabel("Epoch")

    axs[1].plot(q_values, marker='o', color='orange')
    axs[1].set_title("Average Q-Value")
    axs[1].set_ylabel("Avg Q-Value")
    axs[1].set_xlabel("Epoch")

    axs[2].plot(lengths, marker='o', color='green')
    axs[2].set_title("Episode Lengths")
    axs[2].set_ylabel("Avg Length")
    axs[2].set_xlabel("Epoch")

    plt.tight_layout()
    plt.show()

def plot_grade_distribution(csv_path, title):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(7, 4))
    plt.hist(df['grade'], bins=20, color='skyblue', edgecolor='black')
    plt.title(f"Grade Distribution - {title}")
    plt.xlabel("Grade")
    plt.ylabel("Frequency")
    plt.show()

def plot_completion_rate(csv_path, title):
    df = pd.read_csv(csv_path)
    rate = df['completed'].mean()
    plt.bar([title], [rate], color='purple')
    plt.ylim(0, 1)
    plt.ylabel("Completion Rate")
    plt.title(f"Completion Rate - {title}")
    plt.show()

def main():
    base = Path(__file__).parent
    # 1. Vẽ learning curve từ training_history.json
    print("Plotting training history...")
    plot_training(base / "results/training_history.json")

    # 2. Vẽ phân phối điểm số trên train/test
    print("Plotting grade distribution (train)...")
    plot_grade_distribution(base / "data/simulated/train_data.csv", "Train Set")
    print("Plotting grade distribution (test)...")
    plot_grade_distribution(base / "data/simulated/test_data.csv", "Test Set")

    # 3. Vẽ completion rate trên train/test
    print("Plotting completion rate (train)...")
    plot_completion_rate(base / "data/simulated/train_data.csv", "Train Set")
    print("Plotting completion rate (test)...")
    plot_completion_rate(base / "data/simulated/test_data.csv", "Test Set")

if __name__ == "__main__":
    main()
