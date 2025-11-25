#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Models - Data structures for log processing
================================================
Định nghĩa các data model cho log events từ Moodle
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import json


class ActionType(str, Enum):
    VIEW_CONTENT = "view_content"
    VIEW_ASSIGNMENT = "view_assignment"
    ATTEMPT_QUIZ = "attempt_quiz"
    SUBMIT_QUIZ = "submit_quiz"
    REVIEW_QUIZ = "review_quiz"
    SUBMIT_ASSIGNMENT = "submit_assignment"
    POST_FORUM = "post_forum"
    VIEW_FORUM = "view_forum"
    DOWNLOAD_RESOURCE = "download_resource"
    
    @classmethod
    def normalize(cls, raw_action: str) -> Optional[str]:
        if not raw_action:
            return None
        raw_lower = raw_action.lower().strip()
        
        if 'quiz' in raw_lower and 'attempt' in raw_lower:
            return cls.ATTEMPT_QUIZ
        if 'quiz' in raw_lower and ('submit' in raw_lower or 'finish' in raw_lower):
            return cls.SUBMIT_QUIZ
        if 'quiz' in raw_lower and 'review' in raw_lower:
            return cls.REVIEW_QUIZ
        if 'assignment' in raw_lower and ('submit' in raw_lower or 'upload' in raw_lower):
            return cls.SUBMIT_ASSIGNMENT
        if 'assignment' in raw_lower and 'view' in raw_lower:
            return cls.VIEW_ASSIGNMENT
        if 'forum' in raw_lower and ('post' in raw_lower or 'reply' in raw_lower):
            return cls.POST_FORUM
        if 'forum' in raw_lower and 'view' in raw_lower:
            return cls.VIEW_FORUM
        if any(keyword in raw_lower for keyword in ['view', 'page', 'resource', 'url', 'book']):
            if 'download' in raw_lower or 'file' in raw_lower:
                return cls.DOWNLOAD_RESOURCE
            return cls.VIEW_CONTENT
        return None


@dataclass
class LogEvent:
    user_id: int
    cluster_id: int
    module_id: int
    action_type: str
    timestamp: float
    
    score: Optional[float] = None
    progress: Optional[float] = None
    time_spent: Optional[float] = None
    success: Optional[bool] = None
    raw_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # THÊM 3 FIELD MỚI - SIÊU HỮU ÍCH CHO RL
    course_id: Optional[int] = None        # ID của khóa học
    lesson_id: Optional[int] = None        # ID của bài học (subsection instance id)
    lesson_name: Optional[str] = None      # Tên bài học

    def __post_init__(self):
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.timestamp()
        if not (0 <= self.cluster_id <= 6):
            self.cluster_id = 3
        if self.score is not None:
            self.score = max(0.0, min(1.0, self.score))
        if self.progress is not None:
            self.progress = max(0.0, min(1.0, self.progress))

    # ===================================================================
    # MAIN: Load all mappings from course_structure.json (once per course)
    # ===================================================================
    @classmethod
    def _load_contextid_maps(cls, course_id: int, course_structure_path: str = None):
        """
        Load course structure for a specific course_id
        
        Args:
            course_id: Course ID to load structure for
            course_structure_path: Path to course structure JSON file
                                  Default: data/local/course_structure_{course_id}.json
        """
        # Check if already loaded for this course
        # NOTE: Force reload để đảm bảo dùng logic mới (map contextid → section.id)
        # Nếu cần cache, có thể bỏ comment dòng dưới
        # if course_id in cls._contextid_to_module_map:
        #     return  # Already loaded for this course
        
        # Force clear cache cho course này để reload với logic mới
        if course_id in cls._contextid_to_module_map:
            del cls._contextid_to_module_map[course_id]
        if course_id in cls._contextid_to_subsection_map:
            del cls._contextid_to_subsection_map[course_id]
        if course_id in cls._subsection_instance_to_name:
            del cls._subsection_instance_to_name[course_id]

        import json
        from pathlib import Path

        # Auto-generate path if not provided
        if course_structure_path is None:
            course_structure_path = f"data/local/course_structure_{course_id}.json"
            # Fallback to default for backward compatibility
            path = Path(course_structure_path)
            if not path.exists():
                course_structure_path = "data/local/course_structure.json"
                path = Path(course_structure_path)
                if not path.exists():
                    course_structure_path = "data/course_structure.json"
        
        # Initialize storage for this course
        cls._contextid_to_module_map[course_id] = {}
        cls._contextid_to_subsection_map[course_id] = {}
        cls._subsection_instance_to_name[course_id] = {}

        try:
            path = Path(course_structure_path)
            if not path.is_absolute():
                # Resolve relative path từ project root
                project_root = Path(__file__).parent.parent
                path = project_root / course_structure_path
            
            if not path.exists():
                raise FileNotFoundError(f"Không tìm thấy: {path}")
            
            course_structure_path = str(path)

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Map contextid → section id (parent có component="mod_subsection")
            # Flow:
            # 1. Duyệt qua tất cả sections
            # 2. Nếu section có component="mod_subsection", lấy section.id làm lesson_id
            # 3. Map tất cả modules trong section đó: contextid → section.id
            # Ví dụ: contextid=147 → tìm module có contextid=147 → tìm parent section có component="mod_subsection" → lấy section.id=43
            
            for section in data.get('contents', []):
                section_id = section.get('id')  # Section ID (38, 39, 40, 43...) - ĐÂY LÀ LESSON_ID
                section_type = section.get('component')  # "mod_subsection" hoặc null
                section_name = section.get('name', '').strip()
                modules = section.get('modules', [])

                # CHỈ XỬ LÝ SECTION CÓ component="mod_subsection"
                # Đây là section chứa nội dung bài học (ví dụ: id=43, name="Bài 6: ...")
                if section_type == 'mod_subsection':
                    # Lưu mapping: section_id → tên bài học
                    if section_id and section_name:
                        cls._subsection_instance_to_name[course_id][section_id] = section_name
                    
                    # Map tất cả modules trong section này: contextid → section.id
                    for module in modules:
                        # Lấy contextid từ module (đây là giá trị trong log: contextinstanceid)
                        contextid = module.get('contextid')
                        module_id = module.get('id')
                        
                        if contextid:
                            # Map contextid → section.id (lesson_id)
                            # Ví dụ: contextid=147 → section.id=43
                            cls._contextid_to_subsection_map[course_id][contextid] = section_id
                            # Map contextid → module_id (để backward compatibility)
                            cls._contextid_to_module_map[course_id][contextid] = module_id
                        
                        # Cũng map module.id → section.id (nếu module.id khác contextid, để hỗ trợ cả 2 cách)
                        if module_id and module_id != contextid:
                            cls._contextid_to_subsection_map[course_id][module_id] = section_id
                            cls._contextid_to_module_map[course_id][module_id] = module_id

        except Exception as e:
            print(f"❌ LỖI khi load course structure: {e}")
            import traceback
            traceback.print_exc()
            
    # ===================================================================
    # Helper methods - MULTI-COURSE SUPPORT
    # ===================================================================
    @classmethod
    def getModuleIdFromContextInstanceId(cls, course_id: int, contextinstanceid: int):
        if contextinstanceid is None or course_id is None:
            return None
        cls._load_contextid_maps(course_id)
        return cls._contextid_to_module_map.get(course_id, {}).get(contextinstanceid)

    @classmethod
    def get_subsection_id_for_cmid(cls, course_id: int, cmid: int):
        if course_id is None or cmid is None:
            return None
        cls._load_contextid_maps(course_id)
        return cls._contextid_to_subsection_map.get(course_id, {}).get(cmid)

    @classmethod
    def get_subsection_name(cls, course_id: int, subsection_instance_id: int) -> str:
        if subsection_instance_id is None or course_id is None:
            return "Unknown Lesson"
        cls._load_contextid_maps(course_id)
        return cls._subsection_instance_to_name.get(course_id, {}).get(subsection_instance_id, "Unknown Lesson")

    # Siêu tiện: lấy tên bài học trực tiếp từ cmid
    @classmethod
    def get_lesson_name_for_cmid(cls, course_id: int, cmid: int) -> str:
        if not cmid or not course_id:
            return "Unknown Lesson"
        subsection_id = cls.get_subsection_id_for_cmid(course_id, cmid)
        return cls.get_subsection_name(course_id, subsection_id)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['LogEvent']:
        user_id = data.get('user_id') or data.get('userid')
        cluster_id = data.get('cluster_id', 3)
        course_id = data.get('course_id') or data.get('courseid')
        
        # CRITICAL: course_id is required for multi-course support
        if course_id is None:
            print("⚠️ Warning: course_id missing in log data, cannot process")
            return None
        
        contextinstanceid = data.get('contextinstanceid')
        raw_action = data.get('action') or data.get('eventname') or data.get('action_type')
        timestamp = data.get('timestamp') or data.get('timecreated') or data.get('time')
        
        # Get module and lesson info WITH course_id
        module_id = cls.getModuleIdFromContextInstanceId(course_id, contextinstanceid)
        lesson_name = cls.get_lesson_name_for_cmid(course_id, contextinstanceid)
        lesson_id = cls.get_subsection_id_for_cmid(course_id, contextinstanceid)

        if raw_action and 'course' in raw_action.lower() and 'viewed' in raw_action.lower():
            return None

        if module_id is None:
            return None

        action_type = ActionType.normalize(raw_action) or ActionType.VIEW_CONTENT
        score = data.get('score') or data.get('grade')
        if score is not None and score > 1.0:
            score = score / 100.0

        # Lesson identification (removed - now handled in state_update_manager debug log)

        event = cls(
            user_id=user_id,
            cluster_id=cluster_id,
            module_id=module_id,
            action_type=action_type,
            timestamp=timestamp,
            score=score,
            progress=data.get('progress'),
            time_spent=data.get('time_spent') or data.get('duration'),
            success=data.get('success'),
            raw_action=raw_action,
            course_id=course_id,
            lesson_id=lesson_id,
            lesson_name=lesson_name,
            metadata=data.get('metadata', {})
        )

        return event

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'cluster_id': self.cluster_id,
            'module_id': self.module_id,
            'action_type': self.action_type,
            'timestamp': self.timestamp,
            'score': self.score,
            'progress': self.progress,
            'time_spent': self.time_spent,
            'success': self.success,
            'raw_action': self.raw_action,
            'metadata': self.metadata
        }


# Initialize class-level caches as true class attributes (not dataclass fields)
# These are shared across all LogEvent instances and organized per course_id
LogEvent._contextid_to_module_map = {}
LogEvent._contextid_to_subsection_map = {}
LogEvent._subsection_instance_to_name = {}


# (UserLogSummary giữ nguyên như cũ – không cần sửa)
@dataclass
class UserLogSummary:
    user_id: int
    cluster_id: int
    module_id: int
    total_actions: int = 0
    unique_action_types: List[str] = field(default_factory=list)
    recent_actions: List[str] = field(default_factory=list)
    action_timestamps: List[float] = field(default_factory=list)
    avg_score: float = 0.0
    recent_scores: List[float] = field(default_factory=list)
    module_progress: float = 0.0
    total_time_spent: float = 0.0
    time_on_task: float = 0.0
    first_action_time: Optional[float] = None
    last_action_time: Optional[float] = None
    quiz_attempts: int = 0
    quiz_failures: int = 0
    consecutive_failures: int = 0
    repeated_views_same_content: int = 0

    def update_from_event(self, event: LogEvent):
        self.total_actions += 1
        if event.action_type not in self.unique_action_types:
            self.unique_action_types.append(event.action_type)
        self.recent_actions.append(event.action_type)
        self.action_timestamps.append(event.timestamp)
        if event.score is not None:
            self.recent_scores.append(event.score)
            self.avg_score = sum(self.recent_scores) / len(self.recent_scores)
        if event.progress is not None:
            self.module_progress = max(self.module_progress, event.progress)
        if event.time_spent is not None:
            self.total_time_spent += event.time_spent
            self.time_on_task += event.time_spent
        if self.first_action_time is None:
            self.first_action_time = event.timestamp
        self.last_action_time = event.timestamp
        if 'quiz' in event.action_type:
            self.quiz_attempts += 1
            if event.success is False or (event.score is not None and event.score < 0.5):
                self.quiz_failures += 1
                self.consecutive_failures += 1
            else:
                self.consecutive_failures = 0

    def trim_recent_window(self, window_size: int = 10):
        self.recent_actions = self.recent_actions[-window_size:]
        self.action_timestamps = self.action_timestamps[-window_size:]
        self.recent_scores = self.recent_scores[-window_size:]

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


if __name__ == '__main__':
    print("=" * 70)
    print("Testing Log Models - Multi-Course Support")
    print("=" * 70)

    # Test với course_id = 5 (default course)
    test_course_id = 5
    print(f"\nTesting with Course ID: {test_course_id}")
    
    # Load course structure
    LogEvent._load_contextid_maps(test_course_id)
    
    # Test tên bài học
    print(f"\nTest get_lesson_name_for_cmid(course={test_course_id}, cmid=61):")
    print(LogEvent.get_lesson_name_for_cmid(test_course_id, 61))

    print(f"\nTest get_lesson_name_for_cmid(course={test_course_id}, cmid=66):")
    print(LogEvent.get_lesson_name_for_cmid(test_course_id, 66))
    
    # Test với course khác (nếu có)
    test_course_id_2 = 10
    print(f"\nTesting with Course ID: {test_course_id_2}")
    try:
        LogEvent._load_contextid_maps(test_course_id_2)
        print(f"✓ Successfully loaded course structure for course {test_course_id_2}")
    except FileNotFoundError as e:
        print(f"⚠️ Course {test_course_id_2} structure not found (expected)")

    print("\nLog Models test completed!")
    print("=" * 70)