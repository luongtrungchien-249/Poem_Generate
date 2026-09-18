"""Tool `kiem_tra_tho` — cho mô hình tự soi bản nháp NGAY TRONG vòng ReAct.

Quan hệ với cổng vòng ngoài:

    tool này        mô hình gọi tuỳ ý, có thể không gọi, có thể gọi rồi phớt lờ
                    -> THẨM QUYỀN: tư vấn
    verify_output   đường ống luôn chạy, mô hình không bỏ qua được
                    -> THẨM QUYỀN: phán quyết

Cả hai gọi đúng một hàm `application.rule.kiem_tra_bai_tho`. Hai bộ luật song song
là cách chắc chắn nhất để hai nơi nói hai điều khác nhau.

Vì sao tool này nằm ở `adapters/`: mọi tool trong sổ đăng ký đều ở đây, kể cả tool
không chạm mạng. Chỗ đứng theo VAI TRÒ trong hệ thống, không theo việc nó có I/O hay
không. Bản thân phép kiểm vẫn thuần và vẫn nằm ở `application/rule.py`.
"""

from typing import Any

from application.agent.tools.registry import tool_registry
from application.rule import kiem_tra_bai_tho


def register_poem_check_tool() -> None:
    @tool_registry.register(
        name="kiem_tra_tho",
        description=(
            "Kiểm một bản nháp thơ thất ngôn tự do TRƯỚC KHI trả lời. "
            "Trả về số tiếng từng dòng, các dòng sai luật, sơ đồ vần và khuôn thanh. "
            "Gọi tool này rẻ và nhanh — nên gọi mỗi khi vừa soạn xong một bản nháp."
        ),
        parameters_schema={
            "type": "object",
            "properties": {
                "van_ban": {
                    "type": "string",
                    "description": "Toàn bộ bản nháp, các dòng cách nhau bằng ký tự xuống dòng",
                }
            },
            "required": ["van_ban"],
        },
    )
    def _kiem_tra_tho(van_ban: str) -> dict[str, Any]:
        v = kiem_tra_bai_tho(van_ban)
        return {
            "dat": v.dat,
            "so_dong": v.so_dong,
            "so_tieng_tung_dong": [
                {"dong": d.so, "so_tieng": d.so_tieng} for d in v.dong
            ],
            "vi_pham": [
                {
                    "ma": vp.ma,
                    "dong": vp.dong,
                    "can": vp.ky_vong,
                    "dang_co": vp.thuc_te,
                    "goi_y": vp.goi_y,
                }
                for vp in v.vi_pham
            ],
            "so_do_van": ["".join(k) for k in v.so_do_van_theo_kho],
            "khuon": [d.khuon for d in v.dong],
            "ty_le_theo_khuon": v.ty_le_theo_khuon,
            "ghi_chu": list(v.ghi_chu),
        }
