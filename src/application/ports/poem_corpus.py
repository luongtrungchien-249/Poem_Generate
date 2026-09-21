"""Cổng KHO THƠ MẪU — nguồn ví dụ cho few-shot.

Đọc tệp là I/O, nên `application/` chỉ khai cổng; hiện thực nằm ở `adapters/`.

Cổng trả về `tuple` chứ không trả iterator: bộ chọn few-shot phải chấm điểm TOÀN
BỘ kho rồi mới xếp hạng, nên nó cần một tập hữu hạn đã nạp xong. Trả iterator ở
đây chỉ tạo ảo giác tiết kiệm bộ nhớ trong khi nơi gọi vẫn phải gom hết.
"""

from typing import Protocol

from application.poetry.dataset import MauTho


class PoemCorpusPort(Protocol):
    """Kho thơ mẫu đã đúng luật."""

    def tat_ca(self) -> tuple[MauTho, ...]:
        """Toàn bộ bài mẫu dùng được.

        Hợp đồng: MỌI phần tử trả về đều thoả `kiem_tra_bai_tho(...).dat`. Hiện
        thực nào không giữ được điều đó thì đang phá bất biến trung tâm của cơ chế
        few-shot — xem `application/poetry/dataset.py`.
        """
        ...
