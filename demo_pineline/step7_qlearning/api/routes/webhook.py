"""
Webhook endpoints for Moodle events
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models import WebhookPayload, WebhookResponse
from ..dependencies import (
    state_update_manager,
    recommendation_service,
    state_repository
)

router = APIRouter(prefix='/webhook', tags=['webhook'])


async def process_events_async(
    logs: List[Dict],
    event_id: Optional[str] = None
):
    """
    Process events asynchronously using StateUpdateManager
    
    Flow:
    1. Add logs to buffer (StateUpdateManager)
    2. Manager tự động quyết định khi nào cập nhật state
    3. Khi đủ điều kiện: cập nhật state + sinh gợi ý + cập nhật Q-table
    4. Save states và recommendations vào MongoDB
    """
    try:
        print(f"\n{'='*70}")
        print(f"🔄 Background Processing Started (event_id: {event_id})")
        print(f"{'='*70}")
        print(f"📊 Received {len(logs)} logs")
        
        # Step 1: Add logs to StateUpdateManager buffer
        print(f"\n📥 Step 1: Adding logs to buffer...")
        recommendations_generated = []
        states_updated = []
        
        for log in logs:
            try:
                # Add log to buffer - manager sẽ tự quyết định khi nào cập nhật
                result = state_update_manager.add_log(log)
                
                if result:
                    # State đã được cập nhật → có recommendation
                    recommendations_generated.append(result)
                    states_updated.append(result)
                    print(f"  ✓ State updated for user {result['user_id']}, lesson {result['lesson_id']}")
            except Exception as e:
                print(f"  ✗ Error processing log: {e}")
                continue
        
        print(f"  ✓ Processed {len(logs)} logs, {len(states_updated)} state updates triggered")
        
        # Step 2: Generate recommendations và save vào MongoDB
        print(f"\n🎯 Step 2: Generating recommendations and saving to MongoDB...")
        recommendations_saved = 0
        
        for update_result in recommendations_generated:
            try:
                user_id = update_result['user_id']
                course_id = update_result['course_id']
                lesson_id = update_result['lesson_id']
                state = update_result['state']
                
                print(f"\n🔍 DEBUG: Processing update_result:")
                print(f"   - user_id: {user_id}")
                print(f"   - course_id: {course_id}")
                print(f"   - lesson_id: {lesson_id}")
                print(f"   - state: {state}")
                
                # Get recommendations với đúng time context
                print(f"   → Calling get_recommendations_for_context()...")
                recommendations = state_update_manager.get_recommendations_for_context(
                    user_id=user_id,
                    course_id=course_id,
                    lesson_id=lesson_id,
                    recommendation_service=recommendation_service
                )
                
                print(f"   ← Got recommendations: {recommendations is not None}")
                if recommendations:
                    print(f"      - time_context: {recommendations.get('time_context')}")
                    print(f"      - num_recommendations: {len(recommendations.get('recommendations', []))}")
                
                if recommendations:
                    # Save state to MongoDB
                    state_repository.save_state(
                        user_id=user_id,
                        course_id=course_id,
                        module_id=lesson_id,
                        state=state,
                        save_history=True
                    )
                    
                    # Save recommendations
                    state_repository.save_recommendations(
                        user_id=user_id,
                        module_id=lesson_id,
                        recommendations=recommendations['recommendations'],
                        state=state
                    )
                    
                    recommendations_saved += 1
                    
                    # In kết quả gợi ý
                    print(f"\n🎯 Recommendations for User {user_id}, Lesson {lesson_id}:")
                    print(f"   Time context: {recommendations.get('time_context', 'unknown')}")
                    for i, rec in enumerate(recommendations.get('recommendations', [])[:5], 1):
                        action_type = rec.get('action_type', 'N/A')
                        activity_name = rec.get('activity_name', 'N/A')
                        explanation = rec.get('explanation', 'N/A')
                        print(f"   {i}. {action_type}: {activity_name}")
                        print(f"      → {explanation}")
                    print(f"{'='*70}\n")
                
            except Exception as e:
                print(f"  ✗ Error saving recommendations: {e}")
                import traceback
                traceback.print_exc()
        
        # Step 3: Force update các contexts còn lại có logs trong buffer (nếu có)
        # Để đảm bảo không bỏ sót
        print(f"\n🔄 Step 3: Checking remaining contexts in buffer...")
        remaining_updates = state_update_manager.force_update_all_contexts()
        
        if remaining_updates:
            print(f"  ✓ Processed {len(remaining_updates)} additional contexts")
            for update_result in remaining_updates:
                try:
                    user_id = update_result['user_id']
                    course_id = update_result['course_id']
                    lesson_id = update_result['lesson_id']
                    state = update_result['state']
                    
                    recommendations = state_update_manager.get_recommendations_for_context(
                        user_id=user_id,
                        course_id=course_id,
                        lesson_id=lesson_id,
                        recommendation_service=recommendation_service
                    )
                    
                    if recommendations:
                        state_repository.save_state(
                            user_id=user_id,
                            course_id=course_id,
                            module_id=lesson_id,
                            state=state,
                            save_history=True
                        )
                        state_repository.save_recommendations(
                            user_id=user_id,
                            module_id=lesson_id,
                            recommendations=recommendations['recommendations'],
                            state=state
                        )
                        recommendations_saved += 1
                except Exception as e:
                    print(f"  ✗ Error in remaining updates: {e}")
        
        # Step 4: Save logs to MongoDB (optional, for audit)
        try:
            logs_saved = state_repository.save_log_events(logs)
            print(f"\n📝 Step 4: Saved {logs_saved} log events to MongoDB")
        except Exception as e:
            print(f"  ⚠️  Error saving logs: {e}")
        
        # Statistics
        manager_stats = state_update_manager.get_statistics()
        
        print(f"\n{'='*70}")
        print(f"✅ Background Processing Complete")
        print(f"{'='*70}")
        print(f"  - Logs received: {len(logs)}")
        print(f"  - Logs buffered: {manager_stats['logs_buffered']}")
        print(f"  - State updates: {manager_stats['state_updates']}")
        print(f"  - Q-table updates: {manager_stats['qtable_updates']}")
        print(f"  - Recommendations saved: {recommendations_saved}")
        print(f"  - Active contexts: {manager_stats['active_contexts']}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Background processing error: {e}")
        import traceback
        traceback.print_exc()


@router.post('/moodle-events', response_model=WebhookResponse)
async def receive_moodle_events(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks
):
    """Receive events from Moodle observer.php (non-blocking)"""
    if not payload.logs:
        raise HTTPException(status_code=400, detail="No logs provided")
    
    logs_dict = [log.dict() for log in payload.logs]
    
    background_tasks.add_task(
        process_events_async,
        logs=logs_dict,
        event_id=payload.event_id
    )
    
    return WebhookResponse(
        status='accepted',
        message='Events received and queued for processing',
        events_received=len(payload.logs),
        processing_started=True,
        event_id=payload.event_id
    )

