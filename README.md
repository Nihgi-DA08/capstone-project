# CAPSTONE PROJECT
Dựa trên dữ liệu booking khách sạn tại Bồ Đào Nha, phân tích xu hướng đặt phòng và trực quan hóa các yếu tố ảnh hưởng đến lượng booking, khách hàng, quốc gia, kênh bán và Average Daily Rate.

## HÌNH ẢNH DEMO
<p align="center">
<img src='pic/0.png'></img>
</p>

## CODE DEMO
```python
from pathlib import Path

DATA_PATH = Path("data/data_valid.csv")
COUNTRY_CODES_PATH = Path("data/country_codes_list.csv")
EXCEL_PATH = Path("excel/portugal_hotel_booking.xlsx")
```

## CẤU TRÚC DỮ LIỆU
- `data/`: dữ liệu CSV sau khi làm sạch, các dòng không hợp lệ và bảng mã quốc gia.
- `excel/`: file Excel nguồn.
- `powerpoint/`: file thuyết trình dự án.
- `pic/`: hình ảnh dùng trong README và mô tả công nghệ.
- `data_cleaning.ipynb`: notebook làm sạch dữ liệu và sinh `data/data_valid.csv`, `data/data_invalid.csv`.
- `analyse_portugal_hotel_booking.ipynb`: notebook phân tích EDA, trực quan hóa và mô hình Linear Regression minh họa.
- `app.py`: Dash app dùng dữ liệu sạch để hiển thị dashboard.

### THÀNH VIÊN
Nhóm NIHGI gồm các thành viên:

<img src='pic/1.jpg' align='right' width='16%' height='16%'></img>
<div style='display:flex;'>

- Nguyễn Đặng Trường An
- Nguyễn Hồng Phương Nghi
- Trần Văn Ninh (đã rời nhóm)
- Nguyễn Thu Trang
- Lương Thụy Vi (đã rời nhóm)

</div>

### TÍCH HỢP
<img src='pic/2.png' align='left' width='3%' height='3%'></img>
<div style='display:flex;'>

- Matplotlib » 3.8+

</div>
<img src='pic/3.png' align='left' width='3%' height='3%'></img>
<div style='display:flex;'>

- NumPy » 1.26+

</div>
<img src='pic/4.png' align='left' width='3%' height='3%'></img>
<div style='display:flex;'>

- Pandas » 2.2+

</div>
<img src='pic/5.png' align='left' width='3%' height='3%'></img>
<div style='display:flex;'>

- seaborn » 0.13+

</div>
<img src='pic/6.png' align='left' width='3%' height='3%'></img>
<div style='display:flex;'>

- Plotly » 5.22+

</div>
<img src='pic/7.png' align='left' width='3%' height='3%'></img>
<div style='display:flex;'>

- scikit-learn » 1.5+

</div>

### CHẠY DỰ ÁN
```powershell
py -m pip install -r requirements.txt
py -m jupyter nbconvert --to notebook --execute --inplace data_cleaning.ipynb --ExecutePreprocessor.timeout=900
py -m jupyter nbconvert --to notebook --execute --inplace analyse_portugal_hotel_booking.ipynb --ExecutePreprocessor.timeout=900
py app.py
```
