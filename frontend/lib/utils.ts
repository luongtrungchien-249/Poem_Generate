export function cx(...phan: (string | false | null | undefined)[]): string {
  return phan.filter(Boolean).join(" ");
}

export function maNgauNhien(): string {
  return Math.random().toString(36).slice(2, 10);
}

/** "Hôm nay · 14:03" — mốc thời gian tương đối, dễ đọc hơn ISO. */
export function thoiGianGon(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const nay = new Date();
  const cungNgay = d.toDateString() === nay.toDateString();
  const gio = d.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
  if (cungNgay) return `Hôm nay · ${gio}`;
  const homQua = new Date(nay);
  homQua.setDate(nay.getDate() - 1);
  if (d.toDateString() === homQua.toDateString()) return `Hôm qua · ${gio}`;
  return `${d.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" })} · ${gio}`;
}

/** Tiêu đề hội thoại suy từ câu đầu tiên, vì backend không tự đặt tên. */
export function tieuDeTuCau(cau: string): string {
  const s = cau.trim().replace(/\s+/g, " ");
  return s.length <= 42 ? s : `${s.slice(0, 42)}…`;
}

/**
 * Thời lượng cho người đọc.
 *
 * Dưới 10 giây thì một chữ số thập phân là đủ phân biệt; trên 10 giây thì phần
 * thập phân chỉ là nhiễu. Quá 60 giây đổi sang phút, vì "92,4 giây" buộc người
 * đọc phải tự chia.
 *
 * Dùng dấu phẩy thập phân theo quy ước tiếng Việt.
 */
export function thoiLuong(giay: number): string {
  if (giay < 1) return `${Math.round(giay * 1000)} ms`;
  if (giay < 10) return `${giay.toFixed(1).replace(".", ",")} giây`;
  if (giay < 60) return `${Math.round(giay)} giây`;
  const phut = Math.floor(giay / 60);
  const du = Math.round(giay % 60);
  return du ? `${phut} phút ${du} giây` : `${phut} phút`;
}
