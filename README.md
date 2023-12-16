# Wumpus at HCMUS

Để cài đặt project, xin các đồng chí sử dụng venv hoặc miniconda (hoặc anaconda nếu bộ nhớ máy tính của các đồng chí dư thừa). Ở đây toi chỉ nói cách dùng conda tại vì toi quen òi hjhj.

Để tạo môi trường chạy project, mở `Anaconda Prompt (miniconda3)` và chạy
```bash
conda create -n wumpus_hcmus python=3.9 -y

# vscode có support tự update môi trường, nhưng nếu chạy cmd thì
conda activate wumpus_hcmus
```

Xin lưu ý là script activate môi trường của miniconda trong vscode đang có bug với powershell, hãy dùng cmd ạ!

Trong đúng cái thư mục chứ project, hãy chạy
```bash
pip install -r requirements.txt
```

Để cài đặt môi trường chạy project.

Nếu file đó có update, hãy tắt hết tất cả các app đang dùng môi trường wumpus_hcmus (không là thư mục hổng cho xóa hết âu). Vào thư mục `miniconda3` trong vị trí đã cài đặt (thường là %userprofile%), vào thư mục `envs` và xóa thư mục wumpus_hcmus đi. Quay lại bước 1 để cài đặt môi trường mới.

Dị thoi chúc các đồng chí code kịp deadline :3.
