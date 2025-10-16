import matplotlib.pyplot as plt


def main():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')

    # Các box pipeline (x, y, width, height)
    boxes = [
        ("Cluster Statistics\n(JSON)", (0.1, 0.8, 0.18, 0.09)),
        ("Course Structure\n(JSON)", (0.1, 0.6, 0.18, 0.09)),
        ("Real Features\n(JSON, optional)", (0.1, 0.4, 0.18, 0.09)),
        ("Student Profile\n(simulate_student_profile)", (0.36, 0.7, 0.22, 0.09)),
        ("Learning Trajectory\n(simulate_learning_trajectory)", (0.65, 0.7, 0.22, 0.09)),
        ("Dataset (All Students)\n(generate_dataset)", (0.36, 0.5, 0.22, 0.09)),
        ("Train/Test Split", (0.36, 0.3, 0.22, 0.09)),
        ("train_data.csv", (0.65, 0.2, 0.22, 0.09)),
        ("test_data.csv", (0.65, 0.1, 0.22, 0.09)),
        ("dataset_summary.json", (0.36, 0.1, 0.22, 0.09)),
    ]

    # Vẽ box
    for text, (x, y, w, h) in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, fc="lightblue", ec="b", lw=2, zorder=1))
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=10, zorder=2)

    # Hàm tính điểm mép box
    def edge(x, y, w, h, side):
        if side == 'right':
            return (x + w, y + h/2)
        if side == 'left':
            return (x, y + h/2)
        if side == 'top':
            return (x + w/2, y + h)
        if side == 'bottom':
            return (x + w/2, y)

    # Mũi tên (từ mép box này sang mép box kia)
    arrowprops = dict(arrowstyle="->", color='gray', lw=2)

    # Cluster/Course/Real -> Student Profile
    ax.annotate("", xy=edge(*boxes[3][1], 'left'), xytext=edge(*boxes[0][1], 'right'), arrowprops=arrowprops)
    ax.annotate("", xy=edge(*boxes[3][1], 'left'), xytext=edge(*boxes[1][1], 'right'), arrowprops=arrowprops)
    ax.annotate("", xy=edge(*boxes[3][1], 'left'), xytext=edge(*boxes[2][1], 'right'), arrowprops=arrowprops)
    # Student Profile -> Learning Trajectory
    ax.annotate("", xy=edge(*boxes[4][1], 'left'), xytext=edge(*boxes[3][1], 'right'), arrowprops=arrowprops)
    # Student Profile -> Dataset
    ax.annotate("", xy=edge(*boxes[5][1], 'top'), xytext=edge(*boxes[3][1], 'bottom'), arrowprops=arrowprops)
    # Learning Trajectory -> Dataset
    ax.annotate("", xy=edge(*boxes[5][1], 'right'), xytext=edge(*boxes[4][1], 'left'), arrowprops=arrowprops)
    # Dataset -> Train/Test Split
    ax.annotate("", xy=edge(*boxes[6][1], 'top'), xytext=edge(*boxes[5][1], 'bottom'), arrowprops=arrowprops)
    # Train/Test Split -> train_data.csv
    ax.annotate("", xy=edge(*boxes[7][1], 'top'), xytext=edge(*boxes[6][1], 'right'), arrowprops=arrowprops)
    # Train/Test Split -> test_data.csv
    ax.annotate("", xy=edge(*boxes[8][1], 'top'), xytext=edge(*boxes[6][1], 'right'), arrowprops=arrowprops)
    # Train/Test Split -> dataset_summary.json
    ax.annotate("", xy=edge(*boxes[9][1], 'left'), xytext=edge(*boxes[6][1], 'bottom'), arrowprops=arrowprops)

    plt.title("Data Simulation Pipeline (data_simulator.py)", fontsize=14)
    plt.tight_layout()
     # 📸 Lưu hình ra file PNG
    plt.savefig("data_simulation_pipeline.png", dpi=300, bbox_inches='tight')
    print("✅ Hình đã được lưu: data_simulation_pipeline.png")

    plt.show()


if __name__ == "__main__":
    main()