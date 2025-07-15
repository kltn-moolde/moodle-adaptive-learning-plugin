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

## Giảm từ 90,000 → còn 3,240 trạng thái.

* Rút gọn score thành 3 mức: low (score < 40), medium (40 < score < 80), high (score > 80)
* Rút gọn time_spent (phút) thành 3 mức: < 0.5; < 1.5; > 1.5
* Rút gọn attempts thành 4 mức: 0, 1, 2, >=3
* Gom object_position thành 10 nhóm, mỗi nhóm có 5 object (position chia 5 lấy phần nguyên)
