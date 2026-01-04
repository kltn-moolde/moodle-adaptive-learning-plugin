import { useState, useEffect } from "react";
import { motion } from "motion/react";
import {
  Users,
  TrendingUp,
  Award,
  Clock,
  CheckCircle2,
  Lightbulb,
  Network,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Alert, AlertDescription } from "../ui/alert";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import { getClusteringOverview, getClusteringResults } from "../../services/moodleApi";
import { getLtiParams } from "../../utils/ltiParams";
import type {
  ClusteringOverview,
  ClusteringResults,
  ClusterDetail,
  ClusterDistribution,
} from "../../types/clustering";
import { CLUSTER_COLORS, getClusterColor } from "../../types/clustering";

// Mock data for fallback
const mockOverview: ClusteringOverview = {
  course_id: 2,
  run_timestamp: "2026-01-04T09:21:39.511000",
  overview: {
    overall_metrics: {
      total_students: 106,
      total_logs: 11162,
      features_analyzed: 16,
      optimal_clusters: 6,
      clustering_quality: {
        silhouette_score: 0.37224461447550616,
        davies_bouldin_index: 0.686410803348026,
      },
    },
    cluster_distribution: [
      {
        cluster_id: 0,
        cluster_name: "Học sinh hoạt động buổi tối tích cực",
        student_count: 23,
        percentage: 21.69811320754717,
      },
      {
        cluster_id: 1,
        cluster_name: "Học sinh siêu tích cực (Super-Engager)",
        student_count: 1,
        percentage: 0.9433962264150944,
      },
      {
        cluster_id: 2,
        cluster_name: "Học sinh thụ động/Trung bình",
        student_count: 54,
        percentage: 50.943396226415096,
      },
      {
        cluster_id: 3,
        cluster_name: "Học sinh chuyên sâu về bài kiểm tra",
        student_count: 1,
        percentage: 0.9433962264150944,
      },
      {
        cluster_id: 4,
        cluster_name: "Học sinh khám phá cấu trúc sớm",
        student_count: 21,
        percentage: 19.81132075471698,
      },
      {
        cluster_id: 5,
        cluster_name: "Học sinh định hướng kết quả và đánh giá",
        student_count: 6,
        percentage: 5.660377358490567,
      },
    ],
    cluster_summaries: [
      {
        cluster_id: 0,
        name: "Học sinh hoạt động buổi tối tích cực",
        description:
          "Nhóm học sinh này có mức độ hoạt động tổng thể cao hơn mức trung bình, đặc biệt là vào buổi tối. Họ duy trì sự tương tác thường xuyên với hệ thống nhưng các hoạt động cụ thể như xem phần học hay nộp bài kiểm tra lại ở mức tương tự các nhóm khác.",
        student_count: 23,
        key_characteristics: [
          "Có xu hướng học tập và hoạt động trên hệ thống vào buổi tối nhiều hơn đáng kể.",
          "Thực hiện nhiều sự kiện và tương tác trên hệ thống mỗi ngày so với mức trung bình.",
          "Mức độ xem các phần nội dung khóa học và báo cáo tiến độ cá nhân tương đương với học sinh trung bình.",
        ],
      },
      {
        cluster_id: 1,
        name: "Học sinh siêu tích cực (Super-Engager)",
        description:
          "Đây là một học sinh cực kỳ tích cực và năng động trên hệ thống, thể hiện mức độ tương tác và hoàn thành công việc vượt trội so với tất cả các học sinh khác. Học sinh này là một ngoại lệ về mức độ tham gia và cống hiến.",
        student_count: 1,
        key_characteristics: [
          "Có mức độ xem nội dung tổng thể cực kỳ cao.",
          "Duy trì hoạt động liên tục và tích cực trên hệ thống trong một số ngày rất lớn.",
          "Tương tác rất nhiều với các nội dung đa phương tiện và tương tác (H5P).",
        ],
      },
      {
        cluster_id: 2,
        name: "Học sinh thụ động/Trung bình",
        description:
          "Đây là nhóm học sinh lớn nhất, có mức độ tương tác tổng thể thấp hơn hoặc tương đương với mức trung bình. Đặc biệt, họ ít khi xem các phần khóa học chi tiết hoặc theo dõi báo cáo tiến độ cá nhân, cho thấy sự thụ động trong việc tự quản lý học tập.",
        student_count: 54,
        key_characteristics: [
          "Ít xem các phần/mục chi tiết của khóa học so với các nhóm khác.",
          "Hầu như không xem báo cáo tiến độ cá nhân của mình.",
          "Hoạt động vào buổi tối và số sự kiện trung bình mỗi ngày tương đương hoặc hơi thấp hơn mức chung.",
        ],
      },
      {
        cluster_id: 3,
        name: "Học sinh chuyên sâu về bài kiểm tra",
        description:
          "Đây là một học sinh duy nhất có sự tập trung và tương tác cực kỳ cao với các hoạt động kiểm tra, từ việc xem, làm cho đến xem lại kết quả và tóm tắt bài làm. Họ dành nhiều thời gian để phân tích và đánh giá các bài kiểm tra.",
        student_count: 1,
        key_characteristics: [
          "Xem tóm tắt bài kiểm tra và các bài kiểm tra nói chung với tần suất cực kỳ cao.",
          "Tích cực xem lại các bài kiểm tra sau khi nộp để đánh giá và rút kinh nghiệm.",
          "Thực hiện nhiều hành động tự động lưu, có thể liên quan đến quá trình làm bài hoặc chỉnh sửa nội dung.",
        ],
      },
      {
        cluster_id: 4,
        name: "Học sinh khám phá cấu trúc sớm",
        description:
          "Nhóm học sinh này có xu hướng khám phá và xem các phần nội dung của khóa học một cách có hệ thống nhưng lại ít tương tác với các nội dung đa phương tiện và ít hoạt động vào buổi tối. Họ có vẻ thích tìm hiểu cấu trúc hơn là tương tác sâu.",
        student_count: 21,
        key_characteristics: [
          "Thường xuyên xem và khám phá các phần/mục của khóa học để nắm bắt cấu trúc.",
          "Ít tương tác với các module nội dung tương tác như H5P.",
          "Có mức độ hoạt động vào buổi tối thấp hơn đáng kể so với trung bình.",
        ],
      },
      {
        cluster_id: 5,
        name: "Học sinh định hướng kết quả và đánh giá",
        description:
          "Nhóm học sinh này thể hiện sự tập trung cao độ vào việc hoàn thành các bài kiểm tra, theo dõi sát sao tiến độ học tập và thường xuyên hoạt động vào buổi tối. Họ có xu hướng chủ động kiểm tra và đánh giá kết quả của mình.",
        student_count: 6,
        key_characteristics: [
          "Nộp các bài kiểm tra với tần suất cao hơn đáng kể so với mức trung bình.",
          "Thường xuyên xem báo cáo tiến độ cá nhân để theo dõi hiệu suất học tập.",
          "Có xu hướng xem lại các bài kiểm tra đã làm để rút kinh nghiệm.",
        ],
      },
    ],
  },
};

const mockResults: ClusteringResults = {
  _id: "695a312332b3a16580a46522",
  course_id: 2,
  run_timestamp: "2026-01-04T09:21:39.511000",
  optimal_k: 6,
  clusters: [
    {
      cluster_id: 0,
      user_ids: [14, 16, 17, 18, 19, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 33, 34, 36, 38, 39, 40, 42, 43],
      size: 23,
      percentage: 21.69811320754717,
      name: "Học sinh hoạt động buổi tối tích cực",
      description:
        "Nhóm học sinh này có mức độ hoạt động tổng thể cao hơn mức trung bình, đặc biệt là vào buổi tối.",
      characteristics: [
        "Có xu hướng học tập và hoạt động trên hệ thống vào buổi tối nhiều hơn đáng kể.",
        "Thực hiện nhiều sự kiện và tương tác trên hệ thống mỗi ngày so với mức trung bình.",
        "Mức độ xem các phần nội dung khóa học và báo cáo tiến độ cá nhân tương đương với học sinh trung bình.",
      ],
      recommendations: [
        "Cung cấp thêm tài liệu hoặc hoạt động ngoại khóa phù hợp với khung giờ buổi tối.",
        "Khuyến khích họ tham gia các diễn đàn thảo luận hoặc hoạt động nhóm để tận dụng sự tích cực chung.",
      ],
      statistics: {
        feature_means: {
          evening_activity: 0.352,
          avg_events_per_day: 0.58,
          section_viewed: 0.325,
          total_days_active: 0.42,
          action_viewed: 0.61,
          course_module_completion: 0.38,
          hvp_viewed: 0.29,
          url_module_viewed: 0.54,
          forum_discussion_viewed: 0.33,
          forum_user_report_viewed: 0.22,
          page_viewed: 0.47,
          system_course_viewed: 0.51,
          quiz_summary_viewed: 0.36,
          quiz_view_all: 0.28,
          workshop_assessment_evaluated: 0.19,
          attempt_reviewed: 0.31,
        },
        feature_stds: {
          evening_activity: 0.12,
          avg_events_per_day: 0.145,
          section_viewed: 0.14,
          total_days_active: 0.09,
          action_viewed: 0.15,
          course_module_completion: 0.11,
          hvp_viewed: 0.08,
          url_module_viewed: 0.13,
          forum_discussion_viewed: 0.10,
          forum_user_report_viewed: 0.07,
          page_viewed: 0.12,
          system_course_viewed: 0.14,
          quiz_summary_viewed: 0.10,
          quiz_view_all: 0.08,
          workshop_assessment_evaluated: 0.06,
          attempt_reviewed: 0.09,
        },
        top_features: [
          { feature: "evening_activity", value: 0.352, interpretation: "higher" },
          { feature: "avg_events_per_day", value: 0.58, interpretation: "higher" },
          { feature: "section_viewed", value: 0.325, interpretation: "similar" },
          { feature: "total_days_active", value: 0.42, interpretation: "similar" },
          { feature: "action_viewed", value: 0.61, interpretation: "higher" },
          { feature: "course_module_completion", value: 0.38, interpretation: "similar" },
          { feature: "hvp_viewed", value: 0.29, interpretation: "lower" },
          { feature: "url_module_viewed", value: 0.54, interpretation: "higher" },
          { feature: "forum_discussion_viewed", value: 0.33, interpretation: "similar" },
          { feature: "forum_user_report_viewed", value: 0.22, interpretation: "lower" },
          { feature: "page_viewed", value: 0.47, interpretation: "similar" },
          { feature: "system_course_viewed", value: 0.51, interpretation: "higher" },
          { feature: "quiz_summary_viewed", value: 0.36, interpretation: "similar" },
          { feature: "quiz_view_all", value: 0.28, interpretation: "lower" },
          { feature: "workshop_assessment_evaluated", value: 0.19, interpretation: "lower" },
          { feature: "attempt_reviewed", value: 0.31, interpretation: "similar" },
        ],
      },
    },
    {
      cluster_id: 1,
      user_ids: [2],
      size: 1,
      percentage: 0.9433962264150944,
      name: "Học sinh siêu tích cực (Super-Engager)",
      description: "Đây là một học sinh cực kỳ tích cực và năng động trên hệ thống.",
      characteristics: [
        "Có mức độ xem nội dung tổng thể cực kỳ cao.",
        "Duy trì hoạt động liên tục và tích cực trên hệ thống trong một số ngày rất lớn.",
      ],
      recommendations: [
        "Cung cấp các cơ hội học tập nâng cao hoặc mở rộng kiến thức để giữ vững động lực.",
        "Khuyến khích trở thành người hướng dẫn hoặc hỗ trợ các bạn khác trong các hoạt động học tập.",
      ],
      statistics: {
        feature_means: {
          action_viewed: 1.0,
          course_module_completion: 1.0,
          hvp_viewed: 1.0,
          section_viewed: 0.861,
          evening_activity: 0.89,
          avg_events_per_day: 0.95,
          total_days_active: 0.88,
          url_module_viewed: 0.92,
          forum_discussion_viewed: 0.85,
          forum_user_report_viewed: 0.78,
          page_viewed: 0.91,
          system_course_viewed: 0.87,
          quiz_summary_viewed: 0.84,
          quiz_view_all: 0.82,
          workshop_assessment_evaluated: 0.76,
          attempt_reviewed: 0.89,
        },
        feature_stds: {
          action_viewed: 0,
          course_module_completion: 0,
          hvp_viewed: 0,
          section_viewed: 0,
          evening_activity: 0.02,
          avg_events_per_day: 0.01,
          total_days_active: 0.02,
          url_module_viewed: 0.01,
          forum_discussion_viewed: 0.02,
          forum_user_report_viewed: 0.01,
          page_viewed: 0.01,
          system_course_viewed: 0.02,
          quiz_summary_viewed: 0.01,
          quiz_view_all: 0.01,
          workshop_assessment_evaluated: 0.01,
          attempt_reviewed: 0.02,
        },
        top_features: [
          { feature: "action_viewed", value: 1.0, interpretation: "higher" },
          { feature: "course_module_completion", value: 1.0, interpretation: "higher" },
          { feature: "hvp_viewed", value: 1.0, interpretation: "higher" },
          { feature: "section_viewed", value: 0.861, interpretation: "higher" },
          { feature: "evening_activity", value: 0.89, interpretation: "higher" },
          { feature: "avg_events_per_day", value: 0.95, interpretation: "higher" },
          { feature: "total_days_active", value: 0.88, interpretation: "higher" },
          { feature: "url_module_viewed", value: 0.92, interpretation: "higher" },
          { feature: "forum_discussion_viewed", value: 0.85, interpretation: "higher" },
          { feature: "forum_user_report_viewed", value: 0.78, interpretation: "higher" },
          { feature: "page_viewed", value: 0.91, interpretation: "higher" },
          { feature: "system_course_viewed", value: 0.87, interpretation: "higher" },
          { feature: "quiz_summary_viewed", value: 0.84, interpretation: "higher" },
          { feature: "quiz_view_all", value: 0.82, interpretation: "higher" },
          { feature: "workshop_assessment_evaluated", value: 0.76, interpretation: "higher" },
          { feature: "attempt_reviewed", value: 0.89, interpretation: "higher" },
        ],
      },
    },
    {
      cluster_id: 2,
      user_ids: [6, 8, 11, 13, 15, 20, 26, 32, 35, 37, 41, 45, 46, 47, 48, 49, 50, 53, 54, 56, 57, 58, 61, 62, 65, 67, 68, 69, 71, 72, 74, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 91, 92, 93, 96, 98, 99, 100, 101, 103, 104, 105],
      size: 54,
      percentage: 50.943396226415096,
      name: "Học sinh thụ động/Trung bình",
      description: "Đây là nhóm học sinh lớn nhất, có mức độ tương tác tổng thể thấp hơn.",
      characteristics: [
        "Ít xem các phần/mục chi tiết của khóa học so với các nhóm khác.",
        "Hầu như không xem báo cáo tiến độ cá nhân của mình.",
      ],
      recommendations: [
        "Tăng cường các thông báo và nhắc nhở về tiến độ học tập và các mốc quan trọng.",
        "Thiết kế các hoạt động yêu cầu tương tác bắt buộc hơn với nội dung khóa học để thúc đẩy tham gia.",
      ],
      statistics: {
        feature_means: {
          evening_activity: 0.037,
          section_viewed: 0.077,
          avg_events_per_day: 0.095,
          total_days_active: 0.12,
          action_viewed: 0.18,
          course_module_completion: 0.09,
          hvp_viewed: 0.05,
          url_module_viewed: 0.14,
          forum_discussion_viewed: 0.08,
          forum_user_report_viewed: 0.03,
          page_viewed: 0.11,
          system_course_viewed: 0.13,
          quiz_summary_viewed: 0.07,
          quiz_view_all: 0.04,
          workshop_assessment_evaluated: 0.02,
          attempt_reviewed: 0.06,
        },
        feature_stds: {
          evening_activity: 0.078,
          section_viewed: 0.043,
          avg_events_per_day: 0.069,
          total_days_active: 0.05,
          action_viewed: 0.06,
          course_module_completion: 0.04,
          hvp_viewed: 0.02,
          url_module_viewed: 0.05,
          forum_discussion_viewed: 0.03,
          forum_user_report_viewed: 0.01,
          page_viewed: 0.04,
          system_course_viewed: 0.05,
          quiz_summary_viewed: 0.03,
          quiz_view_all: 0.02,
          workshop_assessment_evaluated: 0.01,
          attempt_reviewed: 0.02,
        },
        top_features: [
          { feature: "section_viewed", value: 0.077, interpretation: "lower" },
          { feature: "evening_activity", value: 0.037, interpretation: "lower" },
          { feature: "avg_events_per_day", value: 0.095, interpretation: "lower" },
          { feature: "total_days_active", value: 0.12, interpretation: "lower" },
          { feature: "action_viewed", value: 0.18, interpretation: "lower" },
          { feature: "course_module_completion", value: 0.09, interpretation: "lower" },
          { feature: "hvp_viewed", value: 0.05, interpretation: "lower" },
          { feature: "url_module_viewed", value: 0.14, interpretation: "lower" },
          { feature: "forum_discussion_viewed", value: 0.08, interpretation: "lower" },
          { feature: "forum_user_report_viewed", value: 0.03, interpretation: "lower" },
          { feature: "page_viewed", value: 0.11, interpretation: "lower" },
          { feature: "system_course_viewed", value: 0.13, interpretation: "lower" },
          { feature: "quiz_summary_viewed", value: 0.07, interpretation: "lower" },
          { feature: "quiz_view_all", value: 0.04, interpretation: "lower" },
          { feature: "workshop_assessment_evaluated", value: 0.02, interpretation: "lower" },
          { feature: "attempt_reviewed", value: 0.06, interpretation: "lower" },
        ],
      },
    },
    {
      cluster_id: 3,
      user_ids: [3],
      size: 1,
      percentage: 0.9433962264150944,
      name: "Học sinh chuyên sâu về bài kiểm tra",
      description: "Đây là một học sinh duy nhất có sự tập trung cực kỳ cao với các hoạt động kiểm tra.",
      characteristics: [
        "Xem tóm tắt bài kiểm tra và các bài kiểm tra nói chung với tần suất cực kỳ cao.",
        "Tích cực xem lại các bài kiểm tra sau khi nộp để đánh giá và rút kinh nghiệm.",
      ],
      recommendations: [
        "Cung cấp thêm các bài kiểm tra thực hành hoặc câu hỏi nâng cao để thử thách và duy trì động lực.",
      ],
      statistics: {
        feature_means: {
          attempt_summary_viewed: 0.429,
          attempt_reviewed: 0.476,
          action_ended: 1.0,
          evening_activity: 1.0,
          avg_events_per_day: 0.72,
          section_viewed: 0.65,
          total_days_active: 0.58,
          action_viewed: 0.71,
          course_module_completion: 0.54,
          hvp_viewed: 0.43,
          url_module_viewed: 0.68,
          forum_discussion_viewed: 0.52,
          forum_user_report_viewed: 0.38,
          page_viewed: 0.63,
          system_course_viewed: 0.67,
          quiz_summary_viewed: 0.76,
        },
        feature_stds: {
          attempt_summary_viewed: 0,
          attempt_reviewed: 0,
          action_ended: 0,
          evening_activity: 0,
          avg_events_per_day: 0.08,
          section_viewed: 0.09,
          total_days_active: 0.07,
          action_viewed: 0.08,
          course_module_completion: 0.06,
          hvp_viewed: 0.05,
          url_module_viewed: 0.07,
          forum_discussion_viewed: 0.06,
          forum_user_report_viewed: 0.04,
          page_viewed: 0.07,
          system_course_viewed: 0.08,
          quiz_summary_viewed: 0.09,
        },
        top_features: [
          { feature: "attempt_summary_viewed", value: 0.429, interpretation: "higher" },
          { feature: "evening_activity", value: 1.0, interpretation: "higher" },
          { feature: "action_ended", value: 1.0, interpretation: "higher" },
          { feature: "attempt_reviewed", value: 0.476, interpretation: "higher" },
          { feature: "avg_events_per_day", value: 0.72, interpretation: "higher" },
          { feature: "section_viewed", value: 0.65, interpretation: "similar" },
          { feature: "total_days_active", value: 0.58, interpretation: "similar" },
          { feature: "action_viewed", value: 0.71, interpretation: "higher" },
          { feature: "course_module_completion", value: 0.54, interpretation: "similar" },
          { feature: "hvp_viewed", value: 0.43, interpretation: "similar" },
          { feature: "url_module_viewed", value: 0.68, interpretation: "higher" },
          { feature: "forum_discussion_viewed", value: 0.52, interpretation: "similar" },
          { feature: "forum_user_report_viewed", value: 0.38, interpretation: "lower" },
          { feature: "page_viewed", value: 0.63, interpretation: "similar" },
          { feature: "system_course_viewed", value: 0.67, interpretation: "higher" },
          { feature: "quiz_summary_viewed", value: 0.76, interpretation: "higher" },
        ],
      },
    },
    {
      cluster_id: 4,
      user_ids: [44, 51, 52, 55, 59, 60, 63, 64, 66, 70, 73, 75, 76, 77, 78, 89, 90, 94, 95, 97, 102],
      size: 21,
      percentage: 19.81132075471698,
      name: "Học sinh khám phá cấu trúc sớm",
      description: "Nhóm học sinh này có xu hướng khám phá và xem các phần nội dung của khóa học một cách có hệ thống.",
      characteristics: [
        "Thường xuyên xem và khám phá các phần/mục của khóa học để nắm bắt cấu trúc.",
        "Ít tương tác với các module nội dung tương tác như H5P.",
      ],
      recommendations: [
        "Tích hợp các yếu tố tương tác (như H5P) vào các phần cấu trúc để khuyến khích sự tham gia sâu hơn.",
      ],
      statistics: {
        feature_means: {
          section_viewed: 0.651,
          hvp_viewed: 0.0,
          evening_activity: 0.0,
          avg_events_per_day: 0.45,
          total_days_active: 0.38,
          action_viewed: 0.52,
          course_module_completion: 0.31,
          url_module_viewed: 0.48,
          forum_discussion_viewed: 0.27,
          forum_user_report_viewed: 0.15,
          page_viewed: 0.42,
          system_course_viewed: 0.46,
          quiz_summary_viewed: 0.29,
          quiz_view_all: 0.18,
          workshop_assessment_evaluated: 0.11,
          attempt_reviewed: 0.24,
        },
        feature_stds: {
          section_viewed: 0.193,
          hvp_viewed: 0.0,
          evening_activity: 0.0,
          avg_events_per_day: 0.09,
          total_days_active: 0.07,
          action_viewed: 0.10,
          course_module_completion: 0.06,
          url_module_viewed: 0.09,
          forum_discussion_viewed: 0.05,
          forum_user_report_viewed: 0.03,
          page_viewed: 0.08,
          system_course_viewed: 0.09,
          quiz_summary_viewed: 0.06,
          quiz_view_all: 0.04,
          workshop_assessment_evaluated: 0.02,
          attempt_reviewed: 0.05,
        },
        top_features: [
          { feature: "section_viewed", value: 0.651, interpretation: "higher" },
          { feature: "hvp_viewed", value: 0.0, interpretation: "lower" },
          { feature: "evening_activity", value: 0.0, interpretation: "lower" },
          { feature: "avg_events_per_day", value: 0.45, interpretation: "similar" },
          { feature: "total_days_active", value: 0.38, interpretation: "similar" },
          { feature: "action_viewed", value: 0.52, interpretation: "similar" },
          { feature: "course_module_completion", value: 0.31, interpretation: "lower" },
          { feature: "url_module_viewed", value: 0.48, interpretation: "similar" },
          { feature: "forum_discussion_viewed", value: 0.27, interpretation: "lower" },
          { feature: "forum_user_report_viewed", value: 0.15, interpretation: "lower" },
          { feature: "page_viewed", value: 0.42, interpretation: "similar" },
          { feature: "system_course_viewed", value: 0.46, interpretation: "similar" },
          { feature: "quiz_summary_viewed", value: 0.29, interpretation: "lower" },
          { feature: "quiz_view_all", value: 0.18, interpretation: "lower" },
          { feature: "workshop_assessment_evaluated", value: 0.11, interpretation: "lower" },
          { feature: "attempt_reviewed", value: 0.24, interpretation: "lower" },
        ],
      },
    },
    {
      cluster_id: 5,
      user_ids: [5, 7, 9, 10, 12, 206],
      size: 6,
      percentage: 5.660377358490567,
      name: "Học sinh định hướng kết quả và đánh giá",
      description: "Nhóm học sinh này thể hiện sự tập trung cao độ vào việc hoàn thành các bài kiểm tra.",
      characteristics: [
        "Nộp các bài kiểm tra với tần suất cao hơn đáng kể so với mức trung bình.",
        "Thường xuyên xem báo cáo tiến độ cá nhân để theo dõi hiệu suất học tập.",
      ],
      recommendations: [
        "Cung cấp phản hồi chi tiết và kịp thời cho các bài kiểm tra để hỗ trợ việc học tập.",
      ],
      statistics: {
        feature_means: {
          attempt_submitted: 0.667,
          course_user_report_viewed: 0.692,
          evening_activity: 0.397,
          avg_events_per_day: 0.58,
          section_viewed: 0.51,
          total_days_active: 0.49,
          action_viewed: 0.62,
          course_module_completion: 0.44,
          hvp_viewed: 0.33,
          url_module_viewed: 0.56,
          forum_discussion_viewed: 0.41,
          forum_user_report_viewed: 0.28,
          page_viewed: 0.53,
          system_course_viewed: 0.57,
          quiz_summary_viewed: 0.46,
        },
        feature_stds: {
          attempt_submitted: 0.236,
          course_user_report_viewed: 0.294,
          evening_activity: 0.197,
          avg_events_per_day: 0.11,
          section_viewed: 0.09,
          total_days_active: 0.08,
          action_viewed: 0.12,
          course_module_completion: 0.09,
          hvp_viewed: 0.06,
          url_module_viewed: 0.10,
          forum_discussion_viewed: 0.07,
          forum_user_report_viewed: 0.05,
          page_viewed: 0.10,
          system_course_viewed: 0.11,
          quiz_summary_viewed: 0.09,
        },
        top_features: [
          { feature: "course_user_report_viewed", value: 0.692, interpretation: "higher" },
          { feature: "attempt_submitted", value: 0.667, interpretation: "higher" },
          { feature: "action_viewed", value: 0.62, interpretation: "higher" },
          { feature: "avg_events_per_day", value: 0.58, interpretation: "similar" },
          { feature: "system_course_viewed", value: 0.57, interpretation: "similar" },
          { feature: "url_module_viewed", value: 0.56, interpretation: "similar" },
          { feature: "page_viewed", value: 0.53, interpretation: "similar" },
          { feature: "section_viewed", value: 0.51, interpretation: "similar" },
          { feature: "total_days_active", value: 0.49, interpretation: "similar" },
          { feature: "quiz_summary_viewed", value: 0.46, interpretation: "similar" },
          { feature: "course_module_completion", value: 0.44, interpretation: "similar" },
          { feature: "forum_discussion_viewed", value: 0.41, interpretation: "similar" },
          { feature: "evening_activity", value: 0.397, interpretation: "similar" },
          { feature: "hvp_viewed", value: 0.33, interpretation: "lower" },
          { feature: "forum_user_report_viewed", value: 0.28, interpretation: "lower" },
        ],
      },
    },
  ],
  features_used: [
    "evening_activity",
    "avg_events_per_day",
    "section_viewed",
    "action_viewed",
    "course_module_completion",
  ],
  metadata: {
    total_students: 106,
    total_logs: 11162,
    features_extracted: 118,
    features_selected: 16,
    execution_time_seconds: 28.497091,
    clustering_metrics: {
      inertia: 8.861924374234572,
      silhouette: 0.37224461447550616,
      davies_bouldin: 0.686410803348026,
    },
  },
};

export default function ClusterAnalysis() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overview, setOverview] = useState<ClusteringOverview>(mockOverview);
  const [results, setResults] = useState<ClusteringResults>(mockResults);
  const [selectedCluster, setSelectedCluster] = useState<ClusterDetail | null>(null);
  const [sortBy, setSortBy] = useState<"size" | "percentage" | "id">("size");

  useEffect(() => {
    async function fetchClusteringData() {
      try {
        setLoading(true);
        setError(null);

        // Get course ID from LTI params or use default
        const ltiParams = getLtiParams();
        const courseId = ltiParams?.courseId || 2;

        // Fetch both overview and detailed results
        const [overviewData, resultsData] = await Promise.all([
          getClusteringOverview(courseId),
          getClusteringResults(courseId),
        ]);

        if (overviewData) {
          setOverview(overviewData);
        }

        if (resultsData) {
          setResults(resultsData);
        }

        if (!overviewData && !resultsData) {
          setError("Không thể tải dữ liệu phân tích cụm. Hiển thị dữ liệu mẫu.");
        }
      } catch (err) {
        console.error("Error fetching clustering data:", err);
        setError("Đã xảy ra lỗi khi tải dữ liệu. Hiển thị dữ liệu mẫu.");
      } finally {
        setLoading(false);
      }
    }

    fetchClusteringData();
  }, []);

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Sort clusters
  const sortedClusters = [...overview.overview.cluster_distribution].sort((a, b) => {
    if (sortBy === "size") return b.student_count - a.student_count;
    if (sortBy === "percentage") return b.percentage - a.percentage;
    return a.cluster_id - b.cluster_id;
  });

  // Get cluster detail from results
  const getClusterDetail = (clusterId: number): ClusterDetail | undefined => {
    return results.clusters.find((c) => c.cluster_id === clusterId);
  };

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center gap-3">
          <Network className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Phân Tích Cụm Học Sinh</h1>
            <p className="text-muted-foreground">Đang tải dữ liệu phân tích...</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 rounded-2xl bg-gray-200 dark:bg-gray-800 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6 p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-primary/10 p-3">
            <Network className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Phân Tích Cụm Học Sinh</h1>
            <p className="text-muted-foreground">
              Phân tích hành vi học tập bằng AI • Cập nhật: {formatTimestamp(overview.run_timestamp)}
            </p>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-yellow-400 bg-yellow-50 dark:bg-yellow-950">
          <AlertCircle className="h-5 w-5 text-yellow-600" />
          <AlertDescription className="text-yellow-800 dark:text-yellow-200">{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="rounded-2xl border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tổng Học Sinh</CardTitle>
              <div className="rounded-lg bg-blue-100 p-2 dark:bg-blue-900">
                <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{overview.overview.overall_metrics.total_students}</div>
              <p className="text-xs text-muted-foreground">
                {overview.overview.overall_metrics.total_logs.toLocaleString()} hoạt động ghi nhận
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="rounded-2xl border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Số Cụm Tối Ưu</CardTitle>
              <div className="rounded-lg bg-green-100 p-2 dark:bg-green-900">
                <Network className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{overview.overview.overall_metrics.optimal_clusters}</div>
              <p className="text-xs text-muted-foreground">
                {overview.overview.overall_metrics.features_analyzed} đặc trưng được phân tích
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="rounded-2xl border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Chất Lượng Phân Cụm</CardTitle>
              <div className="rounded-lg bg-purple-100 p-2 dark:bg-purple-900">
                <Award className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {(overview.overview.overall_metrics.clustering_quality.silhouette_score * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">Silhouette Score (càng cao càng tốt)</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card className="rounded-2xl border-0 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Thời Gian Phân Tích</CardTitle>
              <div className="rounded-lg bg-amber-100 p-2 dark:bg-amber-900">
                <Clock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{results.metadata.execution_time_seconds.toFixed(1)}s</div>
              <p className="text-xs text-muted-foreground">Thời gian xử lý dữ liệu</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pie Chart - Distribution */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card className="rounded-2xl border-0 shadow-lg">
            <CardHeader>
              <CardTitle>Phân Bố Cụm Học Sinh</CardTitle>
              <CardDescription>Tỷ lệ học sinh trong từng cụm</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={overview.overview.cluster_distribution}
                    dataKey="percentage"
                    nameKey="cluster_name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    label={(entry) => `${entry.percentage.toFixed(1)}%`}
                  >
                    {overview.overview.cluster_distribution.map((entry) => (
                      <Cell key={`cell-${entry.cluster_id}`} fill={getClusterColor(entry.cluster_id)} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => `${value.toFixed(2)}%`}
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Bar Chart - Student Count */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card className="rounded-2xl border-0 shadow-lg">
            <CardHeader>
              <CardTitle>Số Lượng Học Sinh Theo Cụm</CardTitle>
              <CardDescription>
                <div className="flex items-center gap-2">
                  <span>Sắp xếp theo:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as "size" | "percentage" | "id")}
                    className="rounded-md border bg-background px-2 py-1 text-sm"
                  >
                    <option value="size">Số lượng</option>
                    <option value="percentage">Tỷ lệ</option>
                    <option value="id">ID cụm</option>
                  </select>
                </div>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={450}>
                <BarChart 
                  data={sortedClusters} 
                  layout="vertical" 
                  margin={{ left: 50, right: 30, top: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis 
                    type="number" 
                    stroke="#64748B"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    type="category"
                    dataKey="cluster_name"
                    stroke="#64748B"
                    width={220}
                    tick={{ fontSize: 11 }}
                    interval={0}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Bar dataKey="student_count" radius={[0, 8, 8, 0]}>
                    {sortedClusters.map((entry) => (
                      <Cell key={`bar-${entry.cluster_id}`} fill={getClusterColor(entry.cluster_id)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Cluster Cards Grid */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Chi Tiết Các Cụm</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {overview.overview.cluster_summaries.map((summary, index) => (
            <motion.div
              key={summary.cluster_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
            >
              <Card
                className="rounded-2xl border-0 shadow-lg cursor-pointer transition-all hover:scale-[1.02] hover:shadow-xl"
                onClick={() => setSelectedCluster(getClusterDetail(summary.cluster_id) || null)}
                style={{ borderLeft: `4px solid ${getClusterColor(summary.cluster_id)}` }}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <Badge
                      className="rounded-full px-3 py-1"
                      style={{
                        backgroundColor: `${getClusterColor(summary.cluster_id)}20`,
                        color: getClusterColor(summary.cluster_id),
                      }}
                    >
                      Cụm {summary.cluster_id}
                    </Badge>
                    <div className="text-right">
                      <div className="text-2xl font-bold">{summary.student_count}</div>
                      <div className="text-xs text-muted-foreground">
                        {((summary.student_count / overview.overview.overall_metrics.total_students) * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <CardTitle className="mt-3 text-lg">{summary.name}</CardTitle>
                  <CardDescription className="line-clamp-2">{summary.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {summary.key_characteristics.slice(0, 2).map((char, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-muted-foreground line-clamp-2">{char}</span>
                      </div>
                    ))}
                  </div>
                  <Button variant="outline" className="w-full mt-4" size="sm">
                    Xem chi tiết
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Cluster Detail Dialog */}
      <Dialog open={!!selectedCluster} onOpenChange={() => setSelectedCluster(null)}>
        <DialogContent className="w-[70vw] max-w-[1400px] max-h-[90vh] overflow-y-auto rounded-2xl" style={{ translate: "none", maxWidth: "none" }}>
          {selectedCluster && (
            <>
              <DialogHeader>
                <div className="flex items-start gap-3">
                  <Badge
                    className="rounded-full px-3 py-1"
                    style={{
                      backgroundColor: `${getClusterColor(selectedCluster.cluster_id)}20`,
                      color: getClusterColor(selectedCluster.cluster_id),
                    }}
                  >
                    Cụm {selectedCluster.cluster_id}
                  </Badge>
                  <div className="flex-1">
                    <DialogTitle className="text-2xl">{selectedCluster.name}</DialogTitle>
                    <DialogDescription className="mt-2">{selectedCluster.description}</DialogDescription>
                  </div>
                </div>
              </DialogHeader>

              <div className="space-y-6 mt-4">
                {/* Statistics Cards */}
                <div className="grid gap-4 md:grid-cols-2">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium">Số Lượng</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">{selectedCluster.size}</div>
                      <p className="text-xs text-muted-foreground">học sinh trong cụm</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-medium">Tỷ Lệ</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">{selectedCluster.percentage.toFixed(2)}%</div>
                      <p className="text-xs text-muted-foreground">của tổng số học sinh</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Characteristics */}
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    Đặc Điểm Chính
                  </h3>
                  <div className="space-y-2">
                    {selectedCluster.characteristics.map((char, idx) => (
                      <div key={idx} className="flex items-start gap-2 p-3 rounded-lg bg-muted/50">
                        <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{char}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-yellow-500" />
                    Khuyến Nghị
                  </h3>
                  <div className="space-y-2">
                    {selectedCluster.recommendations.map((rec, idx) => (
                      <div key={idx} className="flex items-start gap-2 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-950/30">
                        <Lightbulb className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Feature Analysis Radar Chart */}
                {selectedCluster.statistics.top_features.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-3">Phân Tích Đặc Trưng</h3>
                    <Card>
                      <CardContent className="pt-6">
                        <ResponsiveContainer width="100%" height={300}>
                          <RadarChart
                            data={selectedCluster.statistics.top_features.map((f) => ({
                              feature: f.feature.replace(/_/g, " ").slice(0, 20),
                              value: f.value,
                            }))}
                          >
                            <PolarGrid />
                            <PolarAngleAxis dataKey="feature" tick={{ fontSize: 11 }} />
                            <PolarRadiusAxis angle={90} domain={[0, 1]} />
                            <Radar
                              name="Giá trị"
                              dataKey="value"
                              stroke={getClusterColor(selectedCluster.cluster_id)}
                              fill={getClusterColor(selectedCluster.cluster_id)}
                              fillOpacity={0.6}
                            />
                            <Tooltip />
                          </RadarChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {/* Student IDs */}
                <div>
                  <h3 className="font-semibold mb-3">
                    Danh Sách Học Sinh ({selectedCluster.user_ids.length})
                  </h3>
                  <div className="flex flex-wrap gap-2 p-4 rounded-lg bg-muted/30 max-h-32 overflow-y-auto">
                    {selectedCluster.user_ids.map((userId) => (
                      <Badge key={userId} variant="secondary" className="rounded-full">
                        ID: {userId}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
