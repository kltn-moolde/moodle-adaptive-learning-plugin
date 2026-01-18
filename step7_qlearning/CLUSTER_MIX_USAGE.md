# Cluster Mix Feature - Usage Examples

## Overview
The training script now supports flexible cluster distribution using `--total-students` and `--cluster-mix` parameters.

## Basic Usage

### 1. Old Method (Fixed students per cluster)
```bash
# 5 students per cluster = 15 total students (5 weak, 5 medium, 5 strong)
python3 training/train_qlearning.py --episodes 50 --students 5 --steps 30
```

### 2. New Method (Total students with cluster mix)

#### Default Distribution (20% weak, 60% medium, 20% strong)
```bash
# 50 total students distributed by default ratio
python3 training/train_qlearning.py \
  --episodes 50 \
  --total-students 50 \
  --steps 30
```

#### Custom Distribution
```bash
# 100 students: 10% weak, 80% medium, 10% strong
python3 training/train_qlearning.py \
  --episodes 100 \
  --total-students 100 \
  --cluster-mix 0.1 0.8 0.1 \
  --steps 30
```

```bash
# 50 students: Equal distribution (33% each)
python3 training/train_qlearning.py \
  --episodes 50 \
  --total-students 50 \
  --cluster-mix 0.33 0.33 0.34 \
  --steps 30
```

## Detailed Examples

### Example 1: Training with Realistic Distribution (More medium students)
```bash
cd /Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning

PYTHONPATH=$PWD:$PYTHONPATH python3 training/train_qlearning.py \
  --course-id 670 \
  --episodes 50 \
  --total-students 30 \
  --cluster-mix 0.2 0.6 0.2 \
  --steps 30
```
**Expected distribution:** ~6 weak, ~18 medium, ~6 strong students

### Example 2: Training with More Weak Students (Focus on struggling learners)
```bash
PYTHONPATH=$PWD:$PYTHONPATH python3 training/train_qlearning.py \
  --course-id 670 \
  --episodes 50 \
  --total-students 30 \
  --cluster-mix 0.5 0.3 0.2 \
  --steps 30
```
**Expected distribution:** ~15 weak, ~9 medium, ~6 strong students

### Example 3: Quick Test Training
```bash
PYTHONPATH=$PWD:$PYTHONPATH python3 training/train_qlearning.py \
  --course-id 670 \
  --episodes 20 \
  --total-students 15 \
  --cluster-mix 0.2 0.6 0.2 \
  --steps 20
```
**Expected distribution:** ~3 weak, ~9 medium, ~3 strong students

### Example 4: Full Training with Detailed Logging
```bash
PYTHONPATH=$PWD:$PYTHONPATH python3 training/train_qlearning.py \
  --course-id 670 \
  --episodes 100 \
  --total-students 50 \
  --cluster-mix 0.2 0.6 0.2 \
  --steps 30 \
  --detailed-logging \
  --log-interval 10
```

## Parameter Explanation

### `--total-students` (NEW)
- Total number of students to generate
- Overrides the old `--students` parameter
- Students are automatically distributed according to `--cluster-mix`

### `--cluster-mix` (NEW)
- Three float values representing ratios for: WEAK MEDIUM STRONG
- Values will be normalized automatically (don't need to sum to 1.0)
- Default: `0.2 0.6 0.2` (20% weak, 60% medium, 20% strong)
- Only used when `--total-students` is specified

### `--students` (OLD - still supported)
- Number of students PER cluster
- Used when `--total-students` is NOT provided
- Creates equal distribution across all 3 clusters

## Migration Guide

### Old Command
```bash
python3 training/train_qlearning.py --episodes 100 --students 5 --steps 30
# Creates: 15 students (5 weak, 5 medium, 5 strong)
```

### New Equivalent
```bash
python3 training/train_qlearning.py --episodes 100 --total-students 15 --cluster-mix 0.33 0.33 0.34 --steps 30
# Creates: ~15 students (5 weak, 5 medium, 5 strong)
```

### More Realistic Distribution
```bash
python3 training/train_qlearning.py --episodes 100 --total-students 15 --cluster-mix 0.2 0.6 0.2 --steps 30
# Creates: ~15 students (3 weak, 9 medium, 3 strong) - more realistic!
```

## Testing Cluster Mix

Run the test script to verify distribution:
```bash
PYTHONPATH=$PWD:$PYTHONPATH python3 test_cluster_mix.py
```

## Notes

1. **Stochastic Distribution:** The actual number of students per cluster may vary slightly due to random sampling, but will converge to the specified ratios for larger sample sizes.

2. **Backward Compatibility:** The old `--students` parameter still works for equal distribution.

3. **Validation:** The ratios are automatically normalized, so `0.1 0.4 0.1` works the same as `0.167 0.666 0.167`.

4. **Best Practice:** Use `--total-students` with `--cluster-mix` for more flexible and realistic training scenarios.
