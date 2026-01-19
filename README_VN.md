# 🎓 Adaptive STEM Learning Pathway Optimization

<div align="center">

**Tối ưu hóa lộ trình học tập STEM thích nghi thông qua Học tăng cường (Reinforcement Learning)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Moodle](https://img.shields.io/badge/Moodle-LTI%201.3-orange.svg)](https://docs.moodle.org/dev/LTI)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

[English](README.md) | **Tiếng Việt**

</div>

---

## 👥 Thông tin dự án

**Tác giả:**  Nguyễn Hữu Lộc, Văn Tuấn Kiệt

**Giảng viên hướng dẫn:** TS. Đỗ Như Tài

**Đơn vị:** Khoa Công nghệ Thông tin - Trường Đại học Sài Gòn

---

## 📝 Tóm tắt (Abstract)

Trong bối cảnh giáo dục 4.0, các hệ thống quản lý học tập (LMS) truyền thống thường áp dụng một lộ trình học tập đồng nhất cho tất cả người học, dẫn đến sự thiếu hiệu quả trong cá nhân hóa. Dự án này đề xuất một **khung học tập thích nghi** dựa trên thuật toán **Q-learning**, tích hợp vào nền tảng **Moodle** qua tiêu chuẩn **LTI 1.3**. 

Quá trình học tập được mô hình hóa thành một **Quá trình quyết định Markov (MDP)**, kết hợp phân cụm hành vi **K-means** để xây dựng không gian trạng thái đa chiều. Thực nghiệm với 500 đợt mô phỏng cho thấy hệ thống cải thiện **22.5%** điểm số trung bình và giảm đến **51.0%** các kỹ năng yếu của người học.

**Từ khóa:** `Reinforcement Learning` • `Q-learning` • `Personalized Learning` • `STEM Education` • `Moodle LMS` • `Adaptive Learning`

## 📌 Mục lục

- [👥 Thông tin dự án](#-thông-tin-dự-án)
- [📝 Tóm tắt](#-tóm-tắt-abstract)
- [🔍 Giới thiệu](#-giới-thiệu)
- [🛠 Phương pháp đề xuất](#-phương-pháp-đề-xuất)
- [📊 Kết quả thực nghiệm](#-kết-quả-thực-nghiệm)
- [🏗️ Kiến trúc hệ thống](#️-kiến-trúc-hệ-thống)
- [💻 Cài đặt](#-cài-đặt)
- [📚 Tài liệu tham khảo](#-tài-liệu-tham-khảo)
- [📄 Giấy phép](#-giấy-phép)
- [🤝 Đóng góp](#-đóng-góp)
- [📞 Liên hệ](#-liên-hệ)

---

## 🔍 Giới thiệu

Giáo dục STEM đối mặt với thách thức lớn do sự **khác biệt đáng kể** về năng lực, kiến thức nền tảng và tốc độ học tập giữa các sinh viên. Các hệ thống quản lý học tập (LMS) như Moodle thường chỉ hoạt động như kho lưu trữ tài liệu và ghi nhận điểm số, **thiếu khả năng phân tích hành vi** và can thiệp sư phạm kịp thời.

Dự án này đề xuất một **khung học tập thích nghi** dựa trên **Reinforcement Learning (Q-learning)** - cho phép Agent AI tự động khám phá và tối ưu hóa chiến lược giảng dạy thông qua cơ chế thử-và-học (trial-and-error), liên tục điều chỉnh dựa trên phản hồi từ người học.

---

## 🛠 Phương pháp đề xuất

Hệ thống mô hình hóa quá trình học tập thành **Markov Decision Process (MDP)** với ba thành phần: không gian trạng thái đa chiều (6 đặc trưng), không gian hành động (15 hành động sư phạm), và hàm phần thưởng đa mục tiêu.

![Tổng quan phương pháp đề xuất](image.png)

### 📈 Chi tiết phương pháp đề xuất

![Chi tiết phương pháp đề xuất](image-1.png)

### 🔬 Các thành phần kỹ thuật chính

#### 1️⃣ Không gian trạng thái (State Space - S)

Bao gồm **6 chiều** đặc trưng người học:

| Chiều | Mô tả | Giá trị |
|-------|-------|---------|
| **Cluster** | Cụm hành vi (K-means) | 0-4 |
| **Module** | Đơn vị học tập hiện tại | 1-N |
| **Progress** | Tiến độ hoàn thành | 0.0-1.0 |
| **Score Level** | Mức điểm số | 0-4 |
| **Phase** | Giai đoạn học (Quiz/Forum/Assignment) | 0-2 |
| **Engagement** | Mức độ tương tác | 0-4 |

#### 2️⃣ Không gian hành động (Action Space - A)

**15 hành động sư phạm** chia theo trục thời gian:

- **Quá khứ (Remedial):** Ôn tập các Learning Outcomes (LO) yếu
- **Hiện tại (Standard):** Học nội dung theo lộ trình chuẩn
- **Tương lai (Advanced):** Học trước nội dung nâng cao

#### 3️⃣ Hàm phần thưởng (Reward Function - R)

$$R_{total} = R_{base} + R_{LO} + R_{bonus} - P_{penalty}$$

Trong đó:
- $R_{base}$: Phần thưởng cơ bản từ điểm số
- $R_{LO}$: Phần thưởng từ việc cải thiện các kỹ năng yếu
- $R_{bonus}$: Thưởng cho sự tham gia tích cực
- $P_{penalty}$: Phạt cho hành động không phù hợp

### 📈 Chi tiết thuật toán Q-learning

Thuật toán Q-learning sử dụng **Bellman update rule** với epsilon-greedy strategy để cân bằng exploration-exploitation:

$$Q(s,a) \leftarrow Q(s,a) + \alpha[r + \gamma \max_{a'} Q(s',a') - Q(s,a)]$$

Trong đó: $\alpha$ = learning rate (0.1), $\gamma$ = discount factor (0.95)

### 🔍 Explainable AI (XAI) - SHAP Framework

Để giải thích quyết định của Agent, hệ thống tích hợp **SHAP (SHapley Additive exPlanations)** - đo lường đóng góp của từng đặc trưng trạng thái vào quyết định hành động:

$$\phi_i(s) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F|-|S|-1)!}{|F|!}[f(S \cup \{i\}) - f(S)]$$

Điều này giúp giáo viên hiểu **tại sao** hệ thống đề xuất một hành động cụ thể cho từng sinh viên.

---

## 📊 Kết quả thực nghiệm

### ⚙️ Thiết lập thực nghiệm

- **Quy mô:** 500 episodes × 100 sinh viên ảo = **50,000 quỹ đạo** tương tác
- **Dataset:** Moodle Log & Grades - Course ID 670 (public dataset)
- **Baseline:** Param Policy (mô phỏng hành vi lịch sử)
- **Mô hình hóa học viên:** 70% Linear learners, 20% Video-first, 10% Practice-first

### 📈 Quá trình huấn luyện Q-table

![Quá trình huấn luyện Q-learning Agent](qtable_growth_states.png)

*Hình: Sự hội tụ của Q-learning qua 500 episodes*

### 📊 So sánh hiệu suất

| Metric | Param Policy (Baseline) | Q-learning (Dự án) | Cải thiện |
|--------|------------------------|-------------------|-----------|
| **Điểm số trung bình** (thang 10) | 5.82 ± 0.48 | 7.14 ± 0.82 | ⬆️ **+22.5%** |
| **Số lượng kỹ năng yếu** | 3.02 | 1.48 | ⬇️ **-51.0%** |
| **Phần thưởng trung bình** | 59.95 ± 12.38 | 264.26 ± 27.33 | ⬆️ **+340.8%** |

> 💡 **Kết luận:** Q-learning vượt trội so với Param Policy trên tất cả chỉ số, chứng minh khả năng tối ưu hóa lộ trình học tập cá nhân hóa.

### 🔍 Phân tích giải thích (Explainability)

![Phân tích SHAP - Feature Importance](shap_summary_bar.png)

*Hình: SHAP values cho thấy **Cluster** và **Score Level** là hai đặc trưng quan trọng nhất trong việc quyết định hành động của Agent.*

---

## 🏗️ Kiến trúc hệ thống

### 📦 Các microservices chính

![Kiến trúc hệ thống](system_design.png)

```
moodle-adaptive-learning-plugin/
├── user-segmentation-service/   # Phân cụm hành vi sinh viên (K-means)
├── course-service/              # Quản lý khóa học và nội dung
├── user-service/                # Quản lý thông tin người dùng
├── question-service/            # Quản lý ngân hàng câu hỏi
├── recommend-service/           # Gợi ý nội dung học tập (Q-learning Agent)
├── lti-service-python/          # LTI 1.3 Authentication & Integration
├── FE-service-v3/               # Frontend React + TypeScript
└── kong-gateway/                # API Gateway & Load Balancer
```

---

## 💻 Cài đặt

### 📋 Yêu cầu hệ thống

- **Docker & Docker Compose:** 20.10+
- **Moodle:** 4.5+ với LTI 1.3 enabled

### 🚀 Triển khai với Docker

```bash
# Clone repository
git clone https://github.com/kltn-moolde/moodle-adaptive-learning-plugin.git
cd moodle-adaptive-learning-plugin

# Khởi chạy toàn bộ hệ thống
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --pull always --build
```

Hệ thống sẽ tự động:
- ✅ Build tất cả microservices
- ✅ Khởi tạo database
- ✅ Cấu hình API Gateway (Kong)
- ✅ Deploy frontend React app

---

## 📚 Tài liệu tham khảo

[1] M. T. Chi and R. Wylie, "The ICAP framework: Linking cognitive engagement to active learning outcomes," *Educational Psychologist*, 2014.

[2] R. S. Sutton and A. G. Barto, *Reinforcement learning: An introduction*, MIT Press, 1998.

[3] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," *Advances in Neural Information Processing Systems*, 2017.

[4] IMS Global Learning Consortium, "LTI 1.3 Core Specification," 2019. [Online]. Available: https://www.imsglobal.org/spec/lti/v1p3/

[5] Moodle Documentation, "LTI and Moodle," 2023. [Online]. Available: https://docs.moodle.org/

---

## 📄 Giấy phép

Dự án này được cấp phép theo **Giấy phép MIT** - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp cho dự án! 

### 🔧 Cách đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### 📝 Coding Standards

- Python: Tuân thủ PEP 8
- JavaScript/TypeScript: Sử dụng ESLint + Prettier
- Commit messages: Conventional Commits format

---

## 📞 Liên hệ

**Nhóm nghiên cứu:**
- 📧 Email: [lockbkbang@gmail.com](mailto:lockbkbang@gmail.com)
- 📱 GitHub Issues: [Report bugs](https://github.com/kltn-moolde/moodle-adaptive-learning-plugin/issues)

---

## 🙏 Lời cảm ơn

Dự án này được thực hiện với sự hỗ trợ của:
- Khoa Công nghệ Thông tin - Trường Đại học Sài Gòn
- TS. Đỗ Như Tài (Giảng viên hướng dẫn)

---

<div align="center">

**⭐ Nếu dự án này hữu ích, hãy cho chúng tôi một star! ⭐**

Made with ❤️ by Adaptive Learning Team

</div>
