# learning_path_optimizer.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import requests
import json
import os
from config import Config
import config
from q_learning import call_moodle_api, safe_get, get_user_cluster, discretize_score, discretize_complete_rate

class LearningPathOptimizer:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        
    def prepare_training_data(self):
        """
        Chuẩn bị dữ liệu training từ lịch sử học tập
        Kết hợp dữ liệu từ user_clusters và Q-table
        """
        try:
            # Load user clusters data
            if isinstance(Config.USER_CLUSTERS_CSV, str) and Config.USER_CLUSTERS_CSV.startswith('http'):
                user_df = pd.read_csv(Config.USER_CLUSTERS_CSV)
            else:
                user_df = pd.read_csv(Config.USER_CLUSTERS_CSV)
            
            # Load Q-table nếu có
            if os.path.exists(Config.DEFAULT_QTABLE_PATH):
                qtable_df = pd.read_csv(Config.DEFAULT_QTABLE_PATH)
                # Lọc những entry có q_value khác 0 (đã được học)
                qtable_df = qtable_df[qtable_df['q_value'] != 0]
            else:
                qtable_df = pd.DataFrame()
            
            training_data = []
            
            # Tạo synthetic training data từ user profiles
            for _, user_row in user_df.iterrows():
                user_id = user_row['userid']
                cluster = user_row['cluster']
                
                # Lấy dữ liệu từ các section
                for section_id in config.section_ids[:5]:  # Giới hạn 5 section đầu
                    for complete_rate in Config.COMPLETE_RATE_BINS:
                        for score_bin in Config.SCORE_AVG_BINS:
                            # Tạo features cho mỗi combination
                            features = {
                                'user_id': user_id,
                                'section_id': section_id,
                                'cluster': cluster,
                                'current_complete_rate': complete_rate,
                                'current_score': score_bin,
                                'difficulty_preference': self._get_difficulty_preference(cluster),
                            }
                            
                            # Tính target performance dựa trên cluster và current state
                            target_performance = self._calculate_target_performance(
                                cluster, complete_rate, score_bin, section_id
                            )
                            
                            features['target_performance'] = target_performance
                            training_data.append(features)
            
            return pd.DataFrame(training_data)
            
        except Exception as e:
            print(f"❌ Error preparing training data: {e}")
            return pd.DataFrame()
    
    def _get_difficulty_preference(self, cluster):
        """Xác định preference độ khó dựa trên cluster"""
        if cluster == 0:  # Yếu
            return 0.3  # Thích độ khó thấp
        elif cluster == 1:  # Trung bình
            return 0.6  # Thích độ khó trung bình
        else:  # Giỏi
            return 0.9  # Thích độ khó cao
    
    def _calculate_target_performance(self, cluster, complete_rate, score_bin, section_id):
        """Tính toán hiệu suất mục tiêu dựa trên các yếu tố"""
        base_performance = 0.5
        
        # Cluster bonus
        if cluster == 0:
            base_performance += 0.1
        elif cluster == 1:
            base_performance += 0.3
        else:
            base_performance += 0.4
            
        # Complete rate bonus
        base_performance += complete_rate * 0.2
        
        # Score bonus
        base_performance += (score_bin / 10) * 0.3
        
        # Section difficulty (giả sử section_id cao hơn = khó hơn)
        section_difficulty = min(section_id / max(config.section_ids), 1.0)
        base_performance -= section_difficulty * 0.1
        
        return min(max(base_performance, 0.0), 1.0)
    
    def train_model(self):
        """Train Linear Regression model"""
        print("🔄 Preparing training data...")
        df = self.prepare_training_data()
        
        if df.empty:
            print("❌ No training data available")
            return False
        
        print(f"📊 Training data shape: {df.shape}")
        
        # Prepare features
        feature_columns = ['section_id', 'cluster', 'current_complete_rate', 
                          'current_score', 'difficulty_preference']
        
        X = df[feature_columns].copy()
        y = df['target_performance']
        
        # Encode categorical features if needed
        for col in ['cluster']:
            if col in X.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                X[col] = self.label_encoders[col].fit_transform(X[col])
        
        # Scale features - Sử dụng feature names
        self.scaler.feature_names_in_ = feature_columns  # Set feature names
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Model trained successfully!")
        print(f"📈 MSE: {mse:.4f}, R²: {r2:.4f}")
        
        self.is_trained = True
        return True
    
    def predict_performance(self, user_id, section_id, complete_rate, score_bin):
        """Dự đoán hiệu suất học tập cho một section cụ thể"""
        if not self.is_trained:
            print("⚠️ Model chưa được train. Training now...")
            if not self.train_model():
                return 0.5  # Default performance
        
        try:
            cluster = get_user_cluster(user_id) or 1
            difficulty_pref = self._get_difficulty_preference(cluster)
            
            # Prepare features as DataFrame to maintain feature names
            feature_names = ['section_id', 'cluster', 'current_complete_rate', 'current_score', 'difficulty_preference']
            features_df = pd.DataFrame([[
                section_id,
                cluster,
                complete_rate,
                score_bin,
                difficulty_pref
            ]], columns=feature_names)
            
            # Encode categorical if needed
            if 'cluster' in self.label_encoders:
                try:
                    features_df['cluster'] = self.label_encoders['cluster'].transform(features_df['cluster'])
                except ValueError:
                    # Handle unseen categories
                    pass
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Predict
            performance = self.model.predict(features_scaled)[0]
            return max(0.0, min(1.0, performance))  # Clamp between 0 and 1
            
        except Exception as e:
            print(f"❌ Error predicting performance: {e}")
            return 0.5
    
    def generate_learning_path(self, user_id, course_id, max_sections=10, include_completed=False, optimization_goal='performance'):
        """
        Tạo lộ trình học tối ưu cho user với Linear Regression
        
        Args:
            user_id: ID của user
            course_id: ID của course
            max_sections: Số section tối đa
            include_completed: Có bao gồm section đã hoàn thành không
            optimization_goal: Mục tiêu tối ưu ('performance', 'speed', 'comprehensive')
        """
        if not config.section_ids:
            return []
        
        try:
            # Lấy trạng thái hiện tại của user
            current_progress = self._get_user_current_progress(user_id, course_id)
            
            # Lấy cluster của user
            cluster = get_user_cluster(user_id) or 1
            
            learning_path = []
            available_sections = config.section_ids[:max_sections]
            
            print(f"🎯 Generating learning path for user {user_id} (cluster: {cluster}, goal: {optimization_goal})")
            
            for section_id in available_sections:
                # Lấy trạng thái hiện tại của section này
                section_progress = current_progress.get(section_id, {
                    'complete_rate': 0.0,
                    'avg_score': 0.0,
                    'completed': False
                })
                
                # Skip section đã hoàn thành nếu không yêu cầu include
                if section_progress['completed'] and not include_completed:
                    continue
                
                # Dự đoán performance cho các action khác nhau
                current_complete = discretize_complete_rate(section_progress['complete_rate'])
                current_score = discretize_score(section_progress['avg_score'])
                
                best_actions = []
                
                # Test các action khả dụng
                for action in Config.ACTIONS:
                    # Simulate trạng thái sau khi thực hiện action
                    simulated_complete, simulated_score = self._simulate_action_result(
                        action, current_complete, current_score, cluster
                    )
                    
                    # Dự đoán performance với Linear Regression
                    predicted_performance = self.predict_performance(
                        user_id, section_id, simulated_complete, simulated_score
                    )
                    
                    # Đảm bảo predicted_performance không phải None
                    if predicted_performance is None:
                        predicted_performance = 0.5
                    
                    # Tính toán điểm action dựa trên optimization goal
                    action_score = self._calculate_action_score(
                        action, predicted_performance, optimization_goal, cluster
                    )
                    
                    # Đảm bảo action_score không phải None
                    if action_score is None:
                        action_score = 0.5
                    
                    best_actions.append({
                        'action': action,
                        'predicted_performance': round(predicted_performance, 4),
                        'action_score': round(action_score, 4),
                        'expected_complete_rate': simulated_complete,
                        'expected_score': simulated_score,
                        'estimated_time_minutes': self._estimate_action_time(action, cluster),
                        'difficulty_level': self._get_action_difficulty(action)
                    })
                
                # Sắp xếp theo action_score (tùy thuộc optimization goal)
                best_actions.sort(key=lambda x: x['action_score'], reverse=True)
                
                # Lấy top 3 actions tốt nhất
                recommended_actions = best_actions[:3]
                
                # Đảm bảo có ít nhất 1 action
                if not recommended_actions:
                    recommended_actions = [{
                        'action': 'read_new_resource',
                        'predicted_performance': 0.5,
                        'action_score': 0.5,
                        'expected_complete_rate': current_complete,
                        'expected_score': current_score,
                        'estimated_time_minutes': 30,
                        'difficulty_level': 'Medium'
                    }]
                
                # Tính toán estimated time và difficulty cho section
                estimated_time = self._estimate_section_time(recommended_actions, optimization_goal)
                difficulty_level = self._assess_section_difficulty(section_progress, cluster)
                
                # Đảm bảo priority_score không phải None
                priority_score = recommended_actions[0]['action_score'] if recommended_actions[0]['action_score'] is not None else 0.5
                predicted_performance = recommended_actions[0]['predicted_performance'] if recommended_actions[0]['predicted_performance'] is not None else 0.5
                
                learning_path.append({
                    'section_id': section_id,
                    'section_name': f"Section {section_id}",  # Có thể lấy từ API nếu cần
                    'current_state': {
                        'complete_rate': round(section_progress['complete_rate'], 3),
                        'avg_score': round(section_progress['avg_score'], 2),
                        'completed': section_progress['completed']
                    },
                    'recommended_actions': recommended_actions,
                    'priority_score': priority_score,
                    'predicted_performance': predicted_performance,
                    'estimated_time_minutes': estimated_time,
                    'difficulty_level': difficulty_level,
                    'personalization_notes': self._get_personalization_notes(cluster, section_progress)
                })
            
            # Sắp xếp theo priority score và optimization goal
            if optimization_goal == 'speed':
                learning_path.sort(key=lambda x: (x['priority_score'], -x['estimated_time_minutes']), reverse=True)
            elif optimization_goal == 'comprehensive':
                learning_path.sort(key=lambda x: (x['difficulty_level'], x['priority_score']), reverse=False)
            else:  # 'performance'
                learning_path.sort(key=lambda x: x['priority_score'], reverse=True)
            
            print(f"✅ Generated learning path with {len(learning_path)} sections")
            return learning_path
            
        except Exception as e:
            print(f"❌ Error generating learning path: {e}")
            return []
    
    def _get_user_current_progress(self, user_id, course_id):
        """Lấy tiến độ hiện tại của user cho tất cả sections"""
        progress = {}
        
        for section_id in config.section_ids:
            try:
                # Lấy điểm trung bình
                avg_score_data = call_moodle_api('local_userlog_get_user_section_avg_grade', {
                    'userid': user_id, 'courseid': course_id, 'sectionid': section_id
                })
                avg_score = safe_get(avg_score_data, 'avg_section_grade', 0)
                
                # Lấy complete rate
                total_resources = safe_get(call_moodle_api('local_userlog_get_total_resources_by_section', {
                    'sectionid': section_id, 'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
                }), 'total_resources', 0)
                
                viewed_resources = safe_get(call_moodle_api('local_userlog_get_viewed_resources_distinct_by_section', {
                    'userid': user_id, 'courseid': course_id, 'sectionid': section_id,
                    'objecttypes[0]': 'resource', 'objecttypes[1]': 'hvp'
                }), 'viewed_resources', 0)
                
                complete_rate = viewed_resources / total_resources if total_resources > 0 else 0.0
                
                # Kiểm tra completion
                completion_data = call_moodle_api('local_userlog_get_section_completion', {
                    'userid': user_id, 'sectionid': section_id
                })
                completion_rate = safe_get(completion_data, 'completion_rate', 0)
                
                progress[section_id] = {
                    'complete_rate': complete_rate,
                    'avg_score': avg_score,
                    'completed': completion_rate >= 95  # 95% là hoàn thành
                }
                
            except Exception as e:
                print(f"❌ Error getting progress for section {section_id}: {e}")
                progress[section_id] = {
                    'complete_rate': 0.0,
                    'avg_score': 0.0,
                    'completed': False
                }
        
        return progress
    
    def _simulate_action_result(self, action, current_complete, current_score, cluster):
        """Simulate kết quả sau khi thực hiện một action"""
        new_complete = current_complete
        new_score = current_score
        
        # Logic simulation dựa trên action
        if action == 'read_new_resource':
            new_complete = min(current_complete + 0.3, 1.0)
            new_score = current_score + 0.5
            
        elif action == 'review_old_resource':
            new_complete = current_complete  # Không tăng complete rate
            new_score = current_score + 1.0  # Tăng score
            
        elif action == 'attempt_new_quiz' or action == 'do_quiz_same':
            if cluster == 0:  # Yếu
                new_score = current_score + 1.5
            elif cluster == 1:  # Trung bình
                new_score = current_score + 2.0
            else:  # Giỏi
                new_score = current_score + 2.5
                
        elif action == 'redo_failed_quiz':
            new_score = current_score + 2.0
            
        elif action == 'do_quiz_easier':
            new_score = current_score + 1.0
            
        elif action == 'do_quiz_harder':
            if cluster >= 1:  # Trung bình trở lên
                new_score = current_score + 3.0
            else:
                new_score = current_score + 0.5
                
        elif action == 'skip_to_next_module':
            # Không thay đổi trạng thái hiện tại
            pass
        
        # Clamp values
        new_complete = max(0.0, min(1.0, new_complete))
        new_score = max(0, min(10, new_score))
        
        # Discretize
        return discretize_complete_rate(new_complete), discretize_score(new_score)
    
    def _calculate_action_score(self, action, predicted_performance, optimization_goal, cluster):
        """Tính điểm action dựa trên mục tiêu tối ưu"""
        base_score = predicted_performance
        
        if optimization_goal == 'speed':
            # Ưu tiên các action nhanh
            speed_bonus = {
                'skip_to_next_module': 0.3,
                'attempt_new_quiz': 0.2,
                'do_quiz_same': 0.15,
                'read_new_resource': 0.1,
                'review_old_resource': 0.05,
                'redo_failed_quiz': 0.0,
                'do_quiz_easier': -0.05,
                'do_quiz_harder': -0.1
            }
            base_score += speed_bonus.get(action, 0)
            
        elif optimization_goal == 'comprehensive':
            # Ưu tiên học toàn diện
            comprehensive_bonus = {
                'review_old_resource': 0.25,
                'redo_failed_quiz': 0.2,
                'read_new_resource': 0.15,
                'do_quiz_harder': 0.1,
                'attempt_new_quiz': 0.05,
                'do_quiz_same': 0.0,
                'do_quiz_easier': -0.05,
                'skip_to_next_module': -0.3
            }
            base_score += comprehensive_bonus.get(action, 0)
        
        # Cluster-specific adjustments
        if cluster == 0:  # Beginner
            if action in ['do_quiz_easier', 'review_old_resource']:
                base_score += 0.1
            elif action in ['do_quiz_harder', 'skip_to_next_module']:
                base_score -= 0.15
        elif cluster == 2:  # Advanced
            if action in ['do_quiz_harder', 'skip_to_next_module']:
                base_score += 0.1
            elif action in ['do_quiz_easier', 'review_old_resource']:
                base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _estimate_action_time(self, action, cluster):
        """Ước tính thời gian thực hiện action (phút)"""
        base_times = {
            'read_new_resource': 20,
            'review_old_resource': 15,
            'attempt_new_quiz': 25,
            'redo_failed_quiz': 20,
            'skip_to_next_module': 5,
            'do_quiz_harder': 35,
            'do_quiz_easier': 15,
            'do_quiz_same': 25
        }
        
        base_time = base_times.get(action, 20)
        
        # Cluster adjustment
        if cluster == 0:  # Beginner cần thời gian nhiều hơn
            return int(base_time * 1.3)
        elif cluster == 2:  # Advanced nhanh hơn
            return int(base_time * 0.8)
        
        return base_time
    
    def _get_action_difficulty(self, action):
        """Đánh giá độ khó của action"""
        difficulty_map = {
            'skip_to_next_module': 'Easy',
            'do_quiz_easier': 'Easy',
            'review_old_resource': 'Easy',
            'read_new_resource': 'Medium',
            'attempt_new_quiz': 'Medium',
            'do_quiz_same': 'Medium',
            'redo_failed_quiz': 'Medium',
            'do_quiz_harder': 'Hard'
        }
        return difficulty_map.get(action, 'Medium')
    
    def _estimate_section_time(self, recommended_actions, optimization_goal):
        """Ước tính thời gian hoàn thành section"""
        if not recommended_actions:
            return 30
        
        if optimization_goal == 'speed':
            return recommended_actions[0]['estimated_time_minutes']
        elif optimization_goal == 'comprehensive':
            return sum([action['estimated_time_minutes'] for action in recommended_actions])
        else:  # performance
            return int(sum([action['estimated_time_minutes'] for action in recommended_actions[:2]]) / 2)
    
    def _assess_section_difficulty(self, section_progress, cluster):
        """Đánh giá độ khó của section"""
        complete_rate = section_progress['complete_rate']
        avg_score = section_progress['avg_score']
        
        if complete_rate > 0.8 and avg_score > 7:
            return 'Easy'
        elif complete_rate > 0.5 and avg_score > 5:
            return 'Medium'
        else:
            return 'Hard'
    
    def _get_personalization_notes(self, cluster, section_progress):
        """Tạo ghi chú cá nhân hóa"""
        notes = []
        
        if cluster == 0:
            notes.append("Focus on building solid foundations")
            if section_progress['avg_score'] < 5:
                notes.append("Consider reviewing previous materials")
        elif cluster == 1:
            notes.append("Balanced approach recommended")
            if section_progress['complete_rate'] < 0.5:
                notes.append("Complete more resources before attempting quizzes")
        else:  # cluster == 2
            notes.append("Challenge yourself with advanced content")
            if section_progress['avg_score'] > 8:
                notes.append("Ready for more challenging materials")
        
        return notes
    
    def get_study_tips(self, cluster):
        """Lấy tips học tập dựa trên cluster"""
        tips = {
            0: [
                "Take your time to understand each concept thoroughly",
                "Review materials multiple times before moving forward",
                "Start with easier quizzes to build confidence",
                "Don't hesitate to ask for help when needed"
            ],
            1: [
                "Balance between reviewing and learning new content",
                "Try different types of learning activities",
                "Set achievable daily learning goals",
                "Track your progress regularly"
            ],
            2: [
                "Challenge yourself with harder problems",
                "Look for connections between different topics",
                "Help others to reinforce your own learning",
                "Explore additional resources beyond the curriculum"
            ]
        }
        return tips.get(cluster, tips[1])
    
    def analyze_user_performance(self, user_id, course_id):
        """Phân tích hiệu suất học tập của user"""
        try:
            current_progress = self._get_user_current_progress(user_id, course_id)
            cluster = get_user_cluster(user_id) or 1
            
            # Tính toán các metrics
            completed_sections = sum([1 for p in current_progress.values() if p['completed']])
            total_sections = len(current_progress)
            avg_score = sum([p['avg_score'] for p in current_progress.values()]) / total_sections if total_sections > 0 else 0
            avg_completion = sum([p['complete_rate'] for p in current_progress.values()]) / total_sections if total_sections > 0 else 0
            
            # Dự đoán performance cho các section chưa hoàn thành
            future_predictions = []
            for section_id, progress in current_progress.items():
                if not progress['completed']:
                    pred_perf = self.predict_performance(
                        user_id, section_id, 
                        progress['complete_rate'], 
                        progress['avg_score']
                    )
                    future_predictions.append({
                        'section_id': section_id,
                        'predicted_performance': round(pred_perf, 3),
                        'current_score': progress['avg_score'],
                        'current_completion': progress['complete_rate']
                    })
            
            # Sắp xếp predictions
            future_predictions.sort(key=lambda x: x['predicted_performance'], reverse=True)
            
            return {
                'overall_progress': {
                    'completed_sections': completed_sections,
                    'total_sections': total_sections,
                    'completion_percentage': round((completed_sections / total_sections) * 100, 1) if total_sections > 0 else 0,
                    'average_score': round(avg_score, 2),
                    'average_completion_rate': round(avg_completion, 3)
                },
                'user_profile': {
                    'cluster': cluster,
                    'learning_style': {
                        0: 'Methodical and careful learner',
                        1: 'Balanced and adaptive learner', 
                        2: 'Fast-paced and challenge-seeking learner'
                    }.get(cluster, 'Unknown'),
                    'recommended_pace': {
                        0: 'Slow and steady',
                        1: 'Moderate pace',
                        2: 'Fast-paced'
                    }.get(cluster, 'Moderate')
                },
                'performance_predictions': future_predictions[:5],  # Top 5
                'recommendations': {
                    'focus_areas': self._identify_focus_areas(current_progress, cluster),
                    'study_tips': self.get_study_tips(cluster)
                }
            }
            
        except Exception as e:
            print(f"❌ Error analyzing user performance: {e}")
            return {}
    
    def _identify_focus_areas(self, current_progress, cluster):
        """Xác định các khu vực cần tập trung"""
        weak_sections = []
        strong_sections = []
        
        for section_id, progress in current_progress.items():
            if progress['avg_score'] < 5 or progress['complete_rate'] < 0.5:
                weak_sections.append(section_id)
            elif progress['avg_score'] > 8 and progress['complete_rate'] > 0.8:
                strong_sections.append(section_id)
        
        focus_areas = []
        if weak_sections:
            focus_areas.append(f"Review and strengthen understanding in sections: {weak_sections[:3]}")
        if strong_sections and cluster >= 1:
            focus_areas.append(f"Consider advanced challenges in sections: {strong_sections[:2]}")
        if not weak_sections and not strong_sections:
            focus_areas.append("Continue with current learning pace and approach")
        
        return focus_areas


# Global instance
learning_path_optimizer = LearningPathOptimizer()