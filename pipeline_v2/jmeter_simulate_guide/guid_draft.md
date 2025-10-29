### Hướng Dẫn Làm Thủ Công Trong JMeter GUI: Xây Dựng Test Plan Đầy Đủ Để Simulate Logs Moodle

OK, nếu bạn muốn làm thủ công trong JMeter GUI (thay vì import XML), đây là cách an toàn để debug từng phần và đảm bảo khớp phân tích trước (giữ probs gốc 80% viewed, hourly peak 11-13h, over-dispersion activity, bias 3 cụm giỏi/khá/yếu, corr actions-grade qua active bias). Quy trình build từ cơ bản đến full, mất ~45-60 phút. Sau build, save .jmx và run.

**Yêu cầu trước**:
- JMeter GUI mở.
- Moodle local chạy (localhost:80, course 670 có modules assign/quiz/forum, ID module ví dụ 123 – check admin/course).
- File `users.csv` sẵn (200 users, columns username,password,group như script trước).
- Test course có users Moodle (upload CSV nếu chưa).

Hướng dẫn **step-by-step** (right-click để add, edit properties double-click). Bắt đầu với Test Plan trống.

#### Step 1: Tạo Test Plan Cơ Bản Và Thread Group (5 phút)
- **Mục tiêu**: Set scale volume (200 threads = 200 users x10 gốc).
- **Cách làm**:
  1. Mở JMeter → Right-click Test Plan (root) > Add > Threads (Users) > Thread Group.
     - Double-click Thread Group > Edit:
       - Number of Threads (users): 200.
       - Ramp-up period (seconds): 600 (10 phút tăng dần).
       - Loop Count: 1 (số actions per user từ CSV sau).
       - Save.
  2. Right-click Test Plan > Add > Config Element > HTTP Request Defaults.
     - Double-click > Edit:
       - Server Name: localhost.
       - Port Number: 80.
       - Path: /moodle.
       - Save.
  3. Right-click Test Plan > Add > Config Element > CSV Data Set Config.
     - Double-click > Edit:
       - Filename: Đường dẫn full đến users.csv (e.g., D:\...\users.csv).
       - Variable Names (comma separated): username,password,group.
       - Delimiter: ,.
       - Allow quoted data: No.
       - Recycle on EOF: Yes.
       - Stop thread on EOF: No.
       - Ignore first line: Yes.
       - Save.
  4. Right-click Test Plan > Add > Config Element > HTTP Cookie Manager.
     - Double-click > Edit: Clear cookies each iteration: No (giữ session).
       - Save (để nguyên là OK).
- **Kiểm tra**: Cây plan: Test Plan > Thread Group > HTTP Defaults > CSV Config > Cookie Manager.

#### Step 2: Thêm Login Sampler (5 phút)
- **Mục tiêu**: Mỗi user login để giữ session, tạo log 'login'.
- **Cách làm**:
  1. Right-click Thread Group > Add > Sampler > HTTP Request.
     - Double-click > Edit:
       - Name: Login.
       - Method: POST.
       - Path: /moodle/login/index.php.
       - Parameters tab: Add Parameter:
         - Name: username, Value: ${username}.
         - Name: password, Value: ${password}.
       - Advanced tab: Follow Redirects: Yes.
       - Save.
  2. Right-click Login > Add > Listener > View Results Tree (debug, remove sau full run).
- **Kiểm tra**: Run threads=1, check View Results Tree: Response 200 OK, cookies captured.

#### Step 3: Thêm Constant Throughput Timer Cho Velocity (3 phút)
- **Mục tiêu**: Giới hạn throughput 40 requests/sec để match volume ~14k/hour, bias peak hourly ngầm qua ramp.
- **Cách làm**:
  1. Right-click Thread Group > Add > Timer > Constant Throughput Timer.
     - Double-click > Edit:
       - Target throughput (requests/second): 40.
       - Calculate Throughput based on: All active threads.
       - Save.
- **Kiểm tra**: Run small, Summary Report show throughput ~40/sec.

#### Step 4: Thêm Random Controller Cho Actions Gốc (Balanced - Fallback, 10 phút)
- **Mục tiêu**: Random chọn actions theo probs gốc (80 viewed, 7 updated, 4 graded, 3 uploaded, 3 created, 2 submitted).
- **Cách làm**:
  1. Right-click Thread Group > Add > Logic Controller > Random Controller.
     - Double-click > Name: Random Action Fallback (Balanced).
  2. Add 6 child HTTP Request (right-click Random Controller > Add > Sampler > HTTP Request, edit từng cái):
     - **Viewed (80%)**: Name = View Module.
       - Method: GET.
       - Path: /moodle/mod/assign/view.php?id=123 (thay 123 bằng ID module assign thực).
       - Weight (Advanced tab): 80.
     - **Updated (7%)**: Name = Submit Update.
       - Method: POST.
       - Path: /moodle/mod/assign/submit.php.
       - Parameters: Name=assignid, Value=123; Name=submission[online], Value=test text.
       - Weight: 7.
     - **Graded (4%)**: Name = Grade Report.
       - Method: POST.
       - Path: /moodle/grade/report/user.php?userid=${userid}&id=670.
       - Weight: 4.
     - **Uploaded (3%)**: Name = File Submission.
       - Method: POST.
       - Path: /moodle/mod/assign/submission/file.php.
       - Parameters: Name=assignid, Value=123 (add file param nếu Moodle cho phép, Body Data tab).
       - Weight: 3.
     - **Created (3%)**: Name = Forum Post.
       - Method: POST.
       - Path: /moodle/mod/forum/post.php.
       - Parameters: Name=forumid, Value=456 (ID forum từ course); Name=message, Value=test post.
       - Weight: 3.
     - **Submitted (2%)**: Name = Quiz Submit.
       - Method: POST.
       - Path: /moodle/mod/quiz/processattempt.php.
       - Parameters: Name=attemptid, Value=789 (ID quiz).
       - Weight: 2.
  3. Right-click Random Controller > Add > Timer > Constant Timer.
     - Delay: ${__Random(2000,5000,)} (2-5s giữa actions).
- **Kiểm tra**: Run threads=5, Aggregate Report show % viewed ~80%.

#### Step 5: Thêm 3 If Controllers Cho Bias Cụm (20 phút)
- **Mục tiêu**: Bias theo group từ CSV (giỏi: active +20% updated/graded; khá: balanced = fallback; yếu: passive +10% viewed).
- **Cách làm**:
  1. Right-click Thread Group > Add > Logic Controller > If Controller (lặp 3 lần cho 3 cụm).
     - **If Giỏi**: Double-click > Condition: ${group} equals "giỏi".
       - Right-click If Giỏi > Add > Logic Controller > Random Controller (Name = Random Action Giỏi).
         - Add 6 child HTTP Request giống Step 4, nhưng adjust weights: Viewed=70, Updated=27, Graded=10, Uploaded=5, Created=5, Submitted=3 (normalize tổng 120 để bias active).
         - Add Constant Timer child: Delay = ${__Random(1000,3000,)} (nhanh hơn, active).
  2. **If Khá**: Condition: ${group} equals "khá".
       - Right-click If Khá > Add > Logic Controller > Random Controller (Name = Random Action Khá).
         - Duplicate 6 samplers từ Fallback, weights gốc (80/7/4/3/3/2).
         - Constant Timer: 2000-5000s (balanced).
  3. **If Yếu**: Condition: ${group} equals "yếu".
       - Right-click If Yếu > Add > Logic Controller > Random Controller (Name = Random Action Yếu).
         - 6 samplers, weights bias: Viewed=90, Updated=2, Graded=2, Uploaded=2, Created=2, Submitted=2 (passive).
         - Constant Timer: ${__Random(5000,10000,)} (chậm, low engagement).
- **Order**: Login > Constant Throughput > If Giỏi > If Khá > If Yếu > Random Fallback (nếu group null).
- **Kiểm tra**: Run threads=10, Aggregate Report filter by sampler name (e.g., Submit Update Giỏi % cao hơn).

#### Step 6: Thêm Listeners Và Save/Run (5 phút)
- **Mục tiêu**: Monitor và extract results.
- **Cách làm**:
  1. Right-click Test Plan > Add > Listener > Summary Report (aggregate throughput/errors).
  2. Right-click Test Plan > Add > Listener > Aggregate Report (per sampler count/%).
  3. Right-click Thread Group > Add > Listener > View Results Tree (debug, check response).
  4. File > Save > moodle_simulate_manual.jmx.
  5. Test: Threads=10, Run (green play). Check Aggregate: Viewed ~80%, no errors >1%.
  6. Full: Threads=200, Ramp=600s, Run non-GUI: `jmeter -n -t moodle_simulate_manual.jmx -l results.jtl`.
- **Kiểm tra**: results.jtl CSV (open Excel), count requests per sampler ~ probs.

#### Lưu Ý Debug Và Tối Ưu
- **Lỗi phổ biến**: Path ID=123 sai → Check Moodle course (admin > course > ID module). Login fail → Add Parameter 'logintoken' nếu Moodle 3.9+ (check source login.php).
- **Bias grades**: Add JSR223 Sampler end-If (right-click If > Add > Sampler > JSR223 Sampler, Script Groovy: POST Moodle API update grade=9 for giỏi).
- **Volume**: Nếu logs <140k, tăng Loop Count=2 hoặc add Loop Controller child Thread Group.
- **Extract sau run**: Query DB như trước, validate probs/corr.

Build từng step, test sau Step 3 (Random), rồi 5 (If). Nếu stuck (e.g., If not trigger), share screenshot cây plan! 😊