import React, { useState, useEffect } from 'react';
import { learningPathService, type LearningPathData } from '../services/learningPathService';
import { moodleApiService, type EnrolledUser } from '../services/moodleApiService';

interface StudentsLearningPathsProps {
  courseId: number;
}

const StudentsLearningPaths: React.FC<StudentsLearningPathsProps> = ({ courseId }) => {
  const [students, setStudents] = useState<EnrolledUser[]>([]);
  const [learningPaths, setLearningPaths] = useState<Record<number, LearningPathData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedStudent, setExpandedStudent] = useState<number | null>(null);

  useEffect(() => {
    const fetchStudentsAndPaths = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get enrolled students
        const enrolledStudents = await moodleApiService.getEnrolledUsers(courseId);
        const studentUsers = enrolledStudents.filter(user => 
          user.roles.some(role => role.shortname === 'student')
        );
        setStudents(studentUsers);

        // Get learning paths for each student
        const pathPromises = studentUsers.map(async (student) => {
          try {
            const path = await learningPathService.getLearningPath(student.id, courseId);
            return { studentId: student.id, path };
          } catch (err) {
            console.error(`Error getting learning path for student ${student.id}:`, err);
            return { studentId: student.id, path: null };
          }
        });

        const pathResults = await Promise.all(pathPromises);
        const pathsMap: Record<number, LearningPathData> = {};
        pathResults.forEach(result => {
          if (result.path) {
            pathsMap[result.studentId] = result.path;
          }
        });
        setLearningPaths(pathsMap);

      } catch (err) {
        console.error('Error fetching students and learning paths:', err);
        setError('Failed to load student learning paths. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudentsAndPaths();
  }, [courseId]);

  const getDifficultyColor = (quizLevel: string) => {
    switch (quizLevel) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('quiz')) return 'fas fa-question-circle';
    if (action.includes('video')) return 'fas fa-play-circle';
    if (action.includes('read')) return 'fas fa-book';
    if (action.includes('review')) return 'fas fa-eye';
    return 'fas fa-tasks';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        <span className="ml-2 text-gray-600">Loading student learning paths...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <i className="fas fa-exclamation-triangle text-red-500 mr-2"></i>
          <span className="text-red-700">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {students.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <i className="fas fa-users text-4xl mb-4"></i>
          <p>No students found in this course.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {students.map((student) => {
            const learningPath = learningPaths[student.id];
            const isExpanded = expandedStudent === student.id;
            
            return (
              <div key={student.id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Student Header */}
                <div 
                  className="p-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => setExpandedStudent(isExpanded ? null : student.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-sm">
                          {student.firstname.charAt(0)}{student.lastname.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <div className="font-semibold text-gray-800">{student.fullname}</div>
                        <div className="text-sm text-gray-600">{student.email}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      {learningPath && (
                        <>
                          <div className="text-sm text-gray-600">
                            Progress: {learningPath.progress}%
                          </div>
                          {learningPath.next_action && (
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(learningPath.next_action.source_state.quiz_level)}`}>
                                {learningPath.next_action.source_state.quiz_level}
                              </span>
                              <span className="text-sm text-primary-600 font-medium">
                                Q: {learningPath.next_action.q_value.toFixed(2)}
                              </span>
                            </div>
                          )}
                        </>
                      )}
                      <i className={`fas ${isExpanded ? 'fa-chevron-up' : 'fa-chevron-down'} text-gray-400`}></i>
                    </div>
                  </div>
                </div>

                {/* Learning Path Details */}
                {isExpanded && learningPath && (
                  <div className="p-4 border-t border-gray-200">
                    {/* Current Recommended Action */}
                    {learningPath.next_action && (
                      <div className="bg-blue-50 rounded-lg p-4 mb-4">
                        <h4 className="font-semibold text-blue-800 mb-2 flex items-center">
                          <i className="fas fa-lightbulb mr-2"></i>
                          Recommended Action
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Action:</span>
                            <div className="font-medium text-blue-700">
                              {learningPath.next_action.suggested_action.replace(/_/g, ' ')}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Lesson:</span>
                            <div className="font-medium">
                              {learningPath.next_action.source_state.lesson_name || 'N/A'}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Section:</span>
                            <div className="font-medium">
                              {learningPath.next_action.source_state.section_id}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Learning Steps */}
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3">Learning Path</h4>
                      <div className="space-y-2">
                        {learningPath.steps.map((step, index) => (
                          <div 
                            key={index} 
                            className={`flex items-center space-x-3 p-3 rounded-lg ${
                              step.current 
                                ? 'bg-primary-50 border border-primary-200' 
                                : step.completed 
                                  ? 'bg-green-50 border border-green-200'
                                  : 'bg-gray-50 border border-gray-200'
                            }`}
                          >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                              step.completed 
                                ? 'bg-green-500 text-white' 
                                : step.current 
                                  ? 'bg-primary-500 text-white'
                                  : 'bg-gray-300 text-gray-600'
                            }`}>
                              {step.completed ? (
                                <i className="fas fa-check text-xs"></i>
                              ) : step.current ? (
                                <i className="fas fa-play text-xs"></i>
                              ) : (
                                <span className="text-xs">{index + 1}</span>
                              )}
                            </div>
                            
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <i className={`${getActionIcon(step.action)} text-gray-500`}></i>
                                <span className="font-medium text-gray-800">{step.title}</span>
                                {step.current && learningPath.next_action && (
                                  <span className="text-xs text-primary-600 font-medium">
                                    (Q: {learningPath.next_action.q_value.toFixed(2)})
                                  </span>
                                )}
                              </div>
                              <div className="text-sm text-gray-600">{step.description}</div>
                            </div>
                            
                            <div className="text-right">
                              <div className="text-xs text-gray-500">
                                {step.completed ? 'Completed' : step.current ? 'Current' : 'Pending'}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* No Learning Path Available */}
                {isExpanded && !learningPath && (
                  <div className="p-4 border-t border-gray-200 text-center text-gray-500">
                    <i className="fas fa-exclamation-circle mb-2"></i>
                    <p>Learning path not available for this student.</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default StudentsLearningPaths;