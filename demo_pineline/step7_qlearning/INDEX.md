# 📚 Q-LEARNING SYSTEM V2 - DOCUMENTATION INDEX

**Version:** 2.0  
**Date:** November 4, 2025  
**Status:** ✅ Core Complete | ⏳ Simulation Pending

---

## 🎯 BẮT ĐẦU TỪ ĐÂU?

### 1. **Nếu bạn muốn hiểu tổng quan hệ thống:**
   👉 Đọc: [`SUMMARY_VIETNAMESE.md`](SUMMARY_VIETNAMESE.md)  
   - Tóm tắt ngắn gọn thiết kế (5 phút đọc)
   - State, Action, Reward design
   - Examples và so sánh với version cũ

### 2. **Nếu bạn muốn xem kiến trúc hệ thống:**
   👉 Đọc: [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md)  
   - Sơ đồ ASCII chi tiết
   - Data flow
   - Component relationships

### 3. **Nếu bạn muốn hiểu design decisions:**
   👉 Đọc: [`REDESIGN_SPECIFICATION.md`](REDESIGN_SPECIFICATION.md)  
   - Design document đầy đủ (10 sections)
   - Scientific justification
   - State/Reward/Action/Simulation design
   - References

### 4. **Nếu bạn muốn implement các components còn lại:**
   👉 Đọc: [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md)  
   - Step-by-step roadmap (5 phases)
   - Code templates
   - Testing checklist

### 5. **Nếu bạn muốn quick start:**
   👉 Đọc: [`README_V2.md`](README_V2.md)  
   - Overview
   - Quick start commands
   - File structure
   - Examples

---

## 📄 TÀI LIỆU CHI TIẾT

### Design Documents

#### 1. **REDESIGN_SPECIFICATION.md** (⭐ Core Design)
```
Sections:
  1. STATE DESIGN (6 dimensions)
     - Cluster ID mapping
     - Module selection
     - Quartile binning
     - Action types
     - Stuck detection
     - Scientific justification
  
  2. ACTION DESIGN
     - Keep existing structure
     - Course-based actions
  
  3. REWARD DESIGN
     - Cluster-specific strategies
     - 7 reward components
     - Philosophy per cluster
  
  4. SIMULATION DESIGN
     - Student behavior models
     - Trajectory generation
  
  5. VISUALIZATION REQUIREMENTS
     - Journey plots
     - Heatmaps
     - Comparison views
  
  6. API OUTPUT (keep existing)
  
  7. UTILITY APIs (keep existing)
  
  8. IMPLEMENTATION PRIORITY
  
  9. SUCCESS METRICS
  
  10. RISKS & MITIGATION
```

#### 2. **IMPLEMENTATION_GUIDE.md** (⭐ Developer Guide)
```
Contents:
  • Completed Components (detailed)
  • Next Steps (5 phases)
    - Phase 1: Data Processing
    - Phase 2: Simulation
    - Phase 3: Q-Learning Training
    - Phase 4: Visualization
    - Phase 5: API Integration
  • Code templates for each phase
  • Testing strategy
  • File structure
  • Success criteria
```

#### 3. **SUMMARY_VIETNAMESE.md** (⭐ Quick Reference)
```
Contents:
  • Thiết kế State (6 chiều) - chi tiết từng chiều
  • Thiết kế Reward (cluster-specific) - công thức & ví dụ
  • Thiết kế Action (giữ nguyên)
  • Thiết kế Simulation (flow & model)
  • Visualization (4 loại)
  • Files đã tạo & TODO
  • Cách chạy test
  • State space size
  • Justification
  • Next steps
  • Checklist
```

#### 4. **ARCHITECTURE_DIAGRAM.md** (⭐ Visual Reference)
```
Contents:
  • ASCII diagram of entire system
  • Data sources
  • Core components (7 modules)
  • Workflow (training & inference)
  • State space breakdown
  • Action space breakdown
  • Status summary
```

#### 5. **README_V2.md** (⭐ Overview)
```
Contents:
  • Overview & key improvements
  • Architecture
  • File structure
  • Completed components
  • Quick start
  • State design justification
  • Visualization examples
  • Next steps
  • Testing
  • Success metrics
```

---

## 💻 CODE FILES

### ✅ Completed & Tested

#### 1. **core/state_builder_v2.py**
```
Class: StateBuilderV2

Key Features:
  • 6-dimensional state representation
  • Cluster mapping (remove teacher)
  • Quartile binning
  • Action type mapping
  • Stuck detection
  • Module extraction

Key Methods:
  • build_state() - Build state from components
  • map_cluster_id() - Map original → new cluster ID
  • quartile_bin() - Bin continuous values
  • map_action_type() - Map Moodle events → actions
  • detect_stuck() - Detect stuck students
  • state_to_string() - Human-readable state

Test: python3 core/state_builder_v2.py
```

#### 2. **core/reward_calculator_v2.py**
```
Class: RewardCalculatorV2

Key Features:
  • Auto-classify clusters (weak/medium/strong)
  • 7 reward components
  • Cluster-specific strategies

Key Methods:
  • calculate_reward() - Full reward calculation
  • calculate_reward_simple() - Simplified version
  • get_cluster_level() - Get cluster type
  • get_reward_strategy_description() - Strategy info

Test: python3 core/reward_calculator_v2.py
```

#### 3. **visualize_trajectory.py**
```
Class: TrajectoryVisualizer

Key Features:
  • Student journey plot
  • Progress heatmap
  • State metrics over time
  • Multi-student comparison

Key Methods:
  • plot_student_journey() - Path through modules
  • plot_progress_heatmap() - Module x time heatmap
  • plot_state_metrics() - Progress/score/stuck over time
  • plot_comparison() - Compare multiple students

Test: python3 visualize_trajectory.py
Output: plots/test/*.png
```

#### 4. **core/action_space.py** (existing, keep)
```
Class: ActionSpace

Key Features:
  • Load actions from course_structure.json
  • Filter learning activities
  • Map purposes & difficulties

Key Methods:
  • get_action() - Get action by ID
  • get_actions_by_type() - Filter by type
  • get_actions_by_purpose() - Filter by purpose

Status: Working, no changes needed
```

### ⏳ TODO (Next Phases)

#### 5. **core/moodle_log_processor_v2.py** (Phase 1)
```
Goal: Process logs → trajectories

Key Tasks:
  • Parse log.csv & grade.csv
  • Track student progress per module
  • Build state sequences
  • Calculate rewards
  • Output: (state, action, reward, next_state) tuples

Template: See IMPLEMENTATION_GUIDE.md Phase 1.1
```

#### 6. **core/student_context.py** (Phase 1)
```
Goal: Track student context

Key Tasks:
  • Maintain current_module, progress, score
  • Track quiz_attempts, time_on_module
  • Calculate recent_scores
  • Update from log entries

Template: See IMPLEMENTATION_GUIDE.md Phase 1.2
```

#### 7. **core/simulator_v2.py** (Phase 2)
```
Goal: Simulate student learning

Key Tasks:
  • Model student behavior per cluster
  • Simulate action outcomes
  • Generate realistic trajectories
  • Use state_builder_v2 & reward_calculator_v2

Template: See IMPLEMENTATION_GUIDE.md Phase 2.1
```

#### 8. **core/qlearning_agent_v2.py** (Phase 3)
```
Goal: Q-learning agent

Key Tasks:
  • Initialize Q-table
  • Implement Q-learning update
  • ε-greedy policy
  • Save/load Q-table

Template: See IMPLEMENTATION_GUIDE.md Phase 3.1
```

#### 9. **train_qlearning_v2.py** (Phase 3)
```
Goal: Training script

Key Tasks:
  • Load simulated trajectories
  • Train Q-learning agent
  • Monitor convergence
  • Save trained Q-table
  • Generate training report

Template: See IMPLEMENTATION_GUIDE.md Phase 3.2
```

#### 10. **api_service.py** (Phase 5)
```
Goal: Update API endpoints

Key Tasks:
  • Update /recommend with state_v2
  • Add /visualize/trajectory
  • Add /debug/state-v2
  • Backward compatibility

Template: See IMPLEMENTATION_GUIDE.md Phase 5.1
```

---

## 🧪 TESTING

### Run Tests
```bash
# Test state builder
python3 core/state_builder_v2.py

# Test reward calculator
python3 core/reward_calculator_v2.py

# Test visualizer
python3 visualize_trajectory.py

# All tests (when available)
python3 -m pytest tests/
```

### Expected Outputs
```
State Builder:
  ✓ Loaded 36 modules
  ✓ Cluster mapping: {0: 0, 1: 1, 2: 2, 4: 3, 5: 4}
  ✓ State space: 34,560 states

Reward Calculator:
  ✓ Classified 5 clusters (1 weak, 2 medium, 2 strong)
  ✓ Rewards: weak=12.0, medium=7.0, strong=11.0

Visualizer:
  ✓ Generated 9 visualizations
  ✓ Saved to plots/test/
```

---

## 📊 METRICS & STATUS

### Completion Status
```
✅ Design Phase:        100% (5/5 documents)
✅ Core Components:     60%  (3/5 modules)
⏳ Simulation:          0%   (0/2 modules)
⏳ Training:            0%   (0/2 modules)
⏳ API Integration:     0%   (0/1 module)

Overall Progress: 40% Complete
```

### Component Status
```
Component                      Status    Test    Docs
─────────────────────────────────────────────────────
StateBuilderV2                 ✅        ✅      ✅
RewardCalculatorV2             ✅        ✅      ✅
ActionSpace                    ✅        ✅      ✅
TrajectoryVisualizer           ✅        ✅      ✅
MoodleLogProcessorV2           ⏳        ⏳      ✅
StudentContext                 ⏳        ⏳      ✅
StudentSimulatorV2             ⏳        ⏳      ✅
QLearningAgentV2               ⏳        ⏳      ✅
TrainingScript                 ⏳        ⏳      ✅
APIService                     ⏳        ⏳      ✅
```

---

## 🎯 ROADMAP

### Week 1-2: Design & Core ✅
- [x] Complete design specification
- [x] Implement StateBuilderV2
- [x] Implement RewardCalculatorV2
- [x] Implement TrajectoryVisualizer
- [x] Write comprehensive documentation

### Week 3: Data & Simulation ⏳
- [ ] Implement MoodleLogProcessorV2
- [ ] Implement StudentContext
- [ ] Implement StudentSimulatorV2
- [ ] Generate synthetic trajectories
- [ ] Validate simulation

### Week 4: Training & Viz Enhancement ⏳
- [ ] Implement QLearningAgentV2
- [ ] Train on simulated data
- [ ] Enhance visualizations
- [ ] Build interactive dashboard

### Week 5: Integration & Deployment ⏳
- [ ] Update API service
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Deploy & document

---

## 🔗 QUICK LINKS

### Documentation
- [📄 Design Specification](REDESIGN_SPECIFICATION.md)
- [🛠️ Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [🇻🇳 Vietnamese Summary](SUMMARY_VIETNAMESE.md)
- [🏗️ Architecture Diagram](ARCHITECTURE_DIAGRAM.md)
- [📖 README V2](README_V2.md)
- [📑 This Index](INDEX.md)

### Code
- [✅ StateBuilderV2](core/state_builder_v2.py)
- [✅ RewardCalculatorV2](core/reward_calculator_v2.py)
- [✅ TrajectoryVisualizer](visualize_trajectory.py)
- [✅ ActionSpace](core/action_space.py)

### Data
- [📊 Cluster Profiles](data/cluster_profiles.json)
- [📚 Course Structure](data/course_structure.json)
- [📝 Moodle Logs](data/log/log.csv)
- [🎓 Grades](data/log/grade.csv)

### Outputs
- [📊 Sample Visualizations](plots/test/)

---

## 💡 TIPS FOR DEVELOPERS

### Starting a new component:
1. Read IMPLEMENTATION_GUIDE.md for the phase
2. Use provided code template
3. Follow existing code style (see completed components)
4. Write tests alongside implementation
5. Update this INDEX.md when done

### Understanding the system:
1. Start with SUMMARY_VIETNAMESE.md (quick overview)
2. Check ARCHITECTURE_DIAGRAM.md (visual understanding)
3. Deep dive into REDESIGN_SPECIFICATION.md (design rationale)
4. Implement using IMPLEMENTATION_GUIDE.md (step-by-step)

### Debugging:
1. Run individual component tests
2. Check logs in `logs/`
3. Visualize data with existing tools
4. Refer to examples in test files

---

## 📞 CONTACT & SUPPORT

- **Documentation Issues:** Check INDEX.md → relevant doc
- **Code Issues:** Run component tests, check error messages
- **Design Questions:** Refer to REDESIGN_SPECIFICATION.md
- **Implementation Questions:** Follow IMPLEMENTATION_GUIDE.md

---

## 📝 CHANGELOG

### 2024-11-04: Version 2.0 Initial Release
- ✅ Complete redesign of state (6 dimensions)
- ✅ Cluster-specific rewards
- ✅ Comprehensive documentation (5 MD files)
- ✅ Core components implemented & tested
- ✅ Sample visualizations generated
- ⏳ Simulation & training pending

---

**Last Updated:** November 4, 2025  
**Next Review:** Week 3 (after simulation phase)  
**Maintained By:** Q-Learning V2 Development Team
