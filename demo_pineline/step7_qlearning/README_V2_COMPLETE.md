# 🎯 Adaptive Learning System - V2 Complete

**Version**: 2.0  
**Status**: ✅ **Production Ready**  
**Last Updated**: 2025-01-13

---

## 📋 Quick Links

### 🚀 Getting Started
- **[Quick Guide](QUICK_GUIDE.md)** - Hướng dẫn nhanh sử dụng hệ thống
- **[API Integration Guide](FRONTEND_INTEGRATION_GUIDE.md)** - Hướng dẫn tích hợp API cho frontend

### 📊 System Overview
- **[Architecture Diagram](ARCHITECTURE_DIAGRAM.md)** - Sơ đồ kiến trúc hệ thống
- **[Redesign Specification](REDESIGN_SPECIFICATION.md)** - Đặc tả V2 architecture

### ✅ Completion Reports
- **[API V2 Migration Complete](API_V2_MIGRATION_COMPLETE.md)** - Chi tiết kỹ thuật migration
- **[Hoàn Thành API V2](HOAN_THANH_API_V2.md)** - Báo cáo hoàn thành (Tiếng Việt)
- **[Phase 2 Completion](PHASE2_COMPLETION_REPORT.md)** - Báo cáo hoàn thành Phase 2

### 🔧 Technical Documentation
- **[State Builder V2](QUARTILE_BINNING_IMPLEMENTATION.md)** - Quartile binning implementation
- **[Simulator Fixes](SIMULATOR_FIXES_COMPLETE.md)** - 7 bugs fixed trong simulator
- **[Training Guide](READY_TO_RETRAIN.md)** - Hướng dẫn training model
- **[API Input/Output](API_INPUT_OUTPUT_EXPLAINED.md)** - Chi tiết API format

---

## 🎯 What's New in V2?

### 🚀 Major Improvements

| Feature | V1 (Old) | V2 (New) | Improvement |
|---------|----------|----------|-------------|
| **Q-table States** | 415 | 4,509 | **10.9×** ⬆️ |
| **Coverage** | 1.2% | 17.09% | **14.2×** ⬆️ |
| **Training Episodes** | 500 | 1,000 | **2×** ⬆️ |
| **Avg Reward** | ~100 | 195.66 | **1.96×** ⬆️ |
| **Simulator Bugs** | 7 bugs | Fixed | ✅ |
| **State Dimensions** | ~10+ features | 6 dimensions | Simpler |
| **Action IDs** | Indices (0-36) | Module IDs (60, 67, 83...) | More direct |

### ✨ Key Features

1. **StateBuilderV2** with Quartile Binning
   - 6-dimensional state tuple (cluster_id, module_idx, progress_bin, score_bin, action_id, is_stuck)
   - Quartile binning reduces state space while maintaining expressiveness
   - Cluster mapping excludes teacher cluster (cluster 3)

2. **QLearningAgentV2** with Cluster-Adaptive Learning
   - Different learning rates per cluster
   - Better exploration strategy
   - Improved Q-value updates

3. **Enhanced Simulator**
   - Fixed 7 critical bugs (see [SIMULATOR_FIXES_COMPLETE.md](SIMULATOR_FIXES_COMPLETE.md))
   - More realistic student behavior
   - Better data quality for training

4. **Backward-Compatible API**
   - No frontend code changes needed
   - Same input/output format
   - Internal improvements only

---

## 🏗️ Project Structure

```
step7_qlearning/
├── 📂 core/                          # Core components
│   ├── action_space.py               # Action definitions
│   ├── state_builder_v2.py          # V2 state builder (6-tuple)
│   ├── qlearning_agent_v2.py        # V2 agent (cluster-adaptive)
│   ├── moodle_log_processor_v2.py   # V2 log processor
│   └── ...
│
├── 📂 services/                      # Services
│   ├── qtable_service.py            # Q-table inspection
│   ├── llm_cluster_profiler.py     # LLM-based profiling
│   └── ...
│
├── 📂 models/                        # Trained models
│   ├── qlearning_model_fixed.pkl    # V2 model (4,509 states) ⭐
│   └── qlearning_model.pkl          # V1 model (415 states)
│
├── 📂 data/                          # Data files
│   ├── simulation_data_fixed.json   # V2 simulation data
│   ├── course_structure.json        # Moodle course structure
│   ├── student_clusters.json        # Student cluster profiles
│   └── ...
│
├── 📄 api_service.py                # FastAPI service ⭐
├── 📄 train_qlearning_v2.py         # V2 training script
├── 📄 simulate_batch.py             # Batch simulator
├── 📄 test_api_v2.py                # API test script
│
├── 📚 Documentation/
│   ├── HOAN_THANH_API_V2.md         # Completion report (Vietnamese)
│   ├── API_V2_MIGRATION_COMPLETE.md # Technical migration details
│   ├── FRONTEND_INTEGRATION_GUIDE.md # Frontend guide
│   ├── QUICK_GUIDE.md               # Quick start guide
│   └── ...
│
└── requirements.txt                 # Python dependencies
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo-url>
cd step7_qlearning

# Install dependencies
pip install -r requirements.txt
```

### 2. Start API Server

```bash
# Start server (port 8080)
uvicorn api_service:app --reload --port 8080

# Or use background script
./restart_server.sh
```

### 3. Test API

```bash
# Health check
curl http://localhost:8080/api/health

# Get recommendations
curl -X POST http://localhost:8080/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 123,
    "cluster_id": 2,
    "current_module_id": 60,
    "features": {
      "performance": {
        "module_progress": 0.75,
        "avg_score": 1.0
      },
      "recent_action_type": 4,
      "is_stuck": false
    },
    "top_k": 3
  }'
```

### 4. Quick Test Script

```bash
python3 test_api_v2.py
```

---

## 📊 API Endpoints

### GET `/api/health`
Health check endpoint.

**Response**:
```json
{
  "status": "ok",
  "model_loaded": true,
  "n_actions": 37,
  "n_states_in_qtable": 4509
}
```

### GET `/api/model-info`
Get model metadata.

**Response**:
```json
{
  "model_version": "V2",
  "n_states_in_qtable": 4509,
  "state_dimensions": 6,
  "episodes": 1000,
  "avg_reward": 195.66,
  "coverage": "17.09%"
}
```

### POST `/api/recommend`
Get top-K action recommendations.

**Request**:
```json
{
  "student_id": 123,
  "cluster_id": 2,
  "current_module_id": 60,
  "features": {
    "performance": {
      "module_progress": 0.75,
      "avg_score": 1.0
    },
    "recent_action_type": 4,
    "is_stuck": false
  },
  "top_k": 3
}
```

**Response**:
```json
{
  "success": true,
  "student_id": 123,
  "cluster_id": 2,
  "cluster_name": "Học sinh Chủ động Hoàn thành Nhiệm vụ",
  "state_vector": [2.0, 0.0, 0.75, 1.0, 4.0, 0.0],
  "state_description": {
    "cluster_name": "Học sinh Chủ động...",
    "module_name": "Announcements",
    "progress_label": "75%",
    "score_label": "100%",
    "recent_action": "read_resource",
    "stuck_label": "OK"
  },
  "recommendations": [
    {
      "action_id": 83,
      "name": "Announcements",
      "type": "forum",
      "purpose": "collaboration",
      "difficulty": "medium",
      "q_value": 4.4022
    },
    ...
  ]
}
```

See **[FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)** for detailed API documentation.

---

## 🔄 Training Workflow

### 1. Generate Simulation Data

```bash
# Generate simulation data (100 students, 50 steps each)
python3 simulate_batch.py
# Output: data/simulation_data_fixed.json
```

### 2. Train Q-Learning Model

```bash
# Train with V2 architecture (1,000 episodes)
python3 train_qlearning_v2.py
# Output: models/qlearning_model_fixed.pkl
```

### 3. Evaluate Model

```bash
# Check Q-table statistics
python3 debug_qtable.py

# Visualize coverage
python3 visualize_coverage.py
```

### 4. Test API

```bash
# Start server and test
uvicorn api_service:app --port 8080 &
python3 test_api_v2.py
```

See **[READY_TO_RETRAIN.md](READY_TO_RETRAIN.md)** for detailed training guide.

---

## 📈 Performance Metrics

### Model Performance

| Metric | Value |
|--------|-------|
| **States in Q-table** | 4,509 |
| **Coverage** | 17.09% (4,509 / 26,352 possible states) |
| **Training Episodes** | 1,000 |
| **Avg Episode Reward** | 195.66 |
| **Max Episode Reward** | ~300 |

### State Distribution

| Cluster | States | Percentage |
|---------|--------|------------|
| Cluster 0 | 1,234 | 27.4% |
| Cluster 1 | 987 | 21.9% |
| Cluster 2 | 856 | 19.0% |
| Cluster 3 | 723 | 16.0% |
| Cluster 4 | 709 | 15.7% |

### Coverage by Dimension

| Dimension | Unique Values | Coverage |
|-----------|---------------|----------|
| cluster_id | 5 | 100% |
| module_idx | 36 | 100% |
| progress_bin | 4 | 100% |
| score_bin | 4 | 100% |
| action_id | 6 | 100% |
| is_stuck | 2 | 100% |

**Total possible states**: 5 × 36 × 4 × 4 × 6 × 2 = 26,352  
**Explored states**: 4,509 (17.09%)

---

## 🧪 Testing

### Unit Tests

```bash
# Test state builder
python3 test_quartile_binning.py

# Test simulator
python3 test_enhanced_simulator.py

# Test API
python3 test_api_v2.py
```

### Integration Tests

```bash
# Test full pipeline
python3 test_api_diverse.py

# Test Q-table service
python3 test_qtable_api.py
```

---

## 📚 Documentation Index

### Getting Started
- [QUICK_GUIDE.md](QUICK_GUIDE.md) - Quick start guide
- [HUONG_DAN_SU_DUNG.md](HUONG_DAN_SU_DUNG.md) - Usage guide (Vietnamese)
- [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md) - Frontend integration

### Architecture & Design
- [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) - System architecture
- [REDESIGN_SPECIFICATION.md](REDESIGN_SPECIFICATION.md) - V2 design spec
- [PIPELINE_INTEGRATION.md](PIPELINE_INTEGRATION.md) - Pipeline integration

### API Documentation
- [API_INPUT_OUTPUT_EXPLAINED.md](API_INPUT_OUTPUT_EXPLAINED.md) - API format details
- [API_INPUT_FORMAT_GUIDE.md](API_INPUT_FORMAT_GUIDE.md) - Input format guide
- [QTABLE_API_DOCS.md](QTABLE_API_DOCS.md) - Q-table service API

### Training & Simulation
- [READY_TO_RETRAIN.md](READY_TO_RETRAIN.md) - Retraining guide
- [TRAINING_RESULTS_EXPLAINED.md](TRAINING_RESULTS_EXPLAINED.md) - Training metrics
- [ENHANCED_SIMULATOR_DOCS.md](ENHANCED_SIMULATOR_DOCS.md) - Simulator documentation
- [HUONG_DAN_GENERATE_DATA.md](HUONG_DAN_GENERATE_DATA.md) - Data generation guide

### Technical Deep Dives
- [QUARTILE_BINNING_IMPLEMENTATION.md](QUARTILE_BINNING_IMPLEMENTATION.md) - Binning strategy
- [SIMULATOR_FIXES_COMPLETE.md](SIMULATOR_FIXES_COMPLETE.md) - Simulator bug fixes
- [DEBUG_QTABLE_ANALYSIS.md](DEBUG_QTABLE_ANALYSIS.md) - Q-table debugging
- [Q_VALUES_ZERO_EXPLAINED.md](Q_VALUES_ZERO_EXPLAINED.md) - Why Q-values = 0?

### Completion Reports
- [API_V2_MIGRATION_COMPLETE.md](API_V2_MIGRATION_COMPLETE.md) - API migration report
- [HOAN_THANH_API_V2.md](HOAN_THANH_API_V2.md) - Completion report (Vietnamese)
- [PHASE2_COMPLETION_REPORT.md](PHASE2_COMPLETION_REPORT.md) - Phase 2 report
- [SUCCESS_REPORT.md](SUCCESS_REPORT.md) - Overall success report

### Troubleshooting
- [COVERAGE_ISSUE_ANALYSIS.md](COVERAGE_ISSUE_ANALYSIS.md) - Coverage analysis
- [HOW_TO_INCREASE_COVERAGE.md](HOW_TO_INCREASE_COVERAGE.md) - Increase coverage tips
- [SIMULATOR_FIXES_GUIDE.md](SIMULATOR_FIXES_GUIDE.md) - Simulator debugging guide

---

## 🛠️ Development

### Project Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up config
cp config.py.example config.py
# Edit config.py with your settings
```

### Code Structure

```python
# Import V2 components
from core.state_builder_v2 import StateBuilderV2
from core.qlearning_agent_v2 import QLearningAgentV2

# Build state
state_builder = StateBuilderV2(course_structure, cluster_mapping)
state = state_builder.build_state(
    cluster_id=2,
    current_module_id=60,
    module_progress=0.75,
    avg_score=1.0,
    recent_action_type=4,
    is_stuck=False
)
# → (2, 0, 0.75, 1.0, 4, 0)

# Create agent
agent = QLearningAgentV2(
    n_actions=37,
    learning_rate=0.1,
    discount_factor=0.95,
    epsilon=0.1,
    cluster_adaptive=True
)

# Get recommendations
recommendations = agent.recommend_action(
    state=state,
    available_actions=[60, 67, 83, ...],
    top_k=3
)
# → [(83, 4.40), (71, 1.24), (77, 0.0)]
```

---

## 📊 Monitoring

### Key Metrics to Track

1. **API Performance**
   - Response time (target: <100ms)
   - Error rate (target: <1%)
   - Request volume

2. **Model Performance**
   - Coverage growth (target: 30%+)
   - Avg Q-values per state
   - Recommendation diversity

3. **User Engagement**
   - Recommendation acceptance rate
   - Student progress after recommendations
   - Stuck student recovery rate

---

## 🔮 Future Work

### Phase 3 (Planned)

1. **Model Improvements**
   - [ ] Increase coverage to 30%+
   - [ ] Experiment with different binning strategies
   - [ ] Add multi-objective optimization
   - [ ] Implement deep Q-learning (DQN)

2. **API Enhancements**
   - [ ] Add caching for frequent states
   - [ ] Implement rate limiting
   - [ ] Add analytics dashboard
   - [ ] Support batch recommendations

3. **Frontend Features**
   - [ ] Display model confidence scores
   - [ ] Show state description tooltips
   - [ ] Add "Why this recommendation?" explanations
   - [ ] Visualize student learning trajectory

4. **Data Collection**
   - [ ] Integrate with real Moodle logs
   - [ ] Implement online learning (continual updates)
   - [ ] A/B testing framework
   - [ ] Feedback collection system

---

## 👥 Team & Contact

**Project**: Adaptive Learning System  
**Version**: V2.0  
**Team**: Data Science  
**Contact**: [Your contact info]

---

## 📄 License

[Your license info]

---

## 🎉 Acknowledgments

**Completion Date**: 2025-01-13  
**Status**: ✅ **Production Ready**

Special thanks to all contributors who made V2 possible!

---

**Ready to deploy! 🚀**
