/**
 * Đối chiếu `types/api.ts` với `/openapi.json` của backend.
 *
 * Script này KHÔNG sinh file tự động — nó KIỂM TRA. Lý do: sinh tự động sẽ ghi
 * đè các chú thích giải thích vì sao từng trường tồn tại (`da_chay === false`
 * nghĩa là chưa kiểm, không phải đã đạt), và chính những chú thích đó là thứ
 * ngăn người đọc hiểu ngược dữ liệu.
 *
 * Chạy: node scripts/gen-types.mjs
 */

const URL_BACKEND = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const CAN_CO = {
  ModelInfo: ["ten", "provider", "tier", "context_window", "max_output_tokens"],
  Conversation: ["conversation_id", "tieu_de", "model", "tao_luc", "cap_nhat_luc", "so_tin_nhan"],
  ConversationDetail: ["tin_nhan"],
  PoemResponse: [
    "poem", "dat", "thuoc_the", "dat_luat", "dat_chat_luong", "so_dong", "so_kho",
    "so_luot_sua", "bang_chung_bay_tang", "chat_luong", "quyet_dinh_hitl", "trace_id",
  ],
  CanLamRo: ["can_lam_ro", "ca", "cau_hoi", "ly_do", "truong_thieu", "trace_id"],
  PoemKhongDat: ["ma_the", "so_luot_da_sua", "chan_doan", "trace_id"],
};

const res = await fetch(`${URL_BACKEND}/openapi.json`).catch(() => null);
if (!res?.ok) {
  console.error(`✗ Không đọc được ${URL_BACKEND}/openapi.json — backend đã chạy chưa?`);
  process.exit(1);
}

const spec = await res.json();
const schemas = spec.components?.schemas ?? {};
let lech = 0;

for (const [ten, truong] of Object.entries(CAN_CO)) {
  const s = schemas[ten];
  if (!s) {
    console.error(`✗ Backend không còn schema "${ten}"`);
    lech++;
    continue;
  }
  const co = Object.keys(s.properties ?? {});
  const thieu = truong.filter((t) => !co.includes(t));
  if (thieu.length) {
    console.error(`✗ ${ten}: types/api.ts mong có ${thieu.join(", ")} — backend không có`);
    lech++;
  }
}

// Chiều ngược lại: backend THÊM trường mà frontend chưa biết.
for (const ten of Object.keys(CAN_CO)) {
  const co = Object.keys(schemas[ten]?.properties ?? {});
  const moi = co.filter((t) => !(CAN_CO[ten] ?? []).includes(t));
  if (moi.length && ten !== "ConversationDetail") {
    console.warn(`  ${ten}: backend có thêm ${moi.join(", ")} (chưa dùng ở frontend)`);
  }
}

for (const duong of ["/v1/chat", "/v1/poem", "/v1/models", "/v1/conversations"]) {
  if (!spec.paths?.[duong]) {
    console.error(`✗ Backend không còn đường ${duong}`);
    lech++;
  }
}

if (lech) {
  console.error(`\n${lech} chỗ lệch. Sửa types/api.ts cho khớp hợp đồng backend.`);
  process.exit(1);
}
console.log("✓ types/api.ts khớp với hợp đồng backend.");
