# Changelog

## [2.0.0] - 2025-01-13 - Major Redesign

### 🔄 Breaking Changes
- **State Representation**: Changed from 22-dim abstract features → 12-dim Moodle behavioral features
- **Action Space**: Changed from abstract activity features → concrete Moodle resource IDs
- **Data Source**: Changed from simulated data → real Moodle logs

### ✨ Added
- `core/moodle_state_builder.py` - State extraction từ Moodle `features_scaled_report.json`
- `core/action_space.py` - Refactored to work with course structure JSON
- `examples/demo_moodle_integration.py` - New demo với Moodle data
- `README_NEW_DESIGN.md` - Comprehensive design documentation

### 🗑️ Removed/Deprecated
- `policy_step7.json` - Old trained model
- `q_table_step7.npy` - Old Q-table
- `qlearning_final_report_step7.txt` - Old training report
- `qlearning_metadata_step7.json` - Old metadata
- `state_action_mappings_step7.json` - Old mappings
- `adaptive_recommender_step7.py` - Old main script
- `Step7_Q_Learning_Training.ipynb` - Old training notebook
- `ARCHITECTURE.md` - Superseded by README_NEW_DESIGN.md
- `PROJECT_SUMMARY.md` - Superseded by README.md
- `TREE_STRUCTURE.md` - Outdated
- `USAGE_GUIDE.md` - Outdated

### 🔄 Renamed
- `examples/quick_demo.py` → `quick_demo_OLD.py` (old design)
- `core/state_builder.py` → `state_builder_OLD.py` (old design)

### 📝 Changed
- `README.md` - Updated to reflect new design
- `requirements.txt` - Simplified dependencies
- `core/action_space.py` - Complete rewrite for Moodle integration

### 🔧 To Be Refactored
- `core/qlearning_agent.py` - Needs update to work with new State/Action
- `core/reward_calculator.py` - May need adjustments
- `models/` - Consider simplifying or removing if not needed

---

## [1.0.0] - 2024-XX-XX - Initial Release

### Features
- Q-Learning agent with abstract state representation
- Course-agnostic design
- Episode-based training
- Top-K recommendations
