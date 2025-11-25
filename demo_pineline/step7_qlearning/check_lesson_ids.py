#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra lesson IDs thực tế trong course structure
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from core.log_models import LogEvent

# Load course structure
course_structure_path = Path(__file__).parent / 'data' / 'course_structure.json'

print("=" * 80)
print("KIỂM TRA LESSON IDs")
print("=" * 80)

# Load và parse course structure
try:
    LogEvent._load_contextid_maps(5, str(course_structure_path))
    
    print(f"\n📚 Course Structure for course_id=5:")
    
    if 5 in LogEvent._subsection_instance_to_name:
        subsection_names = LogEvent._subsection_instance_to_name[5]
        
        print(f"\n   Tổng số lessons: {len(subsection_names)}")
        print(f"\n   Chi tiết lessons:")
        
        for idx, (lesson_id, lesson_name) in enumerate(sorted(subsection_names.items())):
            print(f"      Index {idx}: Lesson ID = {lesson_id}, Name = {lesson_name}")
        
        print(f"\n🔍 Phân tích:")
        lesson_ids = list(subsection_names.keys())
        print(f"   - Lesson IDs: {sorted(lesson_ids)}")
        print(f"   - Min ID: {min(lesson_ids)}")
        print(f"   - Max ID: {max(lesson_ids)}")
        
        if lesson_ids == list(range(len(lesson_ids))):
            print(f"   ✅ Lesson IDs là TUẦN TỰ (0, 1, 2, ...) - giống INDEX")
        else:
            print(f"   ⚠️  Lesson IDs KHÔNG tuần tự - là ID thật của Moodle")
    else:
        print("   ❌ Không tìm thấy course_id=5 trong course structure")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
