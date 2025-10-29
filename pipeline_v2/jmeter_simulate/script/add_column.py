import csv

input_file = "./users_have_col.csv"          # file gốc
output_file = "users_with_course.csv"  # file kết quả
course_code = "Tin 12 - CS"       # mã khóa học Moodle (shortname)
role = "student"                  # vai trò

with open(input_file, newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    # Loại bỏ cột 'group' nếu có
    fieldnames = [f for f in reader.fieldnames if f != 'group'] + ['course1', 'role1']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in reader:
        # Xóa cột group nếu có
        row.pop('group', None)
        row['course1'] = course_code
        row['role1'] = role
        writer.writerow(row)

print(f"✅ Đã tạo file {output_file} (đã bỏ cột 'group' và thêm course1, role1).")