# Contract v1 — thống nhất với nhóm 3 trước khi chạy chính thức
Corpus JSONL: id (unique), name, statement (chỉ phát biểu, không proof), namespace,
source_commit (mathlib/LeanDojo commit bất biến).
Query JSONL: id, statement, relevant_ids (dependency IDs), split="test",
pool_id="shared-frozen-pool". UTF-8, mỗi dòng một JSON object.

Nhóm 3 và 4 phải dùng cùng corpus, query, qrels, checksum và quy tắc eligible premise.
Không dùng định lý truy vấn hoặc bản sao statement của nó làm premise.
Không tự chia ngẫu nhiên theorem vì có thể gây rò rỉ dependency/file.
Producer phải chọn một pool premise đã có sẵn trước mọi test theorem (hoặc một
snapshot train và query tương lai tương thích). Bộ mã này KHÔNG triển khai per-query
import/time filtering; benchmark cần kiểu pool đó phải bổ sung filtering chung cho
cả exact và ANN, không chỉ lọc top-k sau tìm kiếm.

Adapter LeanDojo phụ thuộc schema/version nguồn: xuất dependency đầy đủ sang
relevant_ids, resolve tên bằng qualified name và vị trí file; không suy diễn qrels
bằng substring. Xác nhận dependency thuộc pool, ghi số query bị loại và lý do.
Bộ mã không tải một benchmark tùy ý rồi tuyên bố là split chung đã thống nhất.

Manifest sinh tự động: checksum input và output, model/revision, pooling, dimension,
dtype, normalization, số bản ghi. Ghi nguồn, giấy phép, URL, ngày tải và commit thật
vào docs/data_card.md trước khi dùng corpus ngoài.
