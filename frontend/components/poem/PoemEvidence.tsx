"use client";

import { useState } from "react";
import { Check, ChevronDown, CircleDashed, Minus, X } from "lucide-react";
import type { PoemResponse } from "@/types/api";
import type { BuocTienTrinh } from "@/lib/types";
import { cx } from "@/lib/utils";

/**
 * §30.4 — TIẾN TRÌNH, KHÔNG PHẢI NỘI DUNG.
 *
 * Đây là thứ thay cho con trỏ nhấp nháy của §17 trong luồng thơ. Người dùng thấy
 * hệ thống đang chạy nhưng không thấy chữ nào, cho tới khi cả bài qua kiểm.
 */
export function TienTrinhTho({ buoc }: { buoc: BuocTienTrinh[] }) {
  return (
    <ul className="anim-fade space-y-2" aria-live="polite">
      {buoc.map((b) => (
        <li key={b.nhan} className="flex items-center gap-2.5 text-[14px]">
          {b.trang_thai === "xong" ? (
            <Check size={15} style={{ color: "var(--color-success)" }} aria-hidden />
          ) : b.trang_thai === "dang_chay" ? (
            <CircleDashed
              size={15}
              className="anim-pulse"
              style={{ color: "var(--color-pink-600)" }}
              aria-hidden
            />
          ) : (
            <Minus size={15} style={{ color: "var(--color-text-muted)" }} aria-hidden />
          )}
          <span
            style={{
              color:
                b.trang_thai === "cho"
                  ? "var(--color-text-muted)"
                  : "var(--color-text)",
            }}
          >
            {b.nhan}
          </span>
          {/* Nhãn chữ, không chỉ màu và biểu tượng — §29. */}
          {b.trang_thai === "dang_chay" && (
            <span className="text-[12px]" style={{ color: "var(--color-text-muted)" }}>
              đang chạy…
            </span>
          )}
        </li>
      ))}
      <li className="pt-1 text-[12px]" style={{ color: "var(--color-text-muted)" }}>
        Mỗi khổ được sinh nhiều bản rồi chọn bản đúng luật, nên bước này lâu hơn một
        lượt trò chuyện thường.
      </li>
    </ul>
  );
}

/**
 * Hai cờ, hiện TÁCH NHAU vì hệ quả của chúng khác hẳn nhau:
 *
 *   `dat_luat`       ràng buộc cứng — trượt thì không có bài để hiện
 *   `dat_chat_luong` thang đo của dự án — trượt vẫn trả bài, kèm ghi chú
 *
 * Gộp thành một dấu tích duy nhất sẽ khiến "đúng luật nhưng chất lượng thấp"
 * trông giống hệt "không đúng luật".
 */
export function HaiCo({ tho }: { tho: PoemResponse }) {
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2">
      <Co dat={tho.dat_luat} nhan={tho.dat_luat ? "Đúng luật" : "Sai luật"} manh />
      <Co
        dat={tho.dat_chat_luong}
        nhan={tho.dat_chat_luong ? "Đạt chất lượng" : "Chất lượng chưa đạt"}
      />
      <span className="text-[12px]" style={{ color: "var(--color-text-muted)" }}>
        {tho.so_dong} dòng · {tho.so_kho} khổ
        {tho.so_luot_sua > 0 && ` · sửa ${tho.so_luot_sua} lượt`}
      </span>
    </div>
  );
}

function Co({ dat, nhan, manh = false }: { dat: boolean; nhan: string; manh?: boolean }) {
  const mau = dat ? "var(--color-success)" : "var(--color-warning)";
  return (
    <span
      className={cx(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12px]",
        manh && "font-semibold",
      )}
      style={{ borderColor: mau, color: mau }}
    >
      {dat ? <Check size={13} aria-hidden /> : <X size={13} aria-hidden />}
      {nhan}
    </span>
  );
}

/**
 * Biên bản bảy tầng, mặc định GẬP LẠI.
 *
 * `da_chay === false` nghĩa là tầng CHƯA ĐƯỢC KIỂM vì một tầng trước đã chặn —
 * không phải "đã kiểm và đạt". Vẽ dấu tích xanh cho nó là nói dối về mức độ đã
 * kiểm, nên nó có biểu tượng riêng và chữ "chưa kiểm".
 */
export function BienBanBayTang({ tho }: { tho: PoemResponse }) {
  const [mo, datMo] = useState(false);
  const daChay = tho.bang_chung_bay_tang.filter((t) => t.da_chay).length;

  return (
    <div className="mt-3">
      <button
        onClick={() => datMo(!mo)}
        aria-expanded={mo}
        className="inline-flex items-center gap-1.5 text-[13px] transition-colors"
        style={{ color: "var(--color-text-secondary)" }}
      >
        <ChevronDown
          size={14}
          aria-hidden
          style={{ transform: mo ? "rotate(0deg)" : "rotate(-90deg)", transition: "transform 150ms" }}
        />
        Biên bản kiểm định — {daChay}/{tho.bang_chung_bay_tang.length} tầng đã kiểm
      </button>

      {mo && (
        <div className="anim-fade mt-2 space-y-1.5">
          {tho.bang_chung_bay_tang.map((t) => (
            <div
              key={t.tang}
              className="rounded-[10px] border p-2.5 text-[13px]"
              style={{ borderColor: "var(--color-divider)" }}
            >
              <div className="flex items-start gap-2">
                {!t.da_chay ? (
                  <Minus size={14} className="mt-0.5 shrink-0" style={{ color: "var(--color-text-muted)" }} aria-hidden />
                ) : t.dat ? (
                  <Check size={14} className="mt-0.5 shrink-0" style={{ color: "var(--color-success)" }} aria-hidden />
                ) : (
                  <X size={14} className="mt-0.5 shrink-0" style={{ color: "var(--color-error)" }} aria-hidden />
                )}
                <div className="min-w-0">
                  <span className="font-medium">
                    Tầng {t.tang} · {t.ten}
                  </span>
                  <span className="ml-2 text-[12px]" style={{ color: "var(--color-text-muted)" }}>
                    {!t.da_chay ? "chưa kiểm" : t.dat ? "đạt" : "không đạt"}
                    {t.ma_luat.length > 0 && ` · ${t.ma_luat.join(", ")}`}
                  </span>
                  {t.bang_chung && (
                    <p className="mt-1 break-words" style={{ color: "var(--color-text-secondary)" }}>
                      {t.bang_chung}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}

          {tho.chat_luong.length > 0 && (
            <div className="pt-1">
              <p className="mb-1.5 text-[12px] font-medium" style={{ color: "var(--color-text-secondary)" }}>
                Chất lượng
              </p>
              <div className="flex flex-wrap gap-1.5">
                {tho.chat_luong.map((c) => (
                  <span
                    key={c.ma}
                    title={c.bang_chung}
                    className="rounded-full border px-2 py-0.5 text-[11.5px]"
                    style={{
                      borderColor: "var(--color-divider)",
                      // `do_duoc === false` → `dat` vô nghĩa, nên không tô màu phán quyết.
                      color: !c.do_duoc
                        ? "var(--color-text-muted)"
                        : c.dat
                          ? "var(--color-success)"
                          : "var(--color-warning)",
                    }}
                  >
                    {c.ma} {!c.do_duoc ? "· không đo được" : c.dat ? "· đạt" : "· chưa đạt"}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
