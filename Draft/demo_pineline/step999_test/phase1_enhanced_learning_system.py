# -*- coding: utf-8 -*-
"""
PHASE 1: Hệ thống AI Gợi ý Học tập Thông minh - Phiên bản Nâng cao
================================================================

Dựa trên phân tích dữ liệu thực tế từ Moodle và mô hình Q-Learning hiện có,
thiết kế lại hệ thống với state space chi tiết hơn và cá nhân hóa sâu hơn.

Tác giả: AI Assistant
Ngày: 2024
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score
import json
import warnings
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# 1. ĐỊNH NGHĨA CÁC LỚP VÀ ENUM
# =============================================================================

class LearningState(Enum):
    """Các trạng thái học tập chi tiết dựa trên Moodle events"""
    # Trạng thái cơ bản
    VIEW_COURSE = "view_course"
    VIEW_MODULE = "view_module"
    VIEW_RESOURCE = "view_resource"
    
    # Trạng thái Assignment
    VIEW_ASSIGNMENT = "view_assignment"
    START_ASSIGNMENT = "start_assignment"
    SUBMIT_ASSIGNMENT = "submit_assignment"
    VIEW_FEEDBACK = "view_feedback"
    
    # Trạng thái Quiz
    VIEW_QUIZ = "view_quiz"
    START_QUIZ = "start_quiz"
    SUBMIT_QUIZ = "submit_quiz"
    REVIEW_QUIZ = "review_quiz"
    
    # Trạng thái tương tác
    VIEW_GRADES = "view_grades"
    VIEW_PROGRESS = "view_progress"
    PARTICIPATE_DISCUSSION = "participate_discussion"
    DOWNLOAD_MATERIALS = "download_materials"
    
    # Trạng thái đặc biệt
    SEEK_HELP = "seek_help"
    REVIEW_MISTAKES = "review_mistakes"
    PLAN_STUDY = "plan_study"

class LearningStyle(Enum):
    """Phong cách học tập"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

class PerformanceLevel(Enum):
    """Mức độ hiệu suất"""
    EXCELLENT = "excellent"      # >= 0.8
    GOOD = "good"               # 0.6 - 0.8
    AVERAGE = "average"         # 0.4 - 0.6
    BELOW_AVERAGE = "below_avg" # 0.2 - 0.4
    POOR = "poor"               # < 0.2

@dataclass
class StudentProfile:
    """Hồ sơ cá nhân của sinh viên"""
    user_id: int
    cluster_id: int
    learning_style: LearningStyle
    performance_level: PerformanceLevel
    engagement_score: float
    completion_rate: float
    time_preference: str  # "morning", "afternoon", "evening"
    weak_areas: List[str]
    strong_areas: List[str]
    learning_goals: List[str]
    current_state: LearningState
    learning_history: List[LearningState]
    performance_trend: str  # "improving", "stable", "declining"

@dataclass
class LearningRecommendation:
    """Gợi ý học tập cá nhân"""
    student_id: int
    recommended_state: LearningState
    confidence_score: float
    reasoning: str
    expected_benefit: float
    time_estimate: int  # phút
    difficulty_level: str
    prerequisites: List[LearningState]

# =============================================================================
# 2. LỚP Q-LEARNING NÂNG CAO
# =============================================================================

class EnhancedQLearningAgent:
    """Q-Learning Agent nâng cao với khả năng cá nhân hóa"""
    
    def __init__(self, n_states: int, n_actions: int, 
                 learning_rate: float = 0.1, 
                 discount: float = 0.95, 
                 epsilon: float = 0.1,
                 student_profile: Optional[StudentProfile] = None):
        self.n_states = n_states
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.student_profile = student_profile
        
        # Q-table chính
        self.q_table = np.zeros((n_states, n_actions))
        
        # Q-tables phụ cho các tình huống đặc biệt
        self.help_q_table = np.zeros((n_states, n_actions))  # Khi cần hỗ trợ
        self.excellent_q_table = np.zeros((n_states, n_actions))  # Khi học tốt
        self.struggling_q_table = np.zeros((n_states, n_actions))  # Khi gặp khó khăn
        
        # Lịch sử học tập
        self.learning_history = []
        self.performance_history = []
        
    def choose_action(self, state: int, context: str = "normal") -> int:
        """Chọn action dựa trên context và profile cá nhân"""
        if context == "help_needed":
            q_table = self.help_q_table
        elif context == "excellent_performance":
            q_table = self.excellent_q_table
        elif context == "struggling":
            q_table = self.struggling_q_table
        else:
            q_table = self.q_table
            
        # Epsilon-greedy với điều chỉnh dựa trên profile
        if np.random.random() < self._get_adaptive_epsilon():
            return np.random.randint(self.n_actions)
        else:
            return np.argmax(q_table[state])
    
    def _get_adaptive_epsilon(self) -> float:
        """Điều chỉnh epsilon dựa trên profile sinh viên"""
        base_epsilon = self.epsilon
        
        if self.student_profile:
            # Sinh viên có performance cao -> ít exploration
            if self.student_profile.performance_level in [PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD]:
                return base_epsilon * 0.5
            # Sinh viên gặp khó khăn -> nhiều exploration
            elif self.student_profile.performance_level in [PerformanceLevel.POOR, PerformanceLevel.BELOW_AVERAGE]:
                return base_epsilon * 1.5
                
        return base_epsilon
    
    def learn(self, state: int, action: int, reward: float, 
              next_state: int, context: str = "normal"):
        """Học từ experience với context awareness"""
        # Cập nhật Q-table chính
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state, action] = new_q
        
        # Cập nhật Q-table phù hợp với context
        if context == "help_needed":
            self._update_context_table(self.help_q_table, state, action, reward, next_state)
        elif context == "excellent_performance":
            self._update_context_table(self.excellent_q_table, state, action, reward, next_state)
        elif context == "struggling":
            self._update_context_table(self.struggling_q_table, state, action, reward, next_state)
        
        # Lưu lịch sử
        self.learning_history.append({
            'state': state, 'action': action, 'reward': reward, 
            'next_state': next_state, 'context': context
        })
    
    def _update_context_table(self, q_table: np.ndarray, state: int, 
                            action: int, reward: float, next_state: int):
        """Cập nhật Q-table cho context cụ thể"""
        current_q = q_table[state, action]
        max_next_q = np.max(q_table[next_state])
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        q_table[state, action] = new_q
    
    def get_policy(self, context: str = "normal") -> np.ndarray:
        """Lấy policy tối ưu cho context cụ thể"""
        if context == "help_needed":
            return np.argmax(self.help_q_table, axis=1)
        elif context == "excellent_performance":
            return np.argmax(self.excellent_q_table, axis=1)
        elif context == "struggling":
            return np.argmax(self.struggling_q_table, axis=1)
        else:
            return np.argmax(self.q_table, axis=1)

# =============================================================================
# 3. HỆ THỐNG REWARD NÂNG CAO
# =============================================================================

class EnhancedRewardSystem:
    """Hệ thống reward nâng cao với nhiều yếu tố"""
    
    def __init__(self):
        # Base rewards cho từng state
        self.base_rewards = {
            LearningState.VIEW_COURSE: 0.1,
            LearningState.VIEW_MODULE: 0.2,
            LearningState.VIEW_RESOURCE: 0.3,
            LearningState.VIEW_ASSIGNMENT: 0.4,
            LearningState.START_ASSIGNMENT: 0.6,
            LearningState.SUBMIT_ASSIGNMENT: 0.9,
            LearningState.VIEW_FEEDBACK: 0.5,
            LearningState.VIEW_QUIZ: 0.4,
            LearningState.START_QUIZ: 0.7,
            LearningState.SUBMIT_QUIZ: 1.0,
            LearningState.REVIEW_QUIZ: 0.6,
            LearningState.VIEW_GRADES: 0.3,
            LearningState.VIEW_PROGRESS: 0.4,
            LearningState.PARTICIPATE_DISCUSSION: 0.5,
            LearningState.DOWNLOAD_MATERIALS: 0.3,
            LearningState.SEEK_HELP: 0.8,
            LearningState.REVIEW_MISTAKES: 0.7,
            LearningState.PLAN_STUDY: 0.6
        }
        
        # Multipliers cho các yếu tố khác nhau
        self.performance_multipliers = {
            PerformanceLevel.EXCELLENT: 1.2,
            PerformanceLevel.GOOD: 1.1,
            PerformanceLevel.AVERAGE: 1.0,
            PerformanceLevel.BELOW_AVERAGE: 0.8,
            PerformanceLevel.POOR: 0.6
        }
        
        self.learning_style_multipliers = {
            LearningStyle.VISUAL: 1.1,
            LearningStyle.AUDITORY: 1.0,
            LearningStyle.KINESTHETIC: 1.05,
            LearningStyle.READING_WRITING: 1.08
        }
    
    def calculate_reward(self, current_state: LearningState, 
                        next_state: LearningState,
                        student_profile: StudentProfile,
                        context: str = "normal") -> float:
        """Tính reward dựa trên nhiều yếu tố"""
        
        # Base reward
        base_reward = self.base_rewards.get(next_state, 0.0)
        
        # Performance multiplier
        perf_multiplier = self.performance_multipliers.get(
            student_profile.performance_level, 1.0
        )
        
        # Learning style multiplier
        style_multiplier = self.learning_style_multipliers.get(
            student_profile.learning_style, 1.0
        )
        
        # Engagement bonus
        engagement_bonus = student_profile.engagement_score * 0.3
        
        # Completion rate bonus
        completion_bonus = student_profile.completion_rate * 0.2
        
        # Context-specific adjustments
        context_bonus = self._get_context_bonus(context, next_state)
        
        # Progress bonus (không lặp lại state)
        progress_bonus = 0.0
        if current_state != next_state:
            progress_bonus = 0.1
        
        # Difficulty penalty (nếu chuyển từ easy sang hard quá nhanh)
        difficulty_penalty = self._get_difficulty_penalty(current_state, next_state)
        
        # Tính tổng reward
        total_reward = (base_reward * perf_multiplier * style_multiplier + 
                       engagement_bonus + completion_bonus + 
                       context_bonus + progress_bonus - difficulty_penalty)
        
        return max(0.0, total_reward)  # Đảm bảo reward không âm
    
    def _get_context_bonus(self, context: str, state: LearningState) -> float:
        """Bonus dựa trên context"""
        if context == "help_needed" and state in [LearningState.SEEK_HELP, LearningState.REVIEW_MISTAKES]:
            return 0.3
        elif context == "excellent_performance" and state in [LearningState.SUBMIT_QUIZ, LearningState.SUBMIT_ASSIGNMENT]:
            return 0.2
        elif context == "struggling" and state in [LearningState.VIEW_RESOURCE, LearningState.VIEW_FEEDBACK]:
            return 0.4
        return 0.0
    
    def _get_difficulty_penalty(self, current_state: LearningState, 
                               next_state: LearningState) -> float:
        """Penalty nếu chuyển đổi khó khăn quá nhanh"""
        # Định nghĩa độ khó của các states
        difficulty_levels = {
            LearningState.VIEW_COURSE: 1,
            LearningState.VIEW_MODULE: 2,
            LearningState.VIEW_RESOURCE: 2,
            LearningState.VIEW_ASSIGNMENT: 3,
            LearningState.START_ASSIGNMENT: 4,
            LearningState.SUBMIT_ASSIGNMENT: 5,
            LearningState.VIEW_QUIZ: 3,
            LearningState.START_QUIZ: 4,
            LearningState.SUBMIT_QUIZ: 5,
            LearningState.REVIEW_QUIZ: 3,
            LearningState.SEEK_HELP: 2,
            LearningState.REVIEW_MISTAKES: 3,
            LearningState.PLAN_STUDY: 2
        }
        
        current_diff = difficulty_levels.get(current_state, 1)
        next_diff = difficulty_levels.get(next_state, 1)
        
        # Penalty nếu nhảy quá xa về độ khó
        if next_diff - current_diff > 2:
            return 0.2
        
        return 0.0

# =============================================================================
# 4. HỆ THỐNG GỢI Ý THÔNG MINH
# =============================================================================

class IntelligentRecommendationSystem:
    """Hệ thống gợi ý thông minh với khả năng cá nhân hóa sâu"""
    
    def __init__(self, q_agents: Dict[int, EnhancedQLearningAgent],
                 reward_system: EnhancedRewardSystem):
        self.q_agents = q_agents
        self.reward_system = reward_system
        self.states = list(LearningState)
        self.state_to_idx = {state: idx for idx, state in enumerate(self.states)}
        
    def get_personalized_recommendation(self, student_profile: StudentProfile) -> LearningRecommendation:
        """Tạo gợi ý cá nhân hóa cho sinh viên"""
        
        # Lấy agent cho cluster của sinh viên
        agent = self.q_agents.get(student_profile.cluster_id)
        if not agent:
            raise ValueError(f"No agent found for cluster {student_profile.cluster_id}")
        
        # Xác định context dựa trên profile
        context = self._determine_context(student_profile)
        
        # Lấy policy tối ưu cho context
        policy = agent.get_policy(context)
        
        # Lấy state hiện tại
        current_state_idx = self.state_to_idx[student_profile.current_state]
        
        # Lấy action được đề xuất
        recommended_action_idx = policy[current_state_idx]
        recommended_state = self.states[recommended_action_idx]
        
        # Tính confidence score
        confidence_score = self._calculate_confidence_score(
            agent, current_state_idx, recommended_action_idx, context
        )
        
        # Tạo reasoning
        reasoning = self._generate_reasoning(student_profile, recommended_state, context)
        
        # Ước tính lợi ích
        expected_benefit = self._estimate_benefit(student_profile, recommended_state)
        
        # Ước tính thời gian
        time_estimate = self._estimate_time(recommended_state, student_profile)
        
        # Xác định độ khó
        difficulty_level = self._get_difficulty_level(recommended_state)
        
        # Xác định prerequisites
        prerequisites = self._get_prerequisites(recommended_state)
        
        return LearningRecommendation(
            student_id=student_profile.user_id,
            recommended_state=recommended_state,
            confidence_score=confidence_score,
            reasoning=reasoning,
            expected_benefit=expected_benefit,
            time_estimate=time_estimate,
            difficulty_level=difficulty_level,
            prerequisites=prerequisites
        )
    
    def _determine_context(self, student_profile: StudentProfile) -> str:
        """Xác định context dựa trên profile sinh viên"""
        if student_profile.performance_level in [PerformanceLevel.POOR, PerformanceLevel.BELOW_AVERAGE]:
            return "struggling"
        elif student_profile.performance_level in [PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD]:
            return "excellent_performance"
        elif student_profile.engagement_score < 0.3:
            return "help_needed"
        else:
            return "normal"
    
    def _calculate_confidence_score(self, agent: EnhancedQLearningAgent, 
                                  current_state_idx: int, 
                                  recommended_action_idx: int,
                                  context: str) -> float:
        """Tính confidence score cho recommendation"""
        if context == "help_needed":
            q_table = agent.help_q_table
        elif context == "excellent_performance":
            q_table = agent.excellent_q_table
        elif context == "struggling":
            q_table = agent.struggling_q_table
        else:
            q_table = agent.q_table
        
        # Lấy Q-value của action được đề xuất
        recommended_q = q_table[current_state_idx, recommended_action_idx]
        
        # Lấy Q-value cao nhất
        max_q = np.max(q_table[current_state_idx])
        
        # Confidence = tỷ lệ Q-value của action được đề xuất so với max
        confidence = recommended_q / max_q if max_q > 0 else 0.0
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, student_profile: StudentProfile, 
                          recommended_state: LearningState,
                          context: str) -> str:
        """Tạo lý do cho recommendation"""
        reasoning_parts = []
        
        # Dựa trên performance level
        if student_profile.performance_level == PerformanceLevel.POOR:
            reasoning_parts.append("Dựa trên hiệu suất hiện tại, bạn nên tập trung vào các hoạt động cơ bản")
        elif student_profile.performance_level == PerformanceLevel.EXCELLENT:
            reasoning_parts.append("Với hiệu suất xuất sắc, bạn có thể thử thách bản thân với các hoạt động nâng cao")
        
        # Dựa trên learning style
        if student_profile.learning_style == LearningStyle.VISUAL:
            reasoning_parts.append("Phong cách học tập trực quan của bạn phù hợp với hoạt động này")
        
        # Dựa trên engagement
        if student_profile.engagement_score < 0.3:
            reasoning_parts.append("Hoạt động này sẽ giúp tăng cường sự tham gia của bạn")
        
        # Dựa trên context
        if context == "struggling":
            reasoning_parts.append("Đây là bước tiếp theo phù hợp để cải thiện tình hình học tập")
        elif context == "excellent_performance":
            reasoning_parts.append("Hoạt động này sẽ giúp bạn duy trì và phát triển thêm kỹ năng")
        
        return ". ".join(reasoning_parts) + "."
    
    def _estimate_benefit(self, student_profile: StudentProfile, 
                         recommended_state: LearningState) -> float:
        """Ước tính lợi ích của recommendation"""
        # Base benefit từ reward system
        base_benefit = self.reward_system.base_rewards.get(recommended_state, 0.0)
        
        # Điều chỉnh dựa trên profile
        if recommended_state in student_profile.strong_areas:
            base_benefit *= 1.2
        elif recommended_state in student_profile.weak_areas:
            base_benefit *= 0.8
        
        return base_benefit
    
    def _estimate_time(self, recommended_state: LearningState, 
                      student_profile: StudentProfile) -> int:
        """Ước tính thời gian cần thiết (phút)"""
        time_estimates = {
            LearningState.VIEW_COURSE: 5,
            LearningState.VIEW_MODULE: 10,
            LearningState.VIEW_RESOURCE: 15,
            LearningState.VIEW_ASSIGNMENT: 10,
            LearningState.START_ASSIGNMENT: 30,
            LearningState.SUBMIT_ASSIGNMENT: 45,
            LearningState.VIEW_FEEDBACK: 10,
            LearningState.VIEW_QUIZ: 5,
            LearningState.START_QUIZ: 20,
            LearningState.SUBMIT_QUIZ: 30,
            LearningState.REVIEW_QUIZ: 15,
            LearningState.VIEW_GRADES: 5,
            LearningState.VIEW_PROGRESS: 10,
            LearningState.PARTICIPATE_DISCUSSION: 20,
            LearningState.DOWNLOAD_MATERIALS: 5,
            LearningState.SEEK_HELP: 15,
            LearningState.REVIEW_MISTAKES: 25,
            LearningState.PLAN_STUDY: 20
        }
        
        base_time = time_estimates.get(recommended_state, 15)
        
        # Điều chỉnh dựa trên performance level
        if student_profile.performance_level == PerformanceLevel.POOR:
            base_time *= 1.5  # Cần nhiều thời gian hơn
        elif student_profile.performance_level == PerformanceLevel.EXCELLENT:
            base_time *= 0.8  # Hoàn thành nhanh hơn
        
        return int(base_time)
    
    def _get_difficulty_level(self, state: LearningState) -> str:
        """Xác định độ khó của state"""
        difficulty_map = {
            LearningState.VIEW_COURSE: "Dễ",
            LearningState.VIEW_MODULE: "Dễ",
            LearningState.VIEW_RESOURCE: "Dễ",
            LearningState.VIEW_ASSIGNMENT: "Trung bình",
            LearningState.START_ASSIGNMENT: "Khó",
            LearningState.SUBMIT_ASSIGNMENT: "Khó",
            LearningState.VIEW_FEEDBACK: "Dễ",
            LearningState.VIEW_QUIZ: "Trung bình",
            LearningState.START_QUIZ: "Khó",
            LearningState.SUBMIT_QUIZ: "Khó",
            LearningState.REVIEW_QUIZ: "Trung bình",
            LearningState.VIEW_GRADES: "Dễ",
            LearningState.VIEW_PROGRESS: "Dễ",
            LearningState.PARTICIPATE_DISCUSSION: "Trung bình",
            LearningState.DOWNLOAD_MATERIALS: "Dễ",
            LearningState.SEEK_HELP: "Dễ",
            LearningState.REVIEW_MISTAKES: "Trung bình",
            LearningState.PLAN_STUDY: "Trung bình"
        }
        
        return difficulty_map.get(state, "Trung bình")
    
    def _get_prerequisites(self, state: LearningState) -> List[LearningState]:
        """Xác định prerequisites cho state"""
        prerequisites_map = {
            LearningState.VIEW_ASSIGNMENT: [LearningState.VIEW_COURSE, LearningState.VIEW_MODULE],
            LearningState.START_ASSIGNMENT: [LearningState.VIEW_ASSIGNMENT],
            LearningState.SUBMIT_ASSIGNMENT: [LearningState.START_ASSIGNMENT],
            LearningState.VIEW_QUIZ: [LearningState.VIEW_COURSE, LearningState.VIEW_MODULE],
            LearningState.START_QUIZ: [LearningState.VIEW_QUIZ],
            LearningState.SUBMIT_QUIZ: [LearningState.START_QUIZ],
            LearningState.REVIEW_QUIZ: [LearningState.SUBMIT_QUIZ],
            LearningState.VIEW_FEEDBACK: [LearningState.SUBMIT_ASSIGNMENT],
            LearningState.REVIEW_MISTAKES: [LearningState.VIEW_FEEDBACK, LearningState.REVIEW_QUIZ],
            LearningState.SEEK_HELP: [LearningState.VIEW_COURSE]
        }
        
        return prerequisites_map.get(state, [])

# =============================================================================
# 5. HỆ THỐNG PHÂN TÍCH VÀ XỬ LÝ DỮ LIỆU
# =============================================================================

class DataProcessor:
    """Xử lý và phân tích dữ liệu học tập"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.feature_columns = []
        self.load_data()
    
    def load_data(self):
        """Tải dữ liệu từ file JSON"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.df = pd.DataFrame(data)
        logger.info(f"Loaded {len(self.df)} students with {len(self.df.columns)} features")
    
    def create_enhanced_features(self):
        """Tạo các features nâng cao từ dữ liệu gốc"""
        # Features cơ bản
        self.df['engagement_score'] = (
            self.df['viewed'] + self.df['submitted'] + self.df['created']
        ) / 3
        
        self.df['assignment_completion'] = self.df['\\mod_assign\\event\\assessable_submitted']
        self.df['quiz_participation'] = (
            self.df['\\mod_quiz\\event\\attempt_started'] + 
            self.df['\\mod_quiz\\event\\attempt_submitted']
        ) / 2
        
        # Features nâng cao
        self.df['resource_utilization'] = (
            self.df['\\mod_resource\\event\\course_module_viewed'] +
            self.df['\\mod_folder\\event\\course_module_viewed'] +
            self.df['\\mod_page\\event\\course_module_viewed']
        ) / 3
        
        self.df['feedback_engagement'] = (
            self.df['\\mod_assign\\event\\feedback_viewed'] +
            self.df['\\mod_quiz\\event\\attempt_reviewed']
        ) / 2
        
        self.df['progress_tracking'] = (
            self.df['\\gradereport_user\\event\\grade_report_viewed'] +
            self.df['\\core\\event\\course_module_completion_updated']
        ) / 2
        
        self.df['interaction_level'] = (
            self.df['\\mod_forum\\event\\course_module_viewed'] +
            self.df['\\assignsubmission_comments\\event\\comment_created']
        ) / 2
        
        # Xác định learning style dựa trên hành vi
        self.df['learning_style'] = self._infer_learning_style()
        
        # Xác định performance level
        self.df['performance_level'] = self._infer_performance_level()
        
        # Xác định weak và strong areas
        self.df['weak_areas'] = self._identify_weak_areas()
        self.df['strong_areas'] = self._identify_strong_areas()
        
        logger.info("Enhanced features created successfully")
    
    def _infer_learning_style(self) -> pd.Series:
        """Suy luận learning style từ hành vi"""
        styles = []
        
        for _, row in self.df.iterrows():
            # Visual: xem nhiều resource, ít tương tác
            visual_score = row['resource_utilization'] - row['interaction_level']
            
            # Auditory: tham gia discussion, xem feedback
            auditory_score = row['interaction_level'] + row['feedback_engagement']
            
            # Kinesthetic: làm assignment, quiz nhiều
            kinesthetic_score = row['assignment_completion'] + row['quiz_participation']
            
            # Reading/Writing: xem tài liệu, tạo content
            rw_score = row['viewed'] + row['created']
            
            scores = {
                'visual': visual_score,
                'auditory': auditory_score,
                'kinesthetic': kinesthetic_score,
                'reading_writing': rw_score
            }
            
            styles.append(max(scores, key=scores.get))
        
        return pd.Series(styles)
    
    def _infer_performance_level(self) -> pd.Series:
        """Suy luận performance level từ điểm số"""
        levels = []
        
        for grade in self.df['mean_module_grade']:
            if grade >= 0.8:
                levels.append('excellent')
            elif grade >= 0.6:
                levels.append('good')
            elif grade >= 0.4:
                levels.append('average')
            elif grade >= 0.2:
                levels.append('below_avg')
            else:
                levels.append('poor')
        
        return pd.Series(levels)
    
    def _identify_weak_areas(self) -> pd.Series:
        """Xác định các lĩnh vực yếu"""
        weak_areas = []
        
        for _, row in self.df.iterrows():
            areas = []
            
            if row['assignment_completion'] < 0.3:
                areas.append('assignment')
            if row['quiz_participation'] < 0.3:
                areas.append('quiz')
            if row['resource_utilization'] < 0.3:
                areas.append('resource')
            if row['interaction_level'] < 0.3:
                areas.append('interaction')
            
            weak_areas.append(areas)
        
        return pd.Series(weak_areas)
    
    def _identify_strong_areas(self) -> pd.Series:
        """Xác định các lĩnh vực mạnh"""
        strong_areas = []
        
        for _, row in self.df.iterrows():
            areas = []
            
            if row['assignment_completion'] > 0.7:
                areas.append('assignment')
            if row['quiz_participation'] > 0.7:
                areas.append('quiz')
            if row['resource_utilization'] > 0.7:
                areas.append('resource')
            if row['interaction_level'] > 0.7:
                areas.append('interaction')
            
            strong_areas.append(areas)
        
        return pd.Series(strong_areas)
    
    def create_student_profiles(self) -> List[StudentProfile]:
        """Tạo student profiles từ dữ liệu đã xử lý"""
        profiles = []
        
        for _, row in self.df.iterrows():
            profile = StudentProfile(
                user_id=row['userid'],
                cluster_id=row.get('cluster', 0),
                learning_style=LearningStyle(row['learning_style']),
                performance_level=PerformanceLevel(row['performance_level']),
                engagement_score=row['engagement_score'],
                completion_rate=row['assignment_completion'],
                time_preference="evening",  # Mặc định, có thể cải thiện
                weak_areas=row['weak_areas'],
                strong_areas=row['strong_areas'],
                learning_goals=["improve_performance"],  # Mặc định
                current_state=LearningState.VIEW_COURSE,  # Mặc định
                learning_history=[],
                performance_trend="stable"  # Mặc định
            )
            profiles.append(profile)
        
        return profiles

# =============================================================================
# 6. HÀM CHÍNH VÀ DEMO
# =============================================================================

def main():
    """Hàm chính để demo hệ thống Phase 1"""
    logger.info("=== PHASE 1: HỆ THỐNG AI GỢI Ý HỌC TẬP THÔNG MINH ===")
    
    # 1. Xử lý dữ liệu
    logger.info("1. Xử lý dữ liệu...")
    processor = DataProcessor("../data/features_scaled_report.json")
    processor.create_enhanced_features()
    
    # 2. Tạo student profiles
    logger.info("2. Tạo student profiles...")
    student_profiles = processor.create_student_profiles()
    
    # 3. Khởi tạo hệ thống
    logger.info("3. Khởi tạo hệ thống...")
    reward_system = EnhancedRewardSystem()
    
    # Tạo Q-agents cho các clusters (giả sử có 3 clusters)
    q_agents = {}
    n_states = len(LearningState)
    n_actions = len(LearningState)
    
    for cluster_id in range(3):
        agent = EnhancedQLearningAgent(
            n_states=n_states,
            n_actions=n_actions,
            learning_rate=0.1,
            discount=0.95,
            epsilon=0.1
        )
        q_agents[cluster_id] = agent
    
    # 4. Khởi tạo hệ thống gợi ý
    recommendation_system = IntelligentRecommendationSystem(q_agents, reward_system)
    
    # 5. Demo gợi ý cho một số sinh viên
    logger.info("4. Demo gợi ý cá nhân hóa...")
    
    for i, profile in enumerate(student_profiles[:5]):  # Demo 5 sinh viên đầu
        logger.info(f"\n--- Sinh viên {profile.user_id} ---")
        logger.info(f"Learning Style: {profile.learning_style.value}")
        logger.info(f"Performance Level: {profile.performance_level.value}")
        logger.info(f"Engagement Score: {profile.engagement_score:.3f}")
        logger.info(f"Weak Areas: {profile.weak_areas}")
        logger.info(f"Strong Areas: {profile.strong_areas}")
        
        # Tạo gợi ý
        recommendation = recommendation_system.get_personalized_recommendation(profile)
        
        logger.info(f"\n🎯 GỢI Ý:")
        logger.info(f"   Hoạt động: {recommendation.recommended_state.value}")
        logger.info(f"   Độ tin cậy: {recommendation.confidence_score:.3f}")
        logger.info(f"   Lý do: {recommendation.reasoning}")
        logger.info(f"   Lợi ích dự kiến: {recommendation.expected_benefit:.3f}")
        logger.info(f"   Thời gian ước tính: {recommendation.time_estimate} phút")
        logger.info(f"   Độ khó: {recommendation.difficulty_level}")
        logger.info(f"   Prerequisites: {[s.value for s in recommendation.prerequisites]}")
    
    logger.info("\n=== PHASE 1 HOÀN THÀNH ===")
    logger.info("Hệ thống đã sẵn sàng để triển khai Phase 2!")

if __name__ == "__main__":
    main()
