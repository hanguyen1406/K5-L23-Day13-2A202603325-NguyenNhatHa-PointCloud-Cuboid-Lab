# Báo cáo Day 13 — Nguyễn Nhật Hạ, 2A202603325

> **Tình trạng theo bản CSV hiện tại:** có 44 cuboid, thấp hơn yêu cầu tối thiểu 53. Theo mức tối thiểu 8 cuboid ở frame đầu và 5 ở mỗi frame sau, còn thiếu 12 cuboid: `s01f33` +5, `s01f49` +1, `s02f21` +1, `s02f53` +3, `s05f23` +2. Nếu bổ sung đúng các frame này, tổng sẽ là 56 và đủ mức tối thiểu từng frame. Ảnh minh chứng đã có đủ 11 file theo tên yêu cầu. Các thông tin không thể xác định từ ảnh/CSV được ghi rõ là chưa được ghi nhận, không suy đoán.
>
> Không đưa biển số, chữ trên biển hiệu/biển chỉ đường, tên đường hay địa danh vào báo cáo public. Ảnh camera thật chỉ nộp trong ZIP LMS, không commit lên repo.

## 1. Kết luận trước

- MSSV: `2A202603325`; task: `D13-2A202603325`.
- 10 frame trong bảng A: `s01f33`, `s01f49`, `s02f21`, `s02f53`, `s03f12`, `s03f53`, `s04f00`, `s04f32`, `s05f01`, `s05f23`.
- Hệ điều hành: Windows. Trình duyệt, phiên bản CVAT và MSSV bạn ngồi cạnh: chưa được cung cấp.
- Bảng A hiện có **44 cuboid**. `s02f53` ít nhất, với 2 cuboid; nguyên nhân không thể xác định từ bảng xuất. Phiếu tự kiểm gắn cờ **9/44 cuboid**. Mức độ tự tin về hướng, đáy, kích thước, class và vật xa chưa được người gán nhãn ghi lại.
- Ảnh chụp cho thấy giao diện CVAT có khung 3D cùng các cửa sổ Top/Side/Front. Để kiểm hộp, quan sát hình dạng từ các hướng này, đối chiếu mũi tên yaw và point cloud; `preview` cung cấp ảnh chiếu lên camera.

## 2. Đọc frame (Bước 2)

Ảnh: `t1-s01f33-3d.png`, `t1-s01f33-top.png`, `t1-s01f49-3d.png`, `t1-s01f49-top.png`. Hệ VF có `+x` sang trái, `+y` ra sau, `+z` lên; phía trước xe là `-y`. Ảnh top cho thấy point cloud và các cuboid nhưng không có chú thích chữ chỉ rõ cạnh ảnh ứng với phía trước / `+x` / `+y`, nên không khẳng định hướng theo cạnh màn hình.

| Frame | Phía trước; hướng +x, +y | Mặt đường / độ cao so với LiDAR | Vật xa nhất | Loại vật; vật phía sau/hai bên; cụm chưa đọc được | Ảnh |
|---|---|---|---|---|---|
| s01f33 | Phía trước là `-y`; cạnh tương ứng trên ảnh chưa ghi chú | Mốc mặt đường của bộ dữ liệu khoảng z=-1.7 m; độ dốc riêng chưa xác định | Cuboid xa nhất trong bảng A: 17.29 m | Bảng A có 3 nhãn Car; ảnh top/3D cho thấy các cụm điểm xe và hộp, cụm không đọc được chưa ghi nhận | 2 ảnh có |
| s01f49 | Phía trước là `-y`; cạnh tương ứng trên ảnh chưa ghi chú | Mốc mặt đường của bộ dữ liệu khoảng z=-1.7 m; độ dốc riêng chưa xác định | Cuboid xa nhất trong bảng A: 15.94 m | Bảng A có 4 nhãn Car; ảnh top có nhiều cụm điểm/hộp, cụm không đọc được chưa ghi nhận | 2 ảnh có |

Từ hai frame: camera cho biết màu sắc/diện mạo bề mặt, ngữ cảnh và giúp phân biệt đầu-đuôi hoặc loại xe; LiDAR cho biết khoảng cách 3D theo mét, hình dạng/kích thước không gian của cụm điểm và vật ở hai bên/phía sau ngoài góc nhìn của một camera. Đây là khác biệt về loại thông tin; ảnh chụp hiện tại không lưu lại ví dụ cụ thể cho từng xe.

Tám frame còn lại trong bảng A:

| Frame | Phía trước ở cạnh nào của ảnh top | Điều lạ (nếu có) |
|---|---|---|
| s02f21 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 4 cuboid; quan sát riêng về điểm lạ chưa được ghi lại |
| s02f53 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 2 cuboid; ít nhất trong 10 frame; quan sát riêng về điểm lạ chưa được ghi lại |
| s03f12 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 6 cuboid; quan sát riêng về điểm lạ chưa được ghi lại |
| s03f53 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 6 cuboid; có nhãn Bus, Cyclist và Car; quan sát riêng về điểm lạ chưa được ghi lại |
| s04f00 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 6 cuboid; có các cờ kích thước trong phiếu tự kiểm |
| s04f32 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 5 cuboid; có cuboid xa nhất toàn bộ bảng A (25.45 m) |
| s05f01 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 5 cuboid; phiếu tự kiểm gắn cờ kích thước nhãn Cyclist |
| s05f23 | Phía trước là `-y`; cạnh ảnh chưa ghi chú | 3 cuboid; quan sát riêng về điểm lạ chưa được ghi lại |

## 3. Ba cuboid có hướng dẫn (Bước 3)

Các hàng dưới đây là ví dụ nhận diện được từ bảng A; chỉ số liệu và cờ tự kiểm được trích từ CSV, không thay thế việc kiểm trực quan trên CVAT.

| Vật | Frame, idx | Class | Yaw trong bảng A | Đáy / tự kiểm | Kích thước và kiểm trực quan |
|---|---|---|---:|---|---|
| Xe con gần | `s04f00`, 1 | Car | 270.0° | `z_bottom=-1.829 m`, `ground_gap=-0.05 m`; cờ width 2.52 m ngoài khoảng | `length=4.992 m`, `width=2.524 m`, `height=2.013 m`; ảnh xe con cho thấy hộp, nhưng không đủ thông tin để đối chiếu mã frame và hướng mũi tên |
| Xe buýt | `s03f53`, 6 | Bus | 86.6° | `z_bottom=-1.889 m`, `ground_gap=0.04 m`; không có cờ | `length=12.639 m`, `width=3.014 m`, `height=3.060 m`; ảnh xe buýt/tải cho thấy hộp, chưa xác minh hướng bằng camera |
| Xe hai bánh | `s03f53`, 3 | Cyclist | 90.0° | `z_bottom=-1.700 m`, `ground_gap=0.05 m`; không có cờ | `length=1.330 m`, `width=0.380 m`, `height=1.420 m`; ảnh có Top/Side/Front, hướng class vẫn cần đối chiếu camera |

Ảnh minh chứng có: `t2-a-car.png`, `t2-b-bus-truck.png`, `t2-c-ped-cyclist.png`. Ảnh xe hai bánh có các cửa sổ Top/Side/Front; ảnh xe con và xe buýt/tải cho thấy hộp trong khung point cloud. CSV xác nhận các class đã chọn, nhưng ảnh chụp không hiển thị rõ mã frame/idx để đối chiếu từng hàng trong bảng.

Điểm khác nhau trong vòng hiệu chuẩn và danh sách vật đã bỏ qua vì thiếu cơ sở không có trong ảnh/CSV; cần ghi theo trao đổi thực tế với lớp, hoặc xác nhận “không có”.

## 4. Bốn hiện tượng chất lượng (Bước 4)

Ảnh đã có. Nguyên nhân dưới đây là giả thuyết, không phải kết luận chắc chắn chỉ từ LiDAR.

| Hiện tượng | Frame / ảnh / nguồn | Nguyên nhân (giả thuyết) | Dấu hiệu trên point cloud | Hệ quả khi gán |
|---|---|---|---|---|
| Bóng che | `t4-1-bong-che.png`; frame/nguồn không ghi trên ảnh | Vật thể gần che tia LiDAR | Các hộp nằm trên cụm điểm, một số vùng sau/vùng cạnh vật có ít hoặc không có điểm so với vùng lân cận | Vùng khuất không đồng nghĩa đường trống; chỉ suy luận phần bị che nếu đủ cơ sở, bật occluded |
| Thưa ở xa | `t4-2-thua-o-xa.png`; frame/nguồn không ghi trên ảnh | Mật độ điểm giảm theo khoảng cách | Cụm điểm trong hộp thưa, rời rạc, hình dáng vật khó thấy đầy đủ | Chỉ gán nếu thấy khoảng 15–20% thể tích hoặc có ảnh hỗ trợ rõ; nếu không thì bỏ qua và ghi LOW_VISIBILITY |
| Phản xạ thấp / ít điểm bất thường | `t4-3-phan-xa-thap.png`; frame/nguồn không ghi trên ảnh | Có thể do bề mặt/vật liệu hoặc góc tới làm tín hiệu phản hồi yếu | Trong vùng hộp chỉ có các điểm rải rác; ảnh không lưu intensity nên không chứng minh được nguyên nhân phản xạ | Không nới hộp theo suy đoán; đối chiếu camera và ghi nguyên nhân là giả thuyết |
| Điểm lạ | `t4-4-diem-la.png`; frame/nguồn không ghi trên ảnh | Nhiễu đo, phản xạ nhiều đường hoặc vật nằm ngoài mặt đường là các khả năng | Có cụm điểm rời rạc không tạo thành bề mặt vật thể rõ trong khung đã chụp | Không gán điểm đơn lẻ thành vật; cần kiểm tra vị trí/độ cao trước khi kết luận |

Nguồn/frame thực tế của bốn ảnh không hiển thị trong ảnh chụp; bổ sung mã frame nếu còn nhớ hoặc xem lại CVAT.

## 5. Số từ cuboid của tôi (Bước 5)

Số liệu hiện tại lấy từ `submission/D13-2A202603325-bangA.csv` và cột `points_in`, `ground_gap_m`, `flags` trong `submission/D13-2A202603325-tukiem.csv`. `r` tính từ tọa độ tâm x, y, z. Mặt đường tham chiếu khoảng −1.7 m.

| Cuboid (frame, idx, class) | z (m) | h (m) | z đáy (m) | dist_m | r (m) | yaw_deg | points_in | Nhận xét từ phiếu tự kiểm |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `s04f00`, 1, Car | -0.822 | 2.013 | -1.829 | 4.39 | 4.46 | 270.0° | 5916 | gap -0.05 m; width 2.52 m bị gắn cờ ngoài khoảng |
| `s03f53`, 3, Cyclist | -0.990 | 1.420 | -1.700 | 11.37 | 11.42 | 90.0° | 226 | gap 0.05 m; không có cờ |
| `s04f32`, 5, Car | -1.175 | 1.466 | -1.909 | 25.45 | 25.47 | 276.5° | 174 | gap 0.06 m; không có cờ |

Cuboid gần nhất trong bảng A hiện tại là `s04f00`, idx 1: `dist_m=4.39 m`, `r=4.46 m`. Xa nhất là `s04f32`, idx 5: `dist_m=25.45 m`, `r=25.47 m`.

| Cuboid Car | dist_m | points_in |
|---|---:|---:|
| `s04f00`, idx 1 | 4.39 m | 5916 |
| `s01f33`, idx 1 | 8.69 m | 1673 |
| `s01f33`, idx 3 | 17.29 m | 458 |
| `s04f32`, idx 5 | 25.45 m | 174 |

Trong bốn ví dụ này, cuboid xa nhất cách xa khoảng 5.8 lần so với gần nhất và có khoảng 2.9% số điểm. Hai hộp có kích thước và số điểm rất khác nên không thể quy toàn bộ chênh lệch cho khoảng cách. So sánh hai xe trong `s01f33`: từ 8.69 m lên 17.29 m (gấp 1.99 lần), số điểm giảm từ 1673 xuống 458 (còn khoảng 27.4%). Xu hướng phù hợp với slide về mật độ giảm theo khoảng cách, nhưng số đo không phải thí nghiệm kiểm soát.

Yaw của một số hộp trong CSV gần 270° (`s04f00`, idx 1: 270.0°) và gần 90° (`s03f53`, idx 3: 90.0°). Theo hệ VF, đó lần lượt là quy ước hướng xe cùng chiều và ngược chiều; ảnh chụp hiện tại không cho phép xác nhận độc lập chiều di chuyển của các xe đó. Phiếu hiện gắn cờ 9 cuboid:

- `s01f49` idx 1: length 2.45 m ngoài khoảng Car.
- `s03f12` idx 2: length 2.81 m ngoài khoảng Car.
- `s03f53` idx 4: ground gap -0.63 m và width 1.39 m ngoài khoảng Car.
- `s04f00` idx 1: width 2.52 m; idx 3: width 2.43 m; idx 4: height 1.18 m; idx 6: length 2.74 m — ngoài khoảng của Car.
- `s04f32` idx 4: width 2.40 m ngoài khoảng Car.
- `s05f01` idx 3: Cyclist length 4.47 m và width 1.76 m ngoài khoảng.

So sánh kích thước với bảng 4.3: Car `s04f00` idx 1 có width 2.524 m, lớn hơn cả khoảng tham chiếu SUV/minivan 1.80–2.10 m; Cyclist `s05f01` idx 3 có `4.471 × 1.760 × 1.147 m`, vượt các khoảng tham chiếu chiều dài/rộng và thấp hơn khoảng chiều cao của xe hai bánh có người. Hai hộp này cần được xem lại trên CVAT/ảnh gốc; cờ chỉ ra điểm bất thường, không tự xác định được nguyên nhân.

Không có lịch sử sửa hộp sau preview/selfcheck hoặc biên bản đổi kiểm trong các file đã cung cấp, nên không thể nêu hai hộp đã sửa, cảnh báo được giữ lại hay MSSV bạn đối chiếu với. Trước khi nộp, ghi lại theo thao tác và trao đổi thật; không suy ra từ trạng thái CSV hiện tại.

## 6. Ý nghĩa của nhãn, cách dùng AI và điều còn chưa chắc

Nhãn 3D đo bằng mét mô tả vị trí và kích thước vật thể trong không gian, nên không phụ thuộc trực tiếp vào độ phân giải hay góc nhìn của một camera như hộp pixel 2D. Với vật xa hoặc thưa điểm, hình dạng và ranh giới kém rõ; cần áp dụng quy tắc thận trọng để tránh tạo nhãn không đủ căn cứ.


