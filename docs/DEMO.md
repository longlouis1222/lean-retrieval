# Kịch bản 5–7 phút
1. Giới thiệu bài toán: query là goal/theorem, corpus là premise đã được phép dùng.
2. Mở manifest: model version, pooling, dimension, normalize và checksums.
3. Chạy demo.sh hoặc mở raw CSV đã kèm; giải thích Flat là baseline exact.
4. Mở pareto_1200.png, giải thích recall–P95–index bytes; không tuyên bố ANN luôn nhanh.
5. Mở /docs, gọi /health và /search. Đọc top-k và cosine score.
6. Mở load.csv, so 1/10/50 clients và error count; giải thích cache/lock.
7. Nêu giới hạn: synthetic smoke, chưa có Lean labels thật, chưa có proof success.

Câu hỏi bảo vệ: Vì sao normalize? Vì cosine bằng inner product khi unit norm.
ANN recall cao có chứng minh tìm premise đúng? Không, nó chỉ giống exact encoder.
Tại sao MRR khác Recall? MRR nhấn vị trí premise đúng đầu tiên, recall đo coverage.
Tại sao không chọn riêng cấu hình nhanh nhất? Phải xét mất recall và chi phí.
