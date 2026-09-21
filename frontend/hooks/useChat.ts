"use client";

import { useCallback } from "react";
import { useChatStore } from "@/stores/chatStore";
import { useUiStore } from "@/stores/uiStore";
import { docLuongSSE } from "./useStreaming";
import { sinhTho, LoiApi } from "@/services/api";
import { maNgauNhien } from "@/lib/utils";
import type { BuocTienTrinh, TinNhan } from "@/lib/types";

/**
 * Điều phối một lượt gửi. HAI LUỒNG KHÁC HẲN NHAU:
 *
 *   chế độ "chat" → SSE, chữ chảy dần ra màn hình
 *   chế độ "tho"  → KHÔNG stream nội dung, chỉ stream TIẾN TRÌNH
 *
 * Vì sao luồng thơ không stream từng chữ (trái với §17 của tài liệu): không thể
 * phát dần một bài thơ rồi mới phát hiện nó sai luật — chữ đã ra rồi, và người
 * dùng đã đọc. Hệ thống chỉ trả bài SAU khi cả bài qua bảy tầng, nên thứ duy
 * nhất có thể hiện trong lúc chờ là hệ thống đang làm tới đâu.
 */
export function useChat(sessionId: string | null) {
  const {
    themTinNhan, capNhat, noiChu, datTrangThai, datDangChay, xoaTuId,
    datMachTho, datGanTho, datTruongDangHoi,
  } = useChatStore();
  const cheDo = useUiStore((s) => s.cheDo);

  const dung = useCallback(() => {
    const { huy } = useChatStore.getState();
    huy?.abort();
    datDangChay(false, null);
  }, [datDangChay]);

  const gui = useCallback(
    /**
     * @param dat  Giá trị người dùng chọn từ một nút bấm, nên biết CHẮC CHẮN là
     *             trường nào mang giá trị nào — khác với chữ tự do phải nhờ
     *             backend trích xuất.
     */
    async (noiDung: string, dat?: { so_dong?: number; chu_de?: string }) => {
      const van = noiDung.trim();
      if (!van || useChatStore.getState().dangChay) return;

      const idNguoiDung = maNgauNhien();
      const idTraLoi = maNgauNhien();

      themTinNhan({
        id: idNguoiDung,
        vai_tro: "user",
        noi_dung: van,
        trang_thai: "xong",
      });

      const khung: TinNhan = {
        id: idTraLoi,
        vai_tro: "assistant",
        noi_dung: "",
        trang_thai: "dang_gui",
        yeu_cau_goc: van,
      };
      themTinNhan(khung);

      const huy = new AbortController();
      datDangChay(true, huy);

      // `performance.now()` chứ không phải `Date.now()`: đồng hồ hệ thống có thể
      // bị chỉnh (đồng bộ NTP, đổi múi giờ) ngay giữa một lượt đang chạy, và khi
      // đó hiệu số cho ra số âm hoặc nhảy vọt. `performance.now()` đơn điệu tăng.
      const batDau = performance.now();
      const daTroi = () => (performance.now() - batDau) / 1000;

      // ── Luồng thơ ────────────────────────────────────────────────────────
      if (cheDo === "tho") {
        const buoc: BuocTienTrinh[] = [
          { nhan: "Đọc yêu cầu", trang_thai: "dang_chay" },
          { nhan: "Kiểm đủ thông tin", trang_thai: "cho" },
          { nhan: "Sinh và chọn theo khổ", trang_thai: "cho" },
          { nhan: "Kiểm bảy tầng luật", trang_thai: "cho" },
        ];
        // GHÉP với những gì người dùng đã nói ở các lượt hỏi lại trước đó.
        //
        // `/v1/poem` không giữ trạng thái — nó dựng lại yêu cầu từ đúng chuỗi
        // nhận được. Gửi riêng "12 dòng" thì chủ đề nói ở lượt trước biến mất,
        // và hệ thống hỏi vòng vo mãi. Đây chính là lỗi mà dòng chữ "yêu cầu cũ
        // vẫn được giữ" trong thẻ hỏi lại đã hứa nhưng chưa làm.
        //
        // Client KHÔNG phân tích gì ở đây: tách chủ đề, số dòng, cảm xúc ra khỏi
        // câu nói là việc của backend. Nó chỉ không đánh rơi thứ đã được nói.
        const s0 = useChatStore.getState();
        const mach = [...s0.machTho, van];
        const yeuCauDayDu = mach.join(". ");

        // Câu trả lời này thuộc về trường nào?
        //
        //  - Bấm nút  → biết chắc, dùng thẳng giá trị.
        //  - Gõ chữ   → chỉ gán được khi lượt hỏi vừa rồi nêu rõ đang thiếu
        //               `chu_de`; khi đó cả câu là chủ đề.
        //
        // Không gán bừa: đoán sai trường còn tệ hơn để backend hỏi thêm một lượt.
        const gan = { ...s0.ganTho, ...dat };
        if (!dat && s0.truongDangHoi.includes("chu_de") && !gan.chu_de) {
          gan.chu_de = van;
        }
        datGanTho(gan);

        capNhat(idTraLoi, {
          trang_thai: "dang_chay",
          tien_trinh: buoc,
          // Nút "Thử lại" phải gửi lại CẢ mạch, không chỉ câu cuối — nếu không
          // thì thử lại một yêu cầu đã qua nhiều lượt hỏi đáp sẽ mất hết ngữ cảnh.
          yeu_cau_goc: yeuCauDayDu,
        });

        // Tiến trình này là ƯỚC LƯỢNG, không phải sự kiện thật từ backend:
        // `/v1/poem` trả về một lần, không stream. Nó cho người dùng biết hệ
        // thống còn sống, và cố ý KHÔNG hứa thời gian — sinh thơ là best-of-16
        // mỗi khổ nên lâu hơn hẳn một lượt chat, và một thanh tiến trình giả sẽ
        // nói dối về điều đó.
        const nhip = setInterval(() => {
          const t = useChatStore.getState().tinNhan.find((x) => x.id === idTraLoi);
          if (!t?.tien_trinh) return;
          const i = t.tien_trinh.findIndex((b) => b.trang_thai === "dang_chay");
          if (i < 0 || i >= t.tien_trinh.length - 1) return;
          const moi = t.tien_trinh.map((b, j) =>
            j === i
              ? { ...b, trang_thai: "xong" as const }
              : j === i + 1
                ? { ...b, trang_thai: "dang_chay" as const }
                : b,
          );
          capNhat(idTraLoi, { tien_trinh: moi });
        }, 2600);

        try {
          const kq = await sinhTho({
            yeu_cau: yeuCauDayDu,
            chu_de: gan.chu_de ?? null,
            so_dong: gan.so_dong ?? null,
            session_id: sessionId,
          });
          clearInterval(nhip);

          if (kq.loai === "hoi_lai") {
            // Còn thiếu thông tin: giữ mạch, và ghi nhớ lượt này đang hỏi gì
            // để câu trả lời tới được đưa vào đúng trường.
            datMachTho(mach);
            datTruongDangHoi(kq.data.truong_thieu);
            capNhat(idTraLoi, {
              trang_thai: "hoi_lai",
              hoi_lai: kq.data,
              giay: daTroi(),
              tien_trinh: undefined,
              trace_id: kq.data.trace_id,
            });
          } else if (kq.loai === "khong_dat") {
            // Yêu cầu đã đủ thông tin (bài được sinh rồi mới trượt luật), nên
            // mạch khép lại. Giữ tiếp sẽ khiến câu hỏi SAU bị dính chủ đề cũ.
            datMachTho([]);
            datGanTho({});
            datTruongDangHoi([]);
            capNhat(idTraLoi, {
              trang_thai: "khong_dat",
              khong_dat: kq.data,
              giay: daTroi(),
              tien_trinh: undefined,
              trace_id: kq.data.trace_id,
            });
          } else {
            // `HUMAN_REVIEW` = đã có bài, nhưng cần người xem trước khi coi là
            // xong. Không phải lỗi, và cũng không phải hoàn tất.
            const choDuyet = kq.data.quyet_dinh_hitl === "HUMAN_REVIEW";
            // Đã ra bài: mạch khép lại, lượt sau là một yêu cầu mới.
            datMachTho([]);
            datGanTho({});
            datTruongDangHoi([]);
            capNhat(idTraLoi, {
              trang_thai: choDuyet ? "cho_duyet" : "xong",
              noi_dung: kq.data.poem,
              giay: daTroi(),
              tho: kq.data,
              tien_trinh: undefined,
              trace_id: kq.data.trace_id,
            });
          }
        } catch (e) {
          clearInterval(nhip);
          capNhat(idTraLoi, {
            trang_thai: "loi",
            tien_trinh: undefined,
            giay: daTroi(),
            loi: e instanceof LoiApi ? e.message : "Không sinh được bài thơ.",
          });
        } finally {
          datDangChay(false, null);
        }
        return;
      }

      // ── Luồng chat ───────────────────────────────────────────────────────
      datTrangThai(idTraLoi, "dang_chay");
      const lichSu = useChatStore
        .getState()
        .tinNhan.filter((t) => t.vai_tro === "user" || t.trang_thai === "xong")
        .map((t) => ({ role: t.vai_tro, content: t.noi_dung }))
        .filter((m) => m.content);

      let giayChuDau: number | undefined;
      await docLuongSSE(
        { messages: lichSu, stream: true, session_id: sessionId },
        huy.signal,
        {
          onDelta: (chu) => {
            // Chỉ ghi lần ĐẦU. Rào chắn giữ chữ lại trong cửa sổ đệm nên mẩu đầu
            // tiên tới muộn hơn một luồng thô — đó chính là con số đáng đo.
            if (giayChuDau === undefined) giayChuDau = daTroi();
            noiChu(idTraLoi, chu);
          },
          onBiChan: (lyDo, traceId) => {
            // THU HỒI chữ đã hiện. Giữ lại phần đã phát kèm một dòng cảnh báo là
            // phá bỏ chính lý do rào chắn tồn tại: người dùng sẽ chép phần đó đi
            // dùng, và dòng cảnh báo không đi theo.
            capNhat(idTraLoi, {
              noi_dung: "",
              trang_thai: "bi_chan",
              giay: daTroi(),
              loi: lyDo,
              trace_id: traceId,
            });
            datDangChay(false, null);
          },
          onXong: (traceId) => {
            capNhat(idTraLoi, {
              trang_thai: "xong", trace_id: traceId,
              giay: daTroi(), giay_chu_dau: giayChuDau,
            });
            datDangChay(false, null);
          },
          onLoi: (thongBao) => {
            capNhat(idTraLoi, { trang_thai: "loi", loi: thongBao, giay: daTroi() });
            datDangChay(false, null);
          },
        },
      );

      // Huỷ giữa chừng: `docLuongSSE` trả về im lặng, nên đánh dấu ở đây.
      if (huy.signal.aborted) {
        const t = useChatStore.getState().tinNhan.find((x) => x.id === idTraLoi);
        if (t && t.trang_thai === "dang_chay") {
          capNhat(idTraLoi, { trang_thai: "da_dung", giay: daTroi() });
        }
        datDangChay(false, null);
      }
    },
    [
      cheDo, sessionId, themTinNhan, capNhat, noiChu, datTrangThai, datDangChay,
      datMachTho, datGanTho, datTruongDangHoi,
    ],
  );

  /** §52 — Regenerate. Backend không có endpoint riêng: cắt bỏ câu trả lời cũ
   *  rồi gửi lại câu hỏi. Giữ lại cả hai sẽ làm lịch sử có hai câu trả lời cho
   *  một câu hỏi, và lượt sau mô hình đọc cả hai. */
  const sinhLai = useCallback(
    async (idTraLoi: string, yeuCau: string) => {
      const ds = useChatStore.getState().tinNhan;
      const i = ds.findIndex((t) => t.id === idTraLoi);
      if (i < 1) return;
      xoaTuId(ds[i - 1]!.id);
      await gui(yeuCau);
    },
    [gui, xoaTuId],
  );

  return { gui, dung, sinhLai };
}
