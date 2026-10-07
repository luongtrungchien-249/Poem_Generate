import type { TinNhan } from "./types";
import type { KetQuaTho, PoemJob } from "@/types/api";

export function progressMessage(job: PoemJob): Partial<TinNhan> {
  const label: Record<string, string> = {
    queued: "Đang chờ xử lý", planning: "Đọc yêu cầu và lập kế hoạch",
    generating: "Sinh và chọn theo khổ", verifying: "Kiểm bảy tầng luật",
    repairing: "Sửa ứng viên chưa đạt",
  };
  const stanza = job.progress.kho ? ` · khổ ${job.progress.kho}${job.progress.tong_kho ? `/${job.progress.tong_kho}` : ""}` : "";
  return { trang_thai: "dang_chay", tien_trinh: [{ nhan: (label[job.status] ?? job.status) + stanza, trang_thai: "dang_chay" }] };
}

export function resultMessage(result: KetQuaTho): Partial<TinNhan> {
  const common = { tien_trinh: undefined, trace_id: result.data.trace_id };
  if (result.loai === "hoi_lai") return { ...common, trang_thai: "hoi_lai", hoi_lai: result.data };
  if (result.loai === "khong_dat") return { ...common, trang_thai: "khong_dat", khong_dat: result.data };
  return { ...common, trang_thai: result.data.quyet_dinh_hitl === "HUMAN_REVIEW" ? "cho_duyet" : "xong",
           noi_dung: result.data.poem, tho: result.data };
}
