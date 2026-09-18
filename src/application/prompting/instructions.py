"""Layer 2: Task instructions.
Constants per specific task type.
"""

RAG_INSTRUCTION: str = """Quy tắc trả lời dựa trên tài liệu:
1. Đọc kỹ phần [CONTEXT] được cung cấp trong lượt hội thoại.
2. Trả lời trực tiếp câu hỏi dựa vào các sự kiện có trong [CONTEXT].
3. Gắn kèm ID tài liệu trong ngoặc vuông sau mỗi luận điểm quan trọng.
4. Nếu tài liệu không đủ dữ kiện, hãy nói rõ và không suy đoán thêm.
"""

REACT_INSTRUCTION: str = """Quy tắc thực thi công cụ (ReAct):
1. Phân tích xem có cần gọi công cụ bên ngoài để tra cứu dữ liệu không.
2. Nếu cần gọi công cụ, trả về tool_call tương ứng với tham số chuẩn xác.
3. Khi đã có đủ thông tin từ công cụ, tổng hợp câu trả lời cuối cùng cho người dùng.
"""
