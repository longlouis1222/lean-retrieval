# Kế hoạch thực nghiệm & phân tích
1. Chốt split chung, snapshot và model SHA với nhóm 3; chạy exact trước.
2. Cố định k=10, query test, encoder, phần cứng và số thread.
3. Chạy 10K / 100K / full (nếu full=100K thì chọn mức thứ ba khác thực tế).
Script dùng nested subset giữ toàn bộ qrels; tập nhỏ phải chứa đủ union qrels.
Nếu không đủ, chuẩn bị benchmark riêng cho từng scale, dùng cùng benchmark
đó cho mọi phương pháp và nhóm 3; báo số query/premise thực tế.
4. Mỗi cấu hình 3 lần; median và min/max nằm trong summary.csv.
5. Sweep HNSW efSearch=16/64/128, IVF nprobe=1/8/32. IVF nlist cố định theo scale.
6. Chạy API 1/10/50 client, ba lần; báo error/timeout cùng QPS.
7. Ablation: lặp toàn bộ embedding + index bằng encoder thứ hai hoặc dimension
khác có hỗ trợ; mỗi encoder có exact riêng. So chất lượng retrieval giữa encoder,
không dùng ANN recall thay semantic quality. Đây là kế hoạch, chưa có kết quả thật.
8. Error analysis: metrics.errors.json chứa query miss; join với qrels và namespace,
phân loại symbol ambiguity, truncation, unseen namespace, approximate miss,
missing dependency label. Namespace hiện trong error file là namespace top-1 exact,
không phải taxonomy lỗi tự động hay chủ đề của query.
9. So nhóm 3 trên cùng qrels, Recall@10/MRR@10 và HTTP P95; hybrid là mở rộng.

Pareto hiện xét ba mục tiêu: maximize ANN recall, minimize P95, minimize index
bytes. Sao là điểm không bị trội trong 3D, kích thước marker là index bytes.
Không gọi đó là Pareto peak RAM khi chưa đo RAM đáng tin. Bổ sung đồ thị premise
recall nếu encoder thay đổi. HNSW build seed phụ thuộc Faiss/OpenMP; lưu version,
threads và lặp, không hứa bitwise reproducibility giữa máy.
