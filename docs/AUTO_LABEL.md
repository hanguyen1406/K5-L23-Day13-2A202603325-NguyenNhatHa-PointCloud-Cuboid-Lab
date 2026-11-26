# Tự động đề xuất cuboid từ LiDAR

`docs/tools/auto_label.py` tạo tối đa 6 hộp nháp gần LiDAR nhất cho mỗi trong 10 frame của mã số trong `configs/lab.ini` (mặc định tối đa 60 hộp). Công cụ không cần model tải từ mạng: nó gom điểm foreground thành cụm trên mặt phẳng XY rồi dùng PCA để ước lượng hộp xoay. Kết quả nằm trong `work/auto-label-proposals.json` (thư mục `work/` không commit).

```bash
python docs/tools/auto_label.py
```

Lệnh trên chỉ tạo file đề xuất để xem trước. Để thêm cuboid nháp vào task CVAT local `D13-<student>`:

```bash
python docs/tools/auto_label.py --apply
```

Tool hỏi mật khẩu CVAT khi chạy (hoặc đọc biến môi trường `CVAT_PASSWORD`), rồi nhập cuboid 3D qua định dạng point-cloud Sly của CVAT. Mỗi frame chọn tối đa 5 hoặc 6 vật gần nhất (`--per-frame 5` hoặc `--per-frame 6`, mặc định 6). Khi áp dụng, tool đếm Shape đã có và chỉ thêm đến khoảng mục tiêu 60–70 cuboid; frame đã có Shape được bỏ qua. Nếu task đã có từ 60 Shape trở lên thì không thêm nữa; nếu vượt 70 thì dừng và báo cần xử lý annotation cũ thủ công. Tool không xóa annotation. Nếu task có Track, tool dừng để tránh nhập trùng. Task phải khớp đúng 10 frame và có đủ 5 nhãn của lab. Có thể chỉ rõ task bằng `--task-id 12`. Tool chỉ cho phép host local (`localhost`, `127.0.0.1`, `::1`); nhập theo chế độ append.

Vạch đỏ ngắn (`+X`) được đảo 180° so với trục PCA ban đầu để theo quy ước hướng đầu xe của lab. PCA từ một scan không tự phân biệt chắc chắn đầu và đuôi; hãy kiểm lại vạch đỏ bằng ảnh camera và chỉnh trong CVAT nếu cần.

Không dùng REST PATCH thông thường cho 3D cuboid: endpoint đó kiểm tra độ dài điểm theo dạng cuboid 2D. Tool đóng gói đề xuất theo định dạng point-cloud 3D được CVAT hỗ trợ rồi nhập vào task.

Tuỳ chọn: `--student MSSV`, `--data <thư_mục_data-VF>`, `--cell-size 0.35`, `--min-cells 4`, `--per-frame 5` hoặc `--per-frame 6`, `--out <đường_dẫn.json>`. Tăng `--min-cells` để bỏ bớt cụm nhỏ; giảm có thể làm tăng nhiễu. Đầu ra giữ hệ mét VF: x trái, y sau, z lên; mỗi hộp có tâm, kích thước, yaw radian, class gợi ý, số điểm và `needs_review: true`.

Sau khi `--apply`, mở task CVAT và kiểm từng hộp ở Top/Side/Front, đối chiếu ảnh camera, rồi Save. Kiểm tra hướng đầu xe, class, kích thước, đáy chạm đường, vật bên cạnh bị nhập chung, vật bị tách cụm và quy tắc bỏ qua vật quá thưa. Tạo/giữ nhãn chỉ sau khi đã xác nhận có đủ bằng chứng theo [GUIDELINE.md](GUIDELINE.md). Cuối cùng chạy `python scripts/lab.py sync`.

## Giới hạn

- Đây là gợi ý dựa trên hình học, không phải pretrain model hay nhãn tự động đáng tin cậy. Class và hướng đầu/đuôi thường không thể suy ra chắc chắn từ một scan LiDAR; class trong JSON có confidence `low` có chủ ý.
- Cụm BEV có thể nhập hai vật gần nhau, tách một vật thưa thành nhiều cụm, hoặc nhầm lan can/vật thể đường thành xe/người.
- PCA dùng các điểm quan sát được nên hộp có thể thiếu phần bị che và kích thước xe/người thường bị thiếu. Đáy nháp được neo gần z=-1.7 m theo mặt đường điển hình VF; địa hình hoặc độ dốc khác sẽ làm đáy lệch và phải kiểm tra trong CVAT.
- Công cụ chỉ xử lý 10 frame được chọn theo quy tắc của dự án, trong bán kính 50 m; không nội suy giữa frame.
- Không thay đổi `scripts/lab.py` hay `cvat_lab/`; đây là công cụ phụ độc lập. Sau khi hoàn tất nhãn trong CVAT, tiếp tục `python scripts/lab.py sync` như quy trình hiện có.
