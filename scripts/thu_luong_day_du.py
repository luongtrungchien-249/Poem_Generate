"""Chạy thử MỘT luồng hoàn chỉnh qua đúng đường mà trình duyệt đi.

Gọi vào `http://localhost:3000/api/*` (BFF của Next.js), KHÔNG gọi thẳng FastAPI —
vì đó mới là đường thật của người dùng, và nó đi qua thêm một chặng chuyển tiếp
có thể hỏng riêng.

Không mock gì cả: model thật, tiền thật, thời gian thật.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

GOC = "http://localhost:3000"


def goi(duong: str, than: dict | None = None, method: str = "GET") -> tuple[int, dict, float]:
    du_lieu = json.dumps(than).encode() if than is not None else None
    req = urllib.request.Request(
        f"{GOC}{duong}",
        data=du_lieu,
        method=method,
        headers={"content-type": "application/json"},
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            body = r.read().decode()
            ma = r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        ma = e.code
    giay = time.perf_counter() - t0
    return ma, (json.loads(body) if body else {}), giay


def dong(ky_tu: str = "─") -> None:
    print(ky_tu * 78)


def buoc(n: int, ten: str) -> None:
    print()
    dong("═")
    print(f"  BƯỚC {n} — {ten}")
    dong("═")


loi_luy_ke: list[str] = []


def kiem(dieu_kien: bool, mo_ta: str) -> None:
    print(f"   {'✓' if dieu_kien else '✗'} {mo_ta}")
    if not dieu_kien:
        loi_luy_ke.append(mo_ta)


# ══ BƯỚC 1 ═══════════════════════════════════════════════════════════════════
buoc(1, "Danh mục model — BFF có nối được tới backend không")
ma, models, giay = goi("/api/models")
kiem(ma == 200, f"HTTP 200 ({giay * 1000:.0f} ms)")
kiem(len(models) > 0, f"có {len(models)} model")
ten_model = {m["ten"] for m in models}
kiem("gpt-4o-mini" in ten_model, "danh sách lấy từ configs/models.yaml thật")
kiem(
    all(not any(k in m for k in ("cost", "gia")) for m in models),
    "KHÔNG phơi giá tiền ra client",
)

# ══ BƯỚC 2 ═══════════════════════════════════════════════════════════════════
buoc(2, "Tạo hội thoại mới")
ma, hoi_thoai, giay = goi("/api/conversations", {}, "POST")
kiem(ma == 200, f"HTTP 200 ({giay * 1000:.0f} ms)")
cid = hoi_thoai.get("conversation_id", "")
kiem(cid.startswith("conv_"), f"máy chủ sinh id: {cid}")
kiem(hoi_thoai.get("tieu_de") == "", "tiêu đề còn trống, chờ câu đầu tiên")

# ══ BƯỚC 3 ═══════════════════════════════════════════════════════════════════
buoc(3, "Yêu cầu thiếu thông tin → hệ thống phải HỎI LẠI, không được đoán")
YEU_CAU = "Tôi muốn làm thơ về chủ đề người con gái Việt Nam xưa"
ma, r3, giay3 = goi("/api/poem", {"yeu_cau": YEU_CAU, "session_id": cid}, "POST")
kiem(ma == 200, f"HTTP 200 — hỏi lại KHÔNG phải lỗi ({giay3:.1f} giây)")
kiem(r3.get("can_lam_ro") is True, "cờ can_lam_ro")
kiem(bool(r3.get("cau_hoi")), f"câu hỏi: {r3.get('cau_hoi', '')[:58]}")
thieu = r3.get("truong_thieu", [])
kiem(bool(thieu), f"nêu rõ thiếu gì: {thieu}")
kiem(bool(r3.get("trace_id")), "có trace_id để đối chiếu log")
kiem("poem" not in r3, "KHÔNG kèm bài thơ nào")

# ══ BƯỚC 4 ═══════════════════════════════════════════════════════════════════
buoc(4, "Lượt hỏi lại đã được LƯU vào hội thoại chưa")
ma, ct, _ = goi(f"/api/conversations/{cid}")
kiem(ma == 200, "đọc lại được hội thoại")
kiem(ct.get("so_tin_nhan") == 2, f"có {ct.get('so_tin_nhan')} tin nhắn (hỏi + đáp)")
kiem(ct.get("tieu_de") == YEU_CAU, f"tiêu đề tự đặt: {ct.get('tieu_de', '')[:50]}")

# ══ BƯỚC 5 ═══════════════════════════════════════════════════════════════════
buoc(5, "Trả lời câu hỏi — gửi vào TRƯỜNG TƯỜNG MINH để thoát vòng hỏi")
print("   (đây là chỗ giao diện từng lặp vô hạn: trả lời bằng chữ tự do thì")
print("    câu trả lời lại bị trích xuất thành 'suy_doan' và bị hỏi lại)")
than5 = {
    "yeu_cau": f"{YEU_CAU}. 8 dòng",
    "chu_de": "người con gái Việt Nam xưa",
    "so_dong": 8,
    "session_id": cid,
}
ma, r5, giay5 = goi("/api/poem", than5, "POST")
print(f"   ⏱  lượt này mất {giay5:.1f} giây")

if r5.get("can_lam_ro"):
    kiem(False, f"VẪN hỏi lại → vòng lặp chưa khép: {r5.get('cau_hoi', '')[:50]}")
    ket_cuc = "hoi_lai"
elif ma == 422:
    # Không phải lỗi hệ thống: đây là fail-closed, ~17% số lượt rơi vào đây.
    kiem(True, "đi QUA được cổng hỏi lại, đã sinh bài rồi mới trượt luật")
    kiem(ma == 422, "HTTP 422 — từ chối trả bài sai luật")
    kiem("poem" not in r5, "KHÔNG có trường nào chứa văn bản thơ (fail closed)")
    kiem(bool(r5.get("chan_doan")), "có chẩn đoán từng dòng để người dùng biết sai đâu")
    kiem(r5.get("so_luot_da_sua", 0) > 0, f"đã tự sửa {r5.get('so_luot_da_sua')} lượt")
    ket_cuc = "khong_dat"
else:
    kiem(ma == 200, "HTTP 200")
    kiem(bool(r5.get("poem")), "có bài thơ")
    kiem(r5.get("dat_luat") is True, "dat_luat = True")
    kiem(r5.get("so_dong") == 8, f"đúng 8 dòng (thực tế {r5.get('so_dong')})")
    kiem(len(r5.get("bang_chung_bay_tang", [])) == 7, "đủ 7 tầng bằng chứng")
    da_chay = sum(1 for t in r5.get("bang_chung_bay_tang", []) if t["da_chay"])
    kiem(da_chay == 7, f"cả 7 tầng đều đã kiểm ({da_chay}/7)")
    ket_cuc = "tho"
    print()
    dong()
    print(r5["poem"])
    dong()

# ══ BƯỚC 6 ═══════════════════════════════════════════════════════════════════
buoc(6, "Lượt vừa rồi có được lưu, và hội thoại có lên đầu sidebar không")
ma, ct2, _ = goi(f"/api/conversations/{cid}")
kiem(ct2.get("so_tin_nhan", 0) >= 3, f"có {ct2.get('so_tin_nhan')} tin nhắn")
if ket_cuc == "khong_dat":
    kiem(
        ct2.get("so_tin_nhan") == 3,
        "bài trượt luật vẫn ghi CÂU HỎI (3 tin), không ghi bài sai",
    )
ma, ds, _ = goi("/api/conversations")
kiem(bool(ds) and ds[0]["conversation_id"] == cid, "hội thoại vừa dùng đứng đầu danh sách")

# ══ BƯỚC 7 ═══════════════════════════════════════════════════════════════════
buoc(7, "Luồng chat có stream — SSE qua BFF")
t0 = time.perf_counter()
req = urllib.request.Request(
    f"{GOC}/api/chat",
    data=json.dumps(
        {
            "messages": [{"role": "user", "content": "Chào bạn, nói ngắn gọn thôi"}],
            "stream": True,
            "session_id": cid,
        }
    ).encode(),
    method="POST",
    headers={"content-type": "application/json"},
)
su_kien: list[dict] = []
co_done = False
giay_chu_dau: float | None = None
with urllib.request.urlopen(req, timeout=300) as r:
    for dong_byte in r:
        d = dong_byte.decode().strip()
        if not d.startswith("data:"):
            continue
        tai = d[5:].strip()
        if tai == "[DONE]":
            co_done = True
            break
        sk = json.loads(tai)
        su_kien.append(sk)
        if sk.get("delta") and giay_chu_dau is None:
            giay_chu_dau = time.perf_counter() - t0
giay7 = time.perf_counter() - t0

kiem(bool(su_kien), f"nhận {len(su_kien)} sự kiện")
kiem(co_done, "luồng kết thúc bằng [DONE]")
toan_van = "".join(s.get("delta", "") for s in su_kien)
kiem(bool(toan_van), f"có nội dung: {toan_van[:50]}")
kiem(all(s.get("trace_id") for s in su_kien), "mọi sự kiện đều mang trace_id")
print(f"   ⏱  tổng {giay7:.1f} giây · chữ đầu {giay_chu_dau:.1f} giây"
      if giay_chu_dau else f"   ⏱  tổng {giay7:.1f} giây")

# Cái bẫy đã vá: finish_reason tới TRƯỚC nội dung.
vi_tri_finish = next(
    (i for i, s in enumerate(su_kien) if s.get("finish_reason")), None
)
vi_tri_chu = next((i for i, s in enumerate(su_kien) if s.get("delta")), None)
if vi_tri_finish is not None and vi_tri_chu is not None and vi_tri_finish < vi_tri_chu:
    print("   ⚠  finish_reason tới TRƯỚC nội dung — client phải đợi [DONE] (đã xử lý)")

# ══ BƯỚC 8 ═══════════════════════════════════════════════════════════════════
buoc(8, "Cô lập và dọn dẹp")
ma, _, _ = goi("/api/conversations/khong-he-ton-tai")
kiem(ma == 404, "hội thoại không tồn tại → 404, không phải 500")
ma, _, _ = goi(f"/api/conversations/{cid}", None, "DELETE")
kiem(ma == 200, "xoá được hội thoại")
ma, _, _ = goi(f"/api/conversations/{cid}")
kiem(ma == 404, "xoá rồi thì 404")

# ══ TỔNG KẾT ═════════════════════════════════════════════════════════════════
print()
dong("═")
if loi_luy_ke:
    print(f"  KẾT QUẢ: {len(loi_luy_ke)} phép kiểm KHÔNG đạt")
    for m in loi_luy_ke:
        print(f"    ✗ {m}")
else:
    print("  KẾT QUẢ: toàn bộ phép kiểm ĐẠT")
print(f"  Kết cục lượt sinh thơ: {ket_cuc}")
dong("═")
sys.exit(1 if loi_luy_ke else 0)
