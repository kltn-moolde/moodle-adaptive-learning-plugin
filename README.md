## Mục lục

### Folder: demo_V1_V2: 1 chương, chưa có bắt buộc kiến thức trước và option kiến thức sau

* V1: 1 chương, chưa có tìm số cụm trong Kmean tự động, thứ tự gợi ý LO còn lộn xộn, chưa đi tới cuối khóa
* V2: 1 chương, có tìm số cụm trong Kmean tự động

### Folder: demo_V3: 1 khoá học, thêm một số cột trong course_structure.json

* V3: 1 khoá học, tìm số cụm trong Kmean tự động, có bắt buộc kiến thức trước và option kiến thức sau
* Cấu trúc khoá học bổ sung thêm: prerequisites, optional_paths, và resources, tag
  * prerequisites: kiến thức bắt buộc phải có trước khi học
  * optional_paths: có thể chọn các LO học tiếp theo tuỳ điều kiện hiện tại
  * resources: tài nguyên bổ sung
  * tag: 1 số tag

### Folder: demo_V4: Giảm số lượng state bằng cách gom nhóm

#### Giảm từ 90,000 → còn 3,240 trạng thái.

* Rút gọn score thành 3 mức: low (score < 40), medium (40 < score < 80), high (score > 80)
* Rút gọn time_spent (phút) thành 3 mức: < 0.5; < 1.5; > 1.5
* Rút gọn attempts thành 4 mức: 0, 1, 2, >=3
* Gom object_position thành 10 nhóm, mỗi nhóm có 5 object (position chia 5 lấy phần nguyên)

### Folder: local_userlog -> plugin php create api get data from Moodle

### Folder: getDataMoodel: các hàm, api lấy data moodle

- local_userlog_v1.zip: version đầu tiên
- local_userlog_v2.zip: version thứ 2 - lấy log theo courseid và userid
- local_userlog_v3.zip: version thứ 3 - lấy log theo courseid và userid, lấy nhiều thứ khác
- local_userlog_v4.zip: version thứ 4 - bổ sung lấy log realtime
- local_userlog_v5.zip: version thứ 5 - log cho Kmean - demo V6
- local_userlog_v6.zip: version thứ 6 - log cho Qtable - demo V6

course_log_somethingelse.ipynb: lấy thông tin coure, log, nhiều thứ,...

courseOrigin.ipynb: lấy thông tin khoá học

lession.ipynb: lấy data bài học ở dạng lesson khi tạo

restructureDataCourseMoodle.ipynb: chuyển đổi json từ courseOrigin.ipynb thành dạng dễ đọc hơn

data/ : thư mục chưa data

sql/ : thư mục chứa câu lệnh sql về lấy log từ moodle

- lấy log user theo khoá học
- lấy log user theo khoá học có kèm theo tag dok
- lấy log user full yêu cầu của model đang train -> chưa hoạt động đúng (20/07/25)

#### update important: 22/07/25

* getDataMoodle/data/backup-moodle2-course-4-java-20250722-0445.mbz: file export/import khoá học
* getDataMoodle/majorTableMoodle.sql -> dòng 500, câu lệnh sql lấy log bài tập gần hoàn thiện

### Plugin Spring boot

* Auth tự động, có các API chuẩn LTI 1.3, có API get data log từ moodle
* Cần lấy token truy cập function từ moodle và gán vào application.properties
* Hướng dẫn cấu hình:
  * Tool name: User Log Viewer
  * Tool URL: http://localhost:8080/lti/launch
  * LTI version: LTI 1.3
  * Public key type: Keyset URL
  * Public keyset URL: http://localhost:8080/lti/jwks
  * Initiate login URL: http://localhost:8080/lti/login
  * Redirection URI(s): http://localhost:8080/lti/launch
  * Kích hoạt "IMS LTI Names and Role Provisioning"
  * Kích hoạt "IMS LTI Assignment and Grade Services"
  * Share launcher's name with tool: Yes
  * Share launcher's email with tool: Yes
  * Accept grades from the tool: No
  * Cập nhật file application.properties với thông tin của Moodle
    * Secret key tự tạo (512 bit)
    * Chỉnh sửa SecurityConfig cho phù hợp

### Update demo V4

* Chỉ tăng step khi thực sự được thêm recommendation
* Thêm retry logic khi gặp object đã visited
* Sửa logic Go_to_high_level và Go_to_low_level: tăng giảm chỉ trong cùng chapter, low thì chỉ giảm chapter, high thì chỉ tăng chapter
* Cải thiện fallback: Ưu tiên objects theo thứ tự tự nhiên của khóa học, Chỉ fallback khi không có action cụ thể nào thành công
* Tăng giới hạn vòng lặp để tránh trường hợp bất ngờ
* Kết quả:
  * Bước tuần tự: 1, 2, 3, 4, 5...
  * Action chính xác: Go_to_low_level thực sự chọn DOK thấp hơn, Go_to_high_level chọn DOK cao hơn
* Thêm các api flask: get user info, get recommendation, get course object

### Update demo V5

- lấy được log thực tế, gợi ý được thực tế
- tuy nhiên mọi thứ còn thủ công
- gợi ý sai
- Kmean sai, code rối, ...

### Update demo V6 !important

- lấy được log thực tế hoàn thiện cho Kmean
- Kmean đã đúng
- phát triển local_userlog v6 - phiên bản hoàn thiện cho Kmean
- code đẹp
