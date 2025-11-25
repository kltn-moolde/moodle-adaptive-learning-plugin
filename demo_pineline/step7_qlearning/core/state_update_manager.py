#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
State Update Manager - Quản lý logs và quyết định khi cập nhật state
======================================================================
Quản lý buffer logs, xác định time context (past/current/future) cho actions,
và quyết định khi nào đủ logs để cập nhật state + sinh gợi ý + cập nhật Q-table
"""

from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from core.log_models import LogEvent
from core.state_builder_v2 import StateBuilderV2
from core.action_space import ActionSpace
from core.reward_calculator_v2 import RewardCalculatorV2
from core.log_to_state_builder import LogToStateBuilder


@dataclass
class BufferedLog:
    """Single log entry in buffer"""
    log_event: LogEvent
    raw_log: Dict  # Lưu raw log dict để tái sử dụng với LogToStateBuilder
    timestamp: float
    processed: bool = False


@dataclass
class UserModuleContext:
    """Context for a specific (user_id, course_id, lesson_id)"""
    user_id: int
    course_id: int
    lesson_id: int
    
    # Buffer logs (chưa xử lý) - để quyết định khi nào update state
    log_buffer: List[BufferedLog] = field(default_factory=list)
    
    # Logs đã xử lý (để track recent actions) - GIỮ LẠI để tính engagement/phase
    processed_logs: List[LogEvent] = field(default_factory=list)
    
    # Rolling window: giữ tối đa N actions gần nhất để tính engagement/phase
    max_history_size: int = 20  # Giữ 20 actions gần nhất
    
    # State tracking
    current_state: Optional[Tuple] = None
    previous_state: Optional[Tuple] = None
    
    # Action tracking (để xác định time context)
    last_action: Optional[Tuple[str, str]] = None  # (action_type, time_context)
    action_history: List[Tuple[str, str]] = field(default_factory=list)
    
    # Module progress tracking
    current_module_idx: int = 0
    module_progress: float = 0.0
    avg_score: float = 0.5
    
    # Lesson progression tracking (từ Moodle API)
    past_lesson_ids: Set[int] = field(default_factory=set)  # Lessons đã học
    current_lesson_id: Optional[int] = None  # Lesson hiện tại
    future_lesson_ids: Set[int] = field(default_factory=set)  # Lessons chưa học
    all_lesson_ids: List[int] = field(default_factory=list)  # Tất cả lessons trong course
    lesson_progression_cached: bool = False  # Flag để biết đã cache chưa
    lesson_progression_cache_time: Optional[datetime] = None  # Thời gian cache
    
    # Last update time
    last_update_time: Optional[datetime] = None
    
    # Flags
    needs_state_update: bool = False
    needs_recommendation: bool = False


class StateUpdateManager:
    """
    Quản lý logs và quyết định khi cập nhật state
    
    Logic:
    1. Nhận logs → Thêm vào buffer
    2. Kiểm tra điều kiện cập nhật state:
       - Có đủ logs (min_logs threshold)
       - Có action mới (khác action trước)
       - Đủ thời gian (time_window)
       - Có thay đổi quan trọng (progress, score, action type)
    3. Khi đủ điều kiện:
       - Build state từ logs
       - Xác định time context cho actions (past/current/future)
       - Sinh gợi ý với đúng time context
       - Cập nhật Q-table (nếu có prev_state → current_state transition)
    """
    
    def __init__(
        self,
        state_builder: StateBuilderV2,
        action_space: ActionSpace,
        reward_calculator: Optional[RewardCalculatorV2] = None,
        min_logs_for_update: int = 3,  # Tối thiểu bao nhiêu logs để cập nhật
        max_buffer_size: int = 50,  # Tối đa logs trong buffer
        time_window_seconds: int = 300,  # 5 phút - thời gian chờ tối đa
        enable_qtable_updates: bool = False,
        agent = None,  # QLearningAgentV2 instance (nếu cập nhật Q-table)
        log_to_state_builder: Optional[LogToStateBuilder] = None,  # LogToStateBuilder instance (optional, sẽ tạo nếu None)
        moodle_client = None  # MoodleAPIClient instance (optional, để enrich với API)
    ):
        """
        Initialize State Update Manager
        
        Args:
            state_builder: StateBuilderV2 instance
            action_space: ActionSpace instance
            reward_calculator: RewardCalculatorV2 instance (optional)
            min_logs_for_update: Minimum logs needed before state update
            max_buffer_size: Maximum logs in buffer (truncate oldest if exceeded)
            time_window_seconds: Time window for batching logs
            enable_qtable_updates: Enable Q-table updates from transitions
            agent: QLearningAgentV2 instance (required if enable_qtable_updates=True)
            log_to_state_builder: LogToStateBuilder instance (optional, sẽ tạo từ state_builder nếu None)
            moodle_client: MoodleAPIClient instance (optional, để enrich với API)
        """
        self.state_builder = state_builder
        self.action_space = action_space
        self.reward_calculator = reward_calculator
        self.min_logs_for_update = min_logs_for_update
        self.max_buffer_size = max_buffer_size
        self.time_window_seconds = time_window_seconds
        self.enable_qtable_updates = enable_qtable_updates
        self.agent = agent
        self.moodle_client = moodle_client
        
        # Default max_history_size cho contexts (có thể override per context)
        self.default_max_history_size = 20  # Giữ 20 actions gần nhất để tính engagement/phase
        
        # Initialize LogToStateBuilder nếu chưa có
        # Tái sử dụng code từ LogToStateBuilder để build state với API enrichment
        if log_to_state_builder is None:
            # Lấy paths từ state_builder
            cluster_profiles_path = getattr(state_builder, 'cluster_profiles_path', 'data/cluster_profiles.json')
            course_structure_path = getattr(state_builder, 'course_structure_path', 'data/course_structure.json')
            excluded_clusters = getattr(state_builder, 'excluded_clusters', [3])
            recent_window = getattr(state_builder, 'recent_window', 10)
            
            self.log_to_state_builder = LogToStateBuilder(
                cluster_profiles_path=cluster_profiles_path,
                course_structure_path=course_structure_path,
                recent_window=recent_window,
                excluded_clusters=excluded_clusters,
                moodle_client=moodle_client
            )
        else:
            self.log_to_state_builder = log_to_state_builder
        
        # Buffer: (user_id, course_id, lesson_id) -> UserModuleContext
        self.contexts: Dict[Tuple[int, int, int], UserModuleContext] = {}
        
        # MULTI-COURSE SUPPORT: Per-course lesson_id mappings
        # course_id -> {lesson_id: index} mapping để hỗ trợ nhiều courses
        # Mỗi course có lesson_ids khác nhau (ví dụ: Course 5: [14,15,17], Course 6: [20,21,22])
        self.course_lesson_mappings: Dict[int, Dict[int, int]] = {}  # course_id -> {lesson_id: index}
        self.course_idx_to_lesson: Dict[int, Dict[int, int]] = {}    # course_id -> {index: lesson_id}
        self.course_lesson_names: Dict[int, Dict[int, str]] = {}     # course_id -> {lesson_id: name}
        self.course_n_modules: Dict[int, int] = {}                   # course_id -> n_modules
        
        # Statistics
        self.stats = {
            'logs_received': 0,
            'logs_buffered': 0,
            'state_updates': 0,
            'recommendations_generated': 0,
            'qtable_updates': 0,
            'errors': 0
        }
        
        # Initialization log (minimal)
        print(f"StateUpdateManager: min_logs={min_logs_for_update}, buffer_size={max_buffer_size}, time_window={time_window_seconds}s")
    
    def add_log(self, raw_log: Dict) -> Optional[Dict]:
        """
        Thêm log vào buffer và kiểm tra xem có cần cập nhật state không
        
        Args:
            raw_log: Raw log dictionary từ Moodle
            
        Returns:
            Dict với recommendation nếu đã cập nhật state, None nếu chưa
        """
        # Parse log → LogEvent
        event = LogEvent.from_dict(raw_log)
        if not event or event.lesson_id is None:
            return None  # Không thể xác định lesson
        
        # Log raw log và lesson info
        print(f"\n{'='*70}")
        print(f"📥 Log received:")
        print(f"   Raw log: {raw_log}")
        print(f"   → Lesson ID: {event.lesson_id}")
        print(f"   → Lesson Name: {event.lesson_name or 'N/A'}")
        print(f"{'='*70}")
        
        # Map cluster_id nếu là cluster 3 (excluded) → cluster 2 (mặc định)
        if event.cluster_id == 3 or event.cluster_id not in [0, 1, 2, 4, 5]:
            event.cluster_id = 2  # Default to medium cluster
        
        self.stats['logs_received'] += 1
        
        # CRITICAL: Lấy lesson_id từ log mới nhất (event.lesson_id)
        # Đảm bảo dùng đúng lesson_id mà user đang thao tác
        current_lesson_id = event.lesson_id
        
        # Get or create context với lesson_id từ log mới nhất
        key = (event.user_id, event.course_id, current_lesson_id)
        if key not in self.contexts:
            self.contexts[key] = UserModuleContext(
                user_id=event.user_id,
                course_id=event.course_id,
                lesson_id=current_lesson_id,  # Dùng lesson_id từ log mới nhất
                max_history_size=self.default_max_history_size  # Set max history size
            )
        
        context = self.contexts[key]
        
        # CRITICAL: Nếu context.lesson_id khác với lesson_id trong log mới
        # → User đã chuyển sang bài khác → Update context.lesson_id
        if context.lesson_id != current_lesson_id:
            # Tạo context mới cho lesson mới (nếu chưa có)
            new_key = (event.user_id, event.course_id, current_lesson_id)
            if new_key not in self.contexts:
                self.contexts[new_key] = UserModuleContext(
                    user_id=event.user_id,
                    course_id=event.course_id,
                    lesson_id=current_lesson_id,
                    max_history_size=self.default_max_history_size  # Set max history size
                )
            context = self.contexts[new_key]
        
        # Thêm log vào buffer
        buffered_log = BufferedLog(
            log_event=event,
            raw_log=raw_log,  # Lưu raw log để tái sử dụng với LogToStateBuilder
            timestamp=event.timestamp
        )
        context.log_buffer.append(buffered_log)
        self.stats['logs_buffered'] += 1
        
        # Trim buffer nếu quá lớn
        if len(context.log_buffer) > self.max_buffer_size:
            context.log_buffer = context.log_buffer[-self.max_buffer_size:]
        
        # Kiểm tra điều kiện cập nhật state
        should_update = self._should_update_state(context)
        
        if should_update:
            # Cập nhật state và sinh gợi ý
            return self._update_state_and_recommend(context)
        
        return None  # Chưa đủ điều kiện
    
    def _should_update_state(self, context: UserModuleContext) -> bool:
        """
        Kiểm tra xem có nên cập nhật state không
        
        Điều kiện:
        1. Có ít nhất min_logs_for_update logs trong buffer
        2. HOẶC có action mới (khác action trước)
        3. HOẶC đã quá time_window_seconds kể từ lần cập nhật cuối
        4. HOẶC có thay đổi quan trọng (score, progress)
        """
        buffer_size = len(context.log_buffer)
        
        # Điều kiện 1: Đủ logs tối thiểu (mặc định là 2)
        if buffer_size >= self.min_logs_for_update:
            return True
        
        # Điều kiện 2: Có action mới
        if buffer_size > 0:
            latest_log = context.log_buffer[-1].log_event
            latest_action_type = latest_log.action_type
            
            # So sánh với action gần nhất đã xử lý
            if context.processed_logs:
                last_processed_action = context.processed_logs[-1].action_type
                if latest_action_type != last_processed_action:
                    return True
            elif latest_action_type:  # Lần đầu có action
                return True
        
        # Điều kiện 3: Đã quá thời gian chờ
        if context.last_update_time:
            time_since_update = (datetime.now() - context.last_update_time).total_seconds()
            if time_since_update >= self.time_window_seconds:
                return True
        
        # Điều kiện 4: Có log với score (assessment action)
        if buffer_size > 0:
            latest_log = context.log_buffer[-1].log_event
            if latest_log.score is not None:  # Có score → quan trọng
                return True
        
        return False
    
    def _update_state_and_recommend(self, context: UserModuleContext) -> Dict:
        """
        Cập nhật state từ buffer logs và sinh gợi ý
        
        Returns:
            Dict với recommendation và metadata
        """
        try:
            # 1. Process logs từ buffer → aggregate data
            aggregated_data = self._aggregate_logs(context.log_buffer)
            
            # 2. Build state từ aggregated data
            new_state = self._build_state_from_aggregated(context, aggregated_data)
            
            # 3. Xác định time context cho actions
            time_context = self._determine_time_context(context, aggregated_data)
            
            # 4. Cập nhật Q-table nếu có previous_state
            qtable_update_info = None
            if self.enable_qtable_updates and self.agent and context.current_state:
                qtable_update_info = self._update_qtable(
                    context,
                    new_state,
                    aggregated_data
                )
            
            # 5. Update context
            # CRITICAL: Update lesson_id từ aggregated_data (log mới nhất)
            # Đảm bảo context.lesson_id luôn đúng với bài user đang thao tác
            latest_lesson_id = aggregated_data.get('lesson_id')
            if latest_lesson_id and latest_lesson_id != context.lesson_id:
                context.lesson_id = latest_lesson_id
            
            context.previous_state = context.current_state
            context.current_state = new_state
            context.module_progress = aggregated_data.get('progress', 0.0)
            context.avg_score = aggregated_data.get('avg_score', 0.5)
            context.current_module_idx = aggregated_data.get('module_idx', 0)
            
            # Move logs from buffer to processed (GIỮ LẠI để tính engagement/phase)
            for buffered_log in context.log_buffer:
                buffered_log.processed = True
                context.processed_logs.append(buffered_log.log_event)
            
            # Trim history: chỉ giữ N actions gần nhất (rolling window)
            # Không xóa hết, chỉ trim để tránh memory leak
            if len(context.processed_logs) > context.max_history_size:
                removed_count = len(context.processed_logs) - context.max_history_size
                context.processed_logs = context.processed_logs[-context.max_history_size:]
                print(f"   📝 Trimmed history: removed {removed_count} old logs, keeping {len(context.processed_logs)} recent actions")
            
            context.log_buffer.clear()  # Chỉ clear buffer, giữ history
            context.last_update_time = datetime.now()
            
            self.stats['state_updates'] += 1
            
            # 6. Generate recommendation với đúng time context
            # CRITICAL: Dùng lesson_id từ aggregated_data (log mới nhất), không dùng context.lesson_id cũ
            recommendation_lesson_id = aggregated_data.get('lesson_id', context.lesson_id)
            
            recommendation = {
                'user_id': context.user_id,
                'course_id': context.course_id,
                'lesson_id': recommendation_lesson_id,  # Dùng lesson_id từ log mới nhất
                'state': new_state,
                'previous_state': context.previous_state,
                'time_context': time_context,
                'recommendations': [],  # Sẽ được fill bởi caller
                'state_updated': True,
                'qtable_updated': qtable_update_info is not None,
                'qtable_update_info': qtable_update_info
            }
            
            return recommendation
            
        except Exception as e:
            print(f"❌ Error updating state: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            return None
    
    def _aggregate_logs(self, log_buffer: List[BufferedLog]) -> Dict:
        """
        Aggregate logs trong buffer thành intermediate data
        TÁI SỬ DỤNG: Sử dụng LogToStateBuilder._build_intermediate_data()
        
        Returns:
            Dict với aggregated metrics (tương thích với format cũ)
        """
        if not log_buffer:
            return {}
        
        # Convert BufferedLog list thành raw_logs format cho LogToStateBuilder
        # Tái sử dụng raw_log đã lưu trong BufferedLog
        raw_logs = [buffered_log.raw_log for buffered_log in log_buffer]
        
        # Sử dụng LogToStateBuilder để build intermediate data
        intermediate_data = self.log_to_state_builder._build_intermediate_data(raw_logs)
        
        # Convert format từ LogToStateBuilder về format cũ (tương thích)
        # LogToStateBuilder trả về: Dict[(user_id, course_id, lesson_id), Dict]
        # Chúng ta cần lấy data cho (user_id, course_id, lesson_id) từ log mới nhất
        if not intermediate_data:
            return {}
        
        # Lấy latest event để xác định key
        latest_event = log_buffer[-1].log_event
        key = (latest_event.user_id, latest_event.course_id, latest_event.lesson_id)
        
        if key not in intermediate_data:
            # Fallback: lấy data đầu tiên
            data = list(intermediate_data.values())[0]
        else:
            data = intermediate_data[key]
        
        # Map cluster_id: Nếu là cluster 3 (teacher/excluded), map về cluster 2
        cluster_id = data.get('cluster_id', 2)
        if cluster_id == 3 or cluster_id not in [0, 1, 2, 4, 5]:
            cluster_id = 2
        
        # Convert về format cũ (tương thích)
        return {
            'total_actions': data.get('total_actions', len(log_buffer)),
            'recent_actions': data.get('recent_actions', [])[-10:],  # Last 10
            'action_timestamps': data.get('action_timestamps', []),
            'scores': data.get('scores', []),
            'avg_score': data.get('avg_score', 0.5),
            'total_time_spent': data.get('total_time_spent', 0.0),
            'module_idx': data.get('lesson_id'),  # Will be mapped to index
            'progress': data.get('progress', 0.0),  # Will be enriched by API
            'cluster_id': cluster_id,
            'course_id': data.get('course_id', latest_event.course_id),
            'lesson_id': data.get('lesson_id', latest_event.lesson_id)
        }
    
    def _build_state_from_aggregated(
        self,
        context: UserModuleContext,
        aggregated_data: Dict
    ) -> Tuple:
        """
        Build 6D state từ aggregated data
        TÁI SỬ DỤNG: Sử dụng LogToStateBuilder để build state với API enrichment
        
        Đảm bảo:
        - Load course structure cho đúng course_id trước khi map lesson_id
        - Map lesson_id → module_idx
        - Enrich với Moodle API (progress, scores, cluster)
        """
        cluster_id = aggregated_data.get('cluster_id', 2)
        lesson_id = aggregated_data.get('lesson_id')
        course_id = aggregated_data.get('course_id', context.course_id)
        user_id = context.user_id
        
        # Đảm bảo cluster_id hợp lệ (map cluster 3 về 2 - mặc định)
        if cluster_id == 3 or cluster_id not in [0, 1, 2, 4, 5]:
            cluster_id = 2  # Default to medium cluster
        
        # CRITICAL: Đảm bảo course structure được load cho course_id này
        from core.log_models import LogEvent
        
        # Load course structure cho course_id nếu chưa có
        if course_id not in LogEvent._subsection_instance_to_name:
            try:
                course_structure_path = f"data/local/course_structure_{course_id}.json"
                from pathlib import Path
                path = Path(course_structure_path)
                
                if not path.exists():
                    course_structure_path = "data/local/course_structure.json"
                    path = Path(course_structure_path)
                    if not path.exists():
                        course_structure_path = "data/course_structure.json"
                
                LogEvent._load_contextid_maps(course_id, course_structure_path)
            except Exception as e:
                print(f"⚠️  WARNING: Could not load course structure for course_id={course_id}: {e}")
        
        # MULTI-COURSE SUPPORT: Build và maintain mapping riêng cho mỗi course
        if course_id in LogEvent._subsection_instance_to_name:
            subsection_names = LogEvent._subsection_instance_to_name[course_id]
            
            if course_id not in self.course_lesson_mappings:
                sorted_lessons = sorted(subsection_names.items())
                
                self.course_lesson_mappings[course_id] = {}
                self.course_idx_to_lesson[course_id] = {}
                self.course_lesson_names[course_id] = {}
                
                for idx, (lid, name) in enumerate(sorted_lessons):
                    self.course_lesson_mappings[course_id][lid] = idx
                    self.course_idx_to_lesson[course_id][idx] = lid
                    self.course_lesson_names[course_id][lid] = name
                
                self.course_n_modules[course_id] = len(sorted_lessons)
        
        # Verify lesson_id is in mapping for this course
        if course_id not in self.course_lesson_mappings:
            raise ValueError(f"Course {course_id} mapping not found. Please load course structure first.")
        
        lesson_mapping = self.course_lesson_mappings[course_id]
        if lesson_id not in lesson_mapping:
            available_lesson_ids = list(lesson_mapping.keys())
            print(f"❌ Error: Lesson ID {lesson_id} not in mapping for course {course_id}")
            print(f"   Available lesson IDs: {available_lesson_ids}")
            raise ValueError(f"Lesson ID {lesson_id} not found in course {course_id} structure")
        
        # Update state_builder mapping cho course này
        self.state_builder.lesson_id_to_idx = lesson_mapping.copy()
        self.state_builder.idx_to_lesson_id = self.course_idx_to_lesson[course_id].copy()
        self.state_builder.lesson_id_to_name = self.course_lesson_names[course_id].copy()
        self.state_builder.n_modules = self.course_n_modules[course_id]
        
        # CẢI THIỆN: Combine processed_logs (history) + log_buffer (new) để có đủ data
        # cho engagement_level và learning_phase calculation
        all_recent_actions = []
        all_action_timestamps = []
        all_scores = []
        total_time_from_history = 0.0
        
        # Lấy từ processed_logs (history) - giữ lại window size
        history_window = min(context.max_history_size, len(context.processed_logs))
        for event in context.processed_logs[-history_window:]:
            all_recent_actions.append(event.action_type)
            all_action_timestamps.append(event.timestamp)
            if event.score is not None:
                all_scores.append(event.score)
            if event.time_spent:
                total_time_from_history += event.time_spent
        
        # Thêm từ log_buffer (new logs)
        for buffered_log in context.log_buffer:
            event = buffered_log.log_event
            all_recent_actions.append(event.action_type)
            all_action_timestamps.append(event.timestamp)
            if event.score is not None:
                all_scores.append(event.score)
            if event.time_spent:
                total_time_from_history += event.time_spent
        
        # Combine scores từ history + buffer
        combined_scores = all_scores + aggregated_data.get('scores', [])
        combined_avg_score = sum(combined_scores) / len(combined_scores) if combined_scores else aggregated_data.get('avg_score', context.avg_score)
        
        # Combine time spent
        combined_time_spent = total_time_from_history + aggregated_data.get('total_time_spent', 0.0)
        
        # TÁI SỬ DỤNG: Sử dụng LogToStateBuilder để build intermediate data và enrich với API
        # 1. Build intermediate data từ aggregated_data (nhưng dùng combined actions/timestamps)
        intermediate_key = (user_id, course_id, lesson_id)
        intermediate_data = {
            intermediate_key: {
                'user_id': user_id,
                'course_id': course_id,
                'lesson_id': lesson_id,
                'lesson_name': self.course_lesson_names[course_id].get(lesson_id, 'Unknown'),
                'cluster_id': cluster_id,
                'total_actions': len(all_recent_actions),  # Tổng từ history + buffer
                'recent_actions': all_recent_actions,  # Combined từ history + buffer
                'action_timestamps': all_action_timestamps,  # Combined từ history + buffer
                'scores': combined_scores,  # Combined scores
                'avg_score': combined_avg_score,  # Combined avg score
                'total_time_spent': combined_time_spent,  # Combined time spent
                'progress': aggregated_data.get('progress', context.module_progress),
                'completed_activities': [],
                'total_activities': 0
            }
        }
        
        # 2. Enrich với Moodle API (nếu có moodle_client) - không log chi tiết
        if self.moodle_client:
            try:
                intermediate_data = self.log_to_state_builder._enrich_states_with_api(intermediate_data)
            except Exception as e:
                # Continue with default values
                pass
        
        # 3. Convert to 6D state using LogToStateBuilder
        states_6d = self.log_to_state_builder._convert_to_6d_states(intermediate_data)
        
        if intermediate_key not in states_6d:
            raise ValueError(f"Failed to build state for {intermediate_key}")
        
        state = states_6d[intermediate_key]
        
        # In state vector
        print(f"📊 State vector: {state}")
        
        return state
    
    def _load_lesson_progression(self, context: UserModuleContext) -> bool:
        """
        Load lesson progression từ Moodle API và cache vào context
        
        Args:
            context: UserModuleContext
            
        Returns:
            True nếu load thành công, False nếu có lỗi
        """
        # Kiểm tra cache (cache trong 5 phút)
        if context.lesson_progression_cached and context.lesson_progression_cache_time:
            cache_age = (datetime.now() - context.lesson_progression_cache_time).total_seconds()
            if cache_age < 300:  # 5 phút
                return True  # Cache còn hiệu lực
        
        # Load từ API nếu có moodle_client
        if not self.moodle_client:
            return False
        
        try:
            progression = self.moodle_client.get_lesson_progression(
                user_id=context.user_id,
                course_id=context.course_id
            )
            
            # Update context với lesson progression
            context.past_lesson_ids = set(progression.get('past_lesson_ids', []))
            context.current_lesson_id = progression.get('current_lesson_id')
            context.future_lesson_ids = set(progression.get('future_lesson_ids', []))
            context.all_lesson_ids = progression.get('all_lesson_ids', [])
            context.lesson_progression_cached = True
            context.lesson_progression_cache_time = datetime.now()
            
            print(f"   ✓ Lesson progression loaded:")
            print(f"      - Past lessons: {context.past_lesson_ids}")
            print(f"      - Current lesson: {context.current_lesson_id}")
            print(f"      - Future lessons: {context.future_lesson_ids}")
            
            return True
        except Exception as e:
            print(f"   ⚠️  Error loading lesson progression: {e}")
            return False
    
    def _determine_time_context(
        self,
        context: UserModuleContext,
        aggregated_data: Dict = None
    ) -> str:
        """
        Xác định time context cho action recommendation
        
        Logic cải thiện:
        - past: Lesson hiện tại nằm trong past_lesson_ids HOẶC có nhiều review actions
        - current: Lesson hiện tại là current_lesson_id HOẶC không xác định được
        - future: Lesson hiện tại nằm trong future_lesson_ids HOẶC progress > 0.8
        
        Returns:
            'past', 'current', hoặc 'future'
        """
        if aggregated_data is None:
            aggregated_data = {}
        
        # Load lesson progression nếu chưa có
        self._load_lesson_progression(context)
        
        current_lesson_id = aggregated_data.get('lesson_id', context.lesson_id)
        progress = aggregated_data.get('progress', context.module_progress)
        
        # Analyze recent actions để xác định context
        recent_actions = aggregated_data.get('recent_actions', [])
        if not recent_actions and context.processed_logs:
            recent_actions = [log.action_type for log in context.processed_logs[-5:]]
        
        # Nếu có nhiều review actions → past
        review_count = sum(1 for a in recent_actions if 'review' in a.lower())
        if review_count >= 2:
            return 'past'
        
        # Xác định dựa vào lesson progression (nếu đã load được)
        if context.lesson_progression_cached:
            if current_lesson_id in context.past_lesson_ids:
                return 'past'
            elif current_lesson_id == context.current_lesson_id:
                # Nếu progress cao, có thể là future
                if progress > 0.8:
                    return 'future'
                return 'current'
            elif current_lesson_id in context.future_lesson_ids:
                return 'future'
        
        # Fallback: dùng logic cũ dựa vào progress
        if progress > 0.8 and recent_actions:
            return 'future'
        
        # Default: current (user đang học module hiện tại)
        return 'current'
    
    def _get_activities_for_lesson(
        self,
        course_id: int,
        lesson_id: int
    ) -> List[int]:
        """
        Lấy danh sách activity IDs từ course structure cho một lesson cụ thể
        
        Args:
            course_id: Course ID
            lesson_id: Lesson ID (section.id với component="mod_subsection")
        
        Returns:
            List of activity IDs (module.id) trong lesson đó
        """
        from pathlib import Path
        
        # Try to load course structure
        course_structure_paths = [
            f"data/local/course_structure_{course_id}.json",
            "data/local/course_structure.json",
            "data/course_structure.json"
        ]
        
        course_structure_path = None
        for path_str in course_structure_paths:
            path = Path(path_str)
            if not path.is_absolute():
                project_root = Path(__file__).parent.parent
                path = project_root / path_str
            
            if path.exists():
                course_structure_path = str(path)
                break
        
        if not course_structure_path:
            print(f"   ⚠️  Course structure not found for course {course_id}")
            return []
        
        try:
            with open(course_structure_path, 'r', encoding='utf-8') as f:
                course_data = json.load(f)
            
            # Tìm section có id == lesson_id và component == "mod_subsection"
            contents = course_data.get('contents', [])
            activities = []
            
            for section in contents:
                section_id = section.get('id')
                section_component = section.get('component')
                
                # Chỉ xử lý section có component="mod_subsection"
                if section_id == lesson_id and section_component == 'mod_subsection':
                    # Lấy tất cả modules (activities) trong section này
                    modules = section.get('modules', [])
                    for module in modules:
                        activity_id = module.get('id')
                        if activity_id:
                            activities.append(activity_id)
                    break
            
            print(f"   ✓ Found {len(activities)} activities for lesson {lesson_id}")
            return activities
            
        except Exception as e:
            print(f"   ⚠️  Error loading activities for lesson {lesson_id}: {e}")
            return []
    
    def _update_qtable(
        self,
        context: UserModuleContext,
        new_state: Tuple,
        aggregated_data: Dict
    ) -> Optional[Dict]:
        """
        Cập nhật Q-table với state transition
        
        Args:
            context: UserModuleContext
            new_state: New state tuple
            aggregated_data: Aggregated log data
            
        Returns:
            Dict với update info hoặc None nếu không update
        """
        if not context.previous_state:
            return None  # Không có previous state
        
        # Xác định action đã làm từ logs
        if not aggregated_data.get('recent_actions'):
            return None
        
        # Action gần nhất
        latest_action_type = aggregated_data['recent_actions'][-1]
        
        # Map action_type string → action_idx trong action_space
        action_idx = self._map_action_type_to_idx(latest_action_type, context)
        
        if action_idx is None:
            return None
        
        # Tính reward
        reward = 0.0
        if self.reward_calculator:
            try:
                # Build action dict
                action_dict = {
                    'type': latest_action_type,
                    'difficulty': 'medium'
                }
                
                # Build outcome dict
                outcome = {
                    'completed': True,  # Assume completed nếu có log
                    'score': aggregated_data.get('avg_score'),
                    'success': aggregated_data.get('avg_score', 0.5) >= 0.5,
                    'time': aggregated_data.get('total_time_spent', 0.0)
                }
                
                reward = self.reward_calculator.calculate_reward(
                    state=new_state,
                    action=action_dict,
                    outcome=outcome,
                    previous_state=context.previous_state,
                    student_id=context.user_id
                )
            except Exception as e:
                print(f"⚠️  Reward calculation error: {e}")
                reward = 0.0
        else:
            # Simple reward: score improvement
            prev_score = context.previous_state[3] if len(context.previous_state) > 3 else 0.5
            new_score = new_state[3] if len(new_state) > 3 else 0.5
            reward = (new_score - prev_score) * 10.0  # Scale reward
        
        # Update Q-table
        try:
            self.agent.update(
                state=context.previous_state,
                action=action_idx,
                reward=reward,
                next_state=new_state,
                is_terminal=False
            )
            
            self.stats['qtable_updates'] += 1
            
            return {
                'action_idx': action_idx,
                'action_type': latest_action_type,
                'reward': reward,
                'prev_state': context.previous_state,
                'new_state': new_state
            }
        except Exception as e:
            print(f"⚠️  Q-table update error: {e}")
            return None
    
    def _map_action_type_to_idx(
        self,
        action_type: str,
        context: UserModuleContext
    ) -> Optional[int]:
        """
        Map action_type string → action index trong action_space
        
        Với time context (past/current/future)
        """
        # Xác định time context
        time_context = self._determine_time_context(context, {})
        
        # Map action_type → action trong action_space
        # get_action_by_tuple takes (action_type, time_context) tuple
        action = self.action_space.get_action_by_tuple(action_type, time_context)
        
        if action:
            return action.index
        
        # Fallback: tìm action tương tự
        actions_by_type = self.action_space.get_actions_by_type(action_type)
        if actions_by_type:
            # Ưu tiên current context
            for a in actions_by_type:
                if a.time_context == 'current':
                    return a.index
            # Nếu không có current, chọn bất kỳ
            if actions_by_type:
                return actions_by_type[0].index
        
        # Final fallback: map action_type string → action type trong action space
        # Ví dụ: "view_content" → tìm trong action space
        for action in self.action_space.get_actions():
            if action.action_type == action_type and action.time_context == time_context:
                return action.index
        
        # Nếu vẫn không tìm thấy, trả về action đầu tiên (fallback)
        if self.action_space.get_actions():
            return self.action_space.get_actions()[0].index
        
        return None
    
    def get_recommendations_for_context(
        self,
        user_id: int,
        course_id: int,
        lesson_id: int,
        recommendation_service
    ) -> Optional[Dict]:
        """
        Get recommendations cho một context cụ thể
        
        Args:
            user_id, course_id, lesson_id: Context identifier
            recommendation_service: RecommendationService instance
            
        Returns:
            Dict với recommendations hoặc None
        """
        print(f"\n🔍 DEBUG: get_recommendations_for_context")
        print(f"   Input: user_id={user_id}, course_id={course_id}, lesson_id={lesson_id}")
        
        key = (user_id, course_id, lesson_id)
        context = self.contexts.get(key)
        
        if not context:
            print(f"   ❌ Context not found for key {key}")
            return None
        
        if not context.current_state:
            print(f"   ❌ Current state is None")
            return None
        
        print(f"   ✓ Context found: lesson_id={context.lesson_id}, state={context.current_state}")
        
        # Get time context
        time_context = self._determine_time_context(context, {})
        print(f"   ✓ Time context: {time_context}")
        
        # Get recommendations
        print(f"   → Calling recommendation_service.get_recommendations()...")
        print(f"      - state: {context.current_state}")
        print(f"      - cluster_id: {int(context.current_state[0])}")
        print(f"      - module_idx from state: {int(context.current_state[1])}")
        print(f"      - module_idx from context: {context.current_module_idx}")
        
        # CRITICAL: module_idx từ state là index (0-5), không phải lesson_id
        module_idx_from_state = int(context.current_state[1])
        
        # Try to get LO mastery from reward_calculator if available
        lo_mastery = None
        if self.reward_calculator:
            try:
                lo_mastery = self.reward_calculator.get_lo_mastery_state(user_id)
                print(f"      - lo_mastery: Retrieved from reward_calculator ({len(lo_mastery)} LOs)")
            except Exception as e:
                print(f"      - lo_mastery: Failed to retrieve ({e}), using None")
                lo_mastery = None
        else:
            print(f"      - lo_mastery: None (reward_calculator not available)")
        
        # Load lesson progression nếu chưa có
        self._load_lesson_progression(context)
        
        # Get lesson info để pass vào recommendation_service
        current_lesson_id = context.lesson_id
        past_lesson_ids = context.past_lesson_ids
        future_lesson_ids = context.future_lesson_ids
        
        recommendations = recommendation_service.get_recommendations(
            state=context.current_state,
            cluster_id=int(context.current_state[0]),
            top_k=3,
            lo_mastery=lo_mastery,
            module_idx=module_idx_from_state,  # Dùng module_idx từ state
            course_id=context.course_id,
            lesson_id=current_lesson_id,
            past_lesson_ids=past_lesson_ids,
            future_lesson_ids=future_lesson_ids
        )
        
        print(f"   ← Got {len(recommendations) if recommendations else 0} recommendations from service")
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"      {i}. action_id={rec.get('action_id')}, action_type={rec.get('action_type')}, time_context={rec.get('time_context')}, q_value={rec.get('q_value', 0):.3f}")
        
        # Filter recommendations by time_context
        print(f"   → Filtering recommendations by time_context: {time_context}")
        filtered_recommendations = [
            rec for rec in recommendations
            if rec.get('time_context') == time_context
        ]
        
        print(f"   ← Filtered to {len(filtered_recommendations)} recommendations matching time_context")
        
        if not filtered_recommendations:
            filtered_recommendations = recommendations[:3]  # Fallback
            print(f"   ⚠️  No recommendations match time_context, using top 3 as fallback")
        
        result = {
            'user_id': user_id,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'state': context.current_state,
            'time_context': time_context,
            'recommendations': filtered_recommendations,
            'module_progress': context.module_progress,
            'avg_score': context.avg_score
        }
        
        print(f"   ✓ Returning result with {len(filtered_recommendations)} recommendations")
        return result
    
    def force_update_all_contexts(self) -> List[Dict]:
        """
        Force update tất cả contexts có logs trong buffer
        
        Returns:
            List of recommendation dicts
        """
        updates = []
        
        for key, context in self.contexts.items():
            if context.log_buffer and len(context.log_buffer) > 0:
                result = self._update_state_and_recommend(context)
                if result:
                    updates.append(result)
        
        return updates
    
    def get_statistics(self) -> Dict:
        """Get manager statistics"""
        return {
            **self.stats,
            'active_contexts': len([c for c in self.contexts.values() if c.log_buffer]),
            'total_contexts': len(self.contexts),
            'supported_courses': len(self.course_lesson_mappings),  # Multi-course support
            'course_ids': list(self.course_lesson_mappings.keys())  # List of course IDs
        }
    
    def get_course_mapping_info(self, course_id: int) -> Optional[Dict]:
        """
        Get lesson_id to index mapping info for a specific course
        
        Args:
            course_id: Course ID
            
        Returns:
            Dict với mapping info hoặc None nếu course không tồn tại
        """
        if course_id not in self.course_lesson_mappings:
            return None
        
        return {
            'course_id': course_id,
            'lesson_id_to_idx': self.course_lesson_mappings[course_id],
            'idx_to_lesson_id': self.course_idx_to_lesson.get(course_id, {}),
            'lesson_names': self.course_lesson_names.get(course_id, {}),
            'n_modules': self.course_n_modules.get(course_id, 0)
        }
    
    def cleanup_old_contexts(self, max_age_hours: int = 24):
        """
        Cleanup contexts không hoạt động quá lâu
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        keys_to_remove = []
        for key, context in self.contexts.items():
            if context.last_update_time and context.last_update_time < cutoff_time:
                if not context.log_buffer:  # Chỉ remove nếu không có logs pending
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.contexts[key]
        
        # Cleanup completed silently

