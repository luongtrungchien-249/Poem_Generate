"""Tool `danh_gia_chat_luong_tho` — thi hành chỉ thị 3.

QUAN HỆ VỚI `kiem_tra_tho`, và vì sao là HAI tool chứ không phải một:

    kiem_tra_tho            phán LUẬT     — nguồn: rule.py, ĐÓNG BĂNG
    danh_gia_chat_luong_tho phán CHẤT LƯỢNG — nguồn: chuẩn dự án

Gộp chúng lại thì mô hình không phân biệt được "bài sai luật" với "bài chưa đủ tốt",
và sẽ sửa nhầm loại. Tách ra thì mỗi lần gọi trả về đúng một loại phán quyết.

THẨM QUYỀN: cả hai tool này đều chỉ TƯ VẤN. Mô hình có thể gọi, có thể không, có thể
gọi rồi phớt lờ. Thứ bảo đảm là `PoemVerifierDayDu` ở vòng ngoài — nó luôn chạy.
"""

from typing import Any

from application.agent.tools.registry import tool_registry
from application.poetry.cot import dung_khung_suy_luan, tach_tho_khoi_khung
from application.poetry.quality import danh_gia_chat_luong
from application.rule import kiem_tra_bai_tho


def register_poem_quality_tool() -> None:
    @tool_registry.register(
        name="danh_gia_chat_luong_tho",
        description=(
            "Chấm CHẤT LƯỢNG một bản nháp thơ (khác với kiểm luật). Bảy chiều: lặp "
            "tiếng, lặp dòng, bám chủ đề, nhạc tính, đa dạng vần, mạch lạc, hình ảnh. "
            "Trả về chiều nào chưa đạt, và nếu chưa đạt thì trả luôn KHUNG SUY LUẬN "
            "bốn ô phải điền trước khi viết lại. Gọi tool này SAU khi kiem_tra_tho đã "
            "báo bài đúng luật."
        ),
        parameters_schema={
            "type": "object",
            "properties": {
                "van_ban": {
                    "type": "string",
                    "description": "Toàn bộ bản nháp, các dòng cách nhau bằng ký tự xuống dòng",
                },
                "chu_de": {
                    "type": "string",
                    "description": "Chủ đề người dùng yêu cầu, để chấm mức bám chủ đề. "
                                   "Bỏ trống thì chiều này không được kiểm.",
                },
            },
            "required": ["van_ban"],
        },
    )
    def _danh_gia_chat_luong_tho(van_ban: str, chu_de: str | None = None) -> dict[str, Any]:
        tho = tach_tho_khoi_khung(van_ban)
        v = kiem_tra_bai_tho(tho)
        cl = danh_gia_chat_luong(v, chu_de=chu_de)

        ra: dict[str, Any] = {
            # Hai cờ tách rời, không gộp — xem docstring của application/poetry.
            "dat_luat": v.dat,
            "dat_chat_luong": cl.dat,
            "chieu": [
                {
                    "ma": c.ma,
                    "ten": c.ten,
                    "do_duoc": c.do_duoc,
                    "dat": c.dat,
                    "so_do": c.so_do,
                    "nguong": c.nguong,
                    "bang_chung": c.bang_chung,
                }
                for c in cl.chieu
            ],
            "chieu_chua_dat": [c.ten for c in cl.chieu_hong],
            "chieu_khong_do_duoc": list(cl.chieu_khong_do_duoc),
            "ghi_chu": "Chất lượng KHÔNG loại bài khỏi thể thất ngôn tự do. "
                       "Bài có thể đúng luật mà vẫn chưa đạt chất lượng.",
        }
        if not cl.dat:
            # Chỉ thị 3: chưa đạt thì phải suy luận trước khi viết lại.
            ra["khung_suy_luan"] = dung_khung_suy_luan(
                cl, dong_dat=tuple(d.so for d in v.dong)
            )
        return ra
