# Model/system card & limitations
Demo: signed SHA-256 token hashing 256 chiều, không phải pretrained semantic encoder.
Encoder thật: SentenceTransformer với revision SHA bất biến do nhóm lựa chọn;
CPU, float32, L2 normalization, giới hạn 256 token, pooling theo model config.
Ghi tokenizer/truncation, license, model card và đánh giá Lean trước khi chốt encoder.
Không có huấn luyện hoặc fine-tuning trong bộ mã này.

Search: normalized inner product; Flat exact, HNSW M=16/efConstruction=100,
IVFFlat nlist=min(128,N//40). Sweep efSearch và nprobe có lưu effective parameter.
Cosine tie có thể tạo ANN overlap khác nhau dù cùng score; không diễn giải là
semantic failure. IVF có thể trả -1 khi thiếu candidate; metrics loại sentinel.

Primary metrics đề xuất: premise Recall@10 và P95 search latency.
ANN recall đo overlap top-k exact, khác premise Recall@k. MRR tính trong top-k.
QPS offline là tuần tự, không đại diện serving QPS. Load test đo HTTP end-to-end,
bao gồm encode/cache/queue. Service khóa encoder/search để đảm bảo an toàn;
khả năng throughput bị giới hạn, cần worker/replica để mở rộng sau khi đo.
Cache có giới hạn 512 query, không phải benchmark cold-cache.

RSS sampler 5ms đo process high-water quan sát, gồm vector, exact và index;
không phải RAM riêng của index và có thể bỏ lỡ peak ngắn. Khi bị chặn trả null.
Index bytes là kích thước file, KHÔNG được gọi là peak RAM.
Mỗi build trong cùng process có allocator retention; đo RAM so sánh chuẩn cần
chạy isolated process/container từng cấu hình. Faiss threads=1 để giảm biến động.

Batch local có checkpoint theo input+model hash, nhưng đọc JSON và ghép shard
vào RAM: không tuyên bố out-of-core. Spark là luồng mở rộng xuất Parquet,
chưa chạy trên cluster trong môi trường này; cần cài src và model trên executor,
filesystem chung và tài nguyên hợp lý. Parquet cần join theo id và kiểm checksum
trước khi chuyển sang vector matrix; không được dựa vào thứ tự partition.
Không có GPU, proof success hoặc Lean verifier. Không có kết luận superiority.
