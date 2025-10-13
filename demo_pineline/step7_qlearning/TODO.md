# TODO - Q-Learning Adaptive Learning System

## 🔴 High Priority

### 1. Refactor QLearningAgent
- [ ] Update `qlearning_agent.py` để work với `MoodleStateBuilder`
- [ ] Update để work với `ActionSpace` (resource IDs)
- [ ] Test Q-table storage/loading với new state format
- [ ] Simplify API

### 2. Create Training Pipeline
- [ ] Load real student data từ `features_scaled_report.json`
- [ ] Load course structure từ MongoDB JSON
- [ ] Simulate learning trajectories
- [ ] Train Q-table
- [ ] Save trained model

### 3. Validation
- [ ] Test với multiple students
- [ ] Validate recommendations make sense
- [ ] Compare với baseline (random, popularity)

---

## 🟡 Medium Priority

### 4. Reward Function
- [ ] Review `reward_calculator.py`
- [ ] Adjust cho Moodle data format
- [ ] Consider multiple objectives (grade, time, engagement)

### 5. Documentation
- [ ] Add docstrings to all functions
- [ ] Create API documentation
- [ ] Add more examples
- [ ] Tutorial notebook

### 6. Models Cleanup
- [ ] Review `models/course_structure.py` - cần thiết không?
- [ ] Review `models/student_profile.py` - có thể đơn giản hóa?
- [ ] Consider removing nếu không dùng

---

## 🟢 Low Priority

### 7. Optimization
- [ ] Q-table sparsity analysis
- [ ] Consider function approximation (DQN)
- [ ] Batch training

### 8. Features
- [ ] Multi-objective optimization
- [ ] Context-aware recommendations
- [ ] Explanations for recommendations

### 9. Deployment
- [ ] REST API endpoint
- [ ] Integration với Moodle plugin
- [ ] Monitoring & logging
- [ ] A/B testing framework

---

## ✅ Completed

- [x] Design new State representation (12 dims từ Moodle)
- [x] Design new Action space (resource IDs)
- [x] Implement `MoodleStateBuilder`
- [x] Implement new `ActionSpace`
- [x] Create demo script `demo_moodle_integration.py`
- [x] Clean up old files
- [x] Update documentation (README, CHANGELOG)

---

## 🗑️ To Remove Later

- [ ] `core/state_builder_OLD.py` - sau khi confirm new version works
- [ ] `examples/quick_demo_OLD.py` - sau khi có replacement
- [ ] `examples/demo_model.pkl` - old trained model
- [ ] `examples/visualize_architecture.py` - outdated?
- [ ] `examples/architecture_diagram.png` - outdated?

---

## 📝 Notes

### Decisions Made:
1. **State**: 12 dims từ Moodle logs thay vì 22 dims abstract
2. **Action**: Concrete resource IDs thay vì abstract features
3. **Course-agnostic**: State không depend on specific course
4. **Moodle-first**: Design around Moodle data format

### Open Questions:
1. Có cần giữ `models/` folder không? Hay chỉ dùng dict?
2. Reward function best practices cho educational domain?
3. How to handle cold-start (new students)?
4. Online learning vs batch training?

### Resources Needed:
- [ ] More real student data for training
- [ ] Course structure từ multiple courses
- [ ] Historical outcome data (grades over time)
- [ ] Evaluation metrics & benchmarks
