# Cluster Profiling with LLM

## Giới thiệu

Module `ClusterProfiler` sử dụng LLM (Large Language Model) để tự động phân tích và mô tả đặc điểm của từng cluster một cách tự nhiên và dễ hiểu.

## Tính năng

1. **Tính toán Statistics**: Phân tích đặc điểm statistical của mỗi cluster
2. **So sánh với Overall**: Tính z-score để xác định features nổi bật
3. **AI-powered Description**: Sử dụng LLM để generate mô tả bằng tiếng Việt
4. **Actionable Insights**: Đề xuất hành động cụ thể cho từng nhóm học sinh

## Cài đặt

### 1. Install dependencies

```bash
# Cho Gemini (Google)
pip install google-generativeai

# Hoặc cho OpenAI
pip install openai
```

### 2. Lấy API Key

**Gemini (Khuyên dùng - Free tier):**
1. Truy cập: https://makersuite.google.com/app/apikey
2. Tạo API key mới
3. Export biến môi trường:

```bash
export GOOGLE_API_KEY="your-gemini-api-key-here"
# Hoặc
export GEMINI_API_KEY="your-gemini-api-key-here"
```

**OpenAI (Có phí):**
1. Truy cập: https://platform.openai.com/api-keys
2. Tạo API key mới
3. Export biến môi trường:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Lưu API key vĩnh viễn (Optional)

Thêm vào file `~/.zshrc` hoặc `~/.bashrc`:

```bash
echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Sử dụng

### Trong Pipeline chính

```python
# Chạy pipeline với LLM profiling (mặc định: Gemini)
python main.py

# Hoặc tắt LLM profiling
python main.py --no-llm-profiling
```

### Sử dụng trực tiếp

```python
from core import ClusterProfiler
import pandas as pd

# Load data với cluster labels
df = pd.read_csv('outputs/gmm_generation/real_students_with_clusters.csv')

# Initialize profiler
profiler = ClusterProfiler(llm_provider='gemini')  # hoặc 'openai'

# Profile tất cả clusters
profiles = profiler.profile_all_clusters(df, cluster_col='cluster')

# Lưu kết quả
profiler.save_profiles('outputs/cluster_profiling')
```

### Với API key trực tiếp

```python
profiler = ClusterProfiler(
    llm_provider='gemini',
    api_key='your-api-key-here'
)
```

## Output

Kết quả được lưu trong `outputs/cluster_profiling/`:

### 1. `cluster_profiles.json`

```json
{
  "cluster_stats": {
    "0": {
      "cluster_id": 0,
      "n_students": 15,
      "percentage": 35.7,
      "ai_profile": {
        "name": "Học sinh xuất sắc",
        "description": "Nhóm học sinh có thành tích học tập rất tốt...",
        "strengths": [
          "Tham gia học tập tích cực",
          "Hoàn thành bài tập đầy đủ"
        ],
        "weaknesses": [
          "Có thể thiếu thách thức"
        ],
        "recommendations": [
          "Tạo challenges nâng cao",
          "Khuyến khích làm mentor",
          "Cung cấp tài liệu nâng cao"
        ]
      },
      "top_distinguishing_features": [...]
    }
  }
}
```

### 2. `cluster_profiles_report.txt`

Báo cáo dễ đọc với format đẹp:

```
================================================================================
CLUSTER 0: Học sinh xuất sắc
================================================================================

📊 Thống kê:
  • Số lượng: 15 học sinh (35.7%)

📝 Mô tả:
  Nhóm học sinh có thành tích học tập rất tốt, tích cực tham gia các hoạt động...

💪 Điểm mạnh:
  • Tham gia học tập tích cực
  • Hoàn thành bài tập đầy đủ

⚠️ Điểm yếu:
  • Có thể thiếu thách thức

💡 Đề xuất hành động:
  1. Tạo challenges nâng cao
  2. Khuyến khích làm mentor
  3. Cung cấp tài liệu nâng cao

🔍 Top 5 đặc điểm nổi bật:
  • module_count: much higher (z-score: 2.34)
  • mean_module_grade: higher (z-score: 1.87)
  ...
```

## Cấu hình trong config.py

Thêm vào `config.py`:

```python
# Cluster Profiling Settings
ENABLE_LLM_PROFILING = True  # Bật/tắt LLM profiling
LLM_PROVIDER = 'gemini'      # 'gemini' hoặc 'openai'
LLM_API_KEY = None           # None = đọc từ env variable
```

## Xử lý lỗi

### Không có API key

```
ValueError: Gemini API key not found. Set GOOGLE_API_KEY environment variable.
```

**Giải pháp**: Export API key như hướng dẫn ở trên

### LLM không available

Pipeline vẫn chạy được nhưng sẽ sử dụng mô tả cơ bản thay vì AI-powered:

```
⚠ LLM not available. Will generate basic profiles without AI descriptions.
```

### Rate limit

Nếu gặp rate limit, thêm delay giữa các requests:

```python
import time
for cluster_id in clusters:
    profile = profiler.generate_llm_description(cluster_id)
    time.sleep(1)  # Delay 1 giây
```

## So sánh LLM Providers

| Feature | Gemini | OpenAI |
|---------|--------|--------|
| **Cost** | Free (với limits) | Có phí (~$0.002/1K tokens) |
| **Speed** | Nhanh | Nhanh |
| **Quality** | Rất tốt | Xuất sắc |
| **Vietnamese** | Tốt | Rất tốt |
| **Setup** | Dễ | Dễ |

**Khuyến nghị**: Dùng Gemini cho development/testing, OpenAI cho production nếu cần chất lượng cao nhất.

## Example Output

Ví dụ profile cho một cluster:

**Input**: Cluster với 8 học sinh (34.8%), có các đặc điểm:
- `module_count`: lower (z-score: -0.89)
- `mean_module_grade`: much lower (z-score: -1.67)
- `viewed`: lower (z-score: -1.23)

**AI Output**:
```
Tên: Học sinh cần hỗ trợ khẩn cấp

Mô tả: Nhóm học sinh đang gặp khó khăn nghiêm trọng trong học tập, 
với điểm số thấp và mức độ tương tác với khóa học rất hạn chế.

Điểm mạnh:
- Đã xác định được nhóm cần can thiệp
- Còn thời gian để cải thiện

Điểm yếu:
- Điểm số thấp hơn đáng kể so với trung bình
- Ít tương tác với tài liệu học tập
- Có nguy cơ bỏ học cao

Đề xuất:
1. Liên hệ cá nhân với từng học sinh để hiểu nguyên nhân
2. Tổ chức buổi học bổ trợ, ôn tập kiến thức cơ bản
3. Ghép đôi với mentor từ nhóm học sinh giỏi
4. Theo dõi sát sao tiến độ hàng tuần
```

## Troubleshooting

**Q: Kết quả không chính xác?**
- A: Thử điều chỉnh prompt trong `cluster_profiler.py`, method `generate_llm_description()`

**Q: Muốn customize format output?**
- A: Sửa prompt để thay đổi JSON schema, hoặc post-process kết quả

**Q: Chi phí sử dụng OpenAI?**
- A: ~$0.002/1K tokens, với 6 clusters mỗi lần chạy ~$0.01-0.02

## Tích hợp vào workflow

```python
# 1. Chạy pipeline đầy đủ
python main.py

# 2. Xem kết quả profiling
cat outputs/cluster_profiling/cluster_profiles_report.txt

# 3. Sử dụng insights để:
#    - Phân nhóm học sinh
#    - Thiết kế interventions
#    - Personalize learning paths
#    - Report cho giáo viên
```

## Best Practices

1. **Chạy profiling sau mỗi lần cluster mới**: Đảm bảo insights luôn up-to-date
2. **Review AI output**: LLM có thể sai, cần human validation
3. **Combine với domain knowledge**: Kết hợp insights từ LLM với kinh nghiệm giáo dục
4. **Track changes over time**: So sánh profiles qua các kỳ học
5. **Use for communication**: Dùng mô tả tự nhiên để báo cáo cho stakeholders

## Advanced Usage

### Custom prompt template

```python
profiler = ClusterProfiler(llm_provider='gemini')

# Override generate_llm_description với custom prompt
def custom_prompt(cluster_data):
    return f"""
    Phân tích cluster với focus vào learning outcomes:
    {json.dumps(cluster_data, indent=2)}
    """

profiler.generate_llm_description = custom_prompt
```

### Batch processing

```python
# Process multiple cohorts
for cohort_id in ['2023', '2024', '2025']:
    df = load_cohort_data(cohort_id)
    profiler.profile_all_clusters(df)
    profiler.save_profiles(f'outputs/cohort_{cohort_id}')
```
