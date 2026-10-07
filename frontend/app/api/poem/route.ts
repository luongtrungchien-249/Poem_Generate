import { goiBackend } from "../_backend";
import type { CanLamRo, PoemKhongDat, PoemResponse } from "@/types/api";

/**
 * Sinh thơ — BA mã trạng thái, ba nghĩa khác nhau, và route này phải giữ nguyên
 * sự phân biệt đó thay vì gộp tất cả về "thành công / thất bại":
 *
 *   200 + PoemResponse   bài đã qua luật, kèm bằng chứng bảy tầng
 *   200 + CanLamRo       chưa đủ thông tin → HỎI LẠI (không phải lỗi)
 *   422 + PoemKhongDat   hết lượt sửa → KHÔNG trả bài sai
 *
 * Gộp 422 vào nhánh lỗi chung sẽ làm UI hiện "Oops! Something went wrong" cho
 * một trường hợp mà hệ thống đang hoạt động ĐÚNG — nó từ chối trả bài sai luật.
 * Vì vậy 422 được chuyển tiếp nguyên vẹn kèm `chan_doan`, không nuốt mất.
 */
export async function POST(req: Request) {
  const than = await req.json().catch(() => null);
  if (!than?.yeu_cau) {
    return Response.json({ detail: "Thiếu nội dung yêu cầu." }, { status: 400 });
  }

  const kq = await goiBackend<PoemResponse | CanLamRo>("/v1/poem", {
    method: "POST",
    body: JSON.stringify({
      yeu_cau: than.yeu_cau,
      chu_de: than.chu_de ?? null,
      so_dong: than.so_dong ?? null,
      cam_xuc: than.cam_xuc ?? null,
      phong_cach: than.phong_cach ?? null,
      max_repair_rounds: than.max_repair_rounds ?? 3,
      session_id: than.session_id ?? null,
    }),
  });

  if (!kq.ok) {
    // 422 mang dữ liệu có cấu trúc (`chan_doan`, `so_luot_da_sua`, `trace_id`),
    // không phải một thông báo lỗi. Chuyển tiếp NGUYÊN VẸN: ép nó về `{detail}`
    // là vứt đúng những trường UI cần để nói cho người dùng biết sai ở đâu.
    if (kq.status === 422 && kq.body) {
      return Response.json(kq.body as PoemKhongDat, { status: 422 });
    }
    return Response.json({ detail: kq.detail }, { status: kq.status });
  }
  return Response.json(kq.data);
}
