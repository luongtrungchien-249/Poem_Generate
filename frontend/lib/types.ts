import type { CanLamRo, PoemKhongDat, PoemResponse } from "@/types/api";

/**
 * §37 — VÒNG ĐỜI TIN NHẮN.
 *
 * Tài liệu gốc có 6 trạng thái: IDLE · SUBMITTING · STREAMING · COMPLETED ·
 * ERROR · STOPPED. Backend thật phát ra thêm BỐN trạng thái nữa, và cả bốn đều
 * KHÔNG phải lỗi — nếu UI không dựng sẵn chỗ cho chúng thì mỗi cái sẽ hiện ra
 * như một sự cố đỏ, trong khi hệ thống đang làm đúng việc của nó.
 */
export type TrangThaiTinNhan =
  | "dang_gui"
  | "dang_chay"
  | "xong"
  | "da_dung"
  | "loi"
  /** Chưa đủ thông tin → hệ thống hỏi lại. HTTP 200, không phải lỗi. */
  | "hoi_lai"
  /** Trượt kiểm luật → KHÔNG trả bài. HTTP 422. */
  | "khong_dat"
  /** Chủ đề bị đánh dấu REVIEW → đã nhận, chờ người duyệt. */
  | "cho_duyet"
  /** Rào chắn chặn GIỮA luồng, sau khi chữ đã hiện ra. */
  | "bi_chan";

export type VaiTro = "user" | "assistant";

export interface TinNhan {
  id: string;
  vai_tro: VaiTro;
  /** Văn bản đang hiện. Với `bi_chan` thì đã bị xoá về rỗng — xem `useChat`. */
  noi_dung: string;
  trang_thai: TrangThaiTinNhan;
  /** Có thì hiện ở chân thông báo lỗi để đối chiếu log. */
  trace_id?: string;
  loi?: string;
  /** Chỉ có ở tin nhắn thơ. */
  tho?: PoemResponse;
  hoi_lai?: CanLamRo;
  khong_dat?: PoemKhongDat;
  /** Tiến trình sinh thơ theo khổ — §30.4. */
  tien_trinh?: BuocTienTrinh[];
  /** Yêu cầu gốc, để nút "thử lại" gửi lại đúng thứ đã gửi. */
  yeu_cau_goc?: string;

  /**
   * Thời gian một lượt, đo Ở PHÍA CLIENT (giây).
   *
   * Đây là thứ NGƯỜI DÙNG thật sự chờ: nó gồm cả đường truyền và thời gian BFF
   * chuyển tiếp, không chỉ thời gian backend xử lý. Số của backend luôn nhỏ hơn
   * và không trả lời được câu "sao lâu thế".
   *
   * Ghi cho MỌI kết cục, kể cả hỏi lại, không đạt và lỗi — một lượt thất bại sau
   * 90 giây là thông tin đáng giá hơn hẳn một lượt thành công sau 3 giây.
   */
  giay?: number;

  /**
   * Thời gian tới chữ ĐẦU TIÊN (giây), chỉ có ở luồng chat có stream.
   *
   * Tách khỏi `giay` vì hai số đo hai cảm nhận khác nhau: chữ đầu quyết định
   * "hệ thống có treo không", tổng thời gian quyết định "phải chờ bao lâu".
   */
  giay_chu_dau?: number;
}

export interface BuocTienTrinh {
  nhan: string;
  trang_thai: "xong" | "dang_chay" | "cho";
}

export type CheDo = "chat" | "tho";
