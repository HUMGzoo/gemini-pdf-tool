# Tên tệp: pdf_streamlit_app.py

import streamlit as st
import google.generativeai as genai
import os
import tempfile

def get_gemini_response(api_key, pdf_file_path, prompt):
    """
    Hàm xử lý logic cốt lõi với Gemini API.
    """
    try:
        genai.configure(api_key=api_key)
        
        # Tải tệp lên
        uploaded_file = genai.upload_file(path=pdf_file_path)
        
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        # Gửi yêu cầu
        response = model.generate_content([prompt, uploaded_file])
        
        # Xóa tệp đã tải lên
        genai.delete_file(uploaded_file.name)
        
        return response.text
    except Exception as e:
        # Cung cấp thông báo lỗi rõ ràng hơn
        if "API key is invalid" in str(e):
             return "Lỗi: Khóa API không hợp lệ. Vui lòng kiểm tra lại."
        return f"Đã xảy ra lỗi: {e}"

# --- Cấu hình giao diện Streamlit ---
st.set_page_config(page_title="Công cụ PDF với Gemini", layout="wide")

st.title("⚙️ Công cụ trích xuất nội dung PDF với Gemini AI")
st.markdown("Tải lên một tệp PDF và yêu cầu Gemini thực hiện một tác vụ, ví dụ như tóm tắt hoặc trích xuất thông tin.")

# --- Khu vực nhập liệu ở cột bên ---
with st.sidebar:
    st.header("Cấu hình")
    # Thay vì yêu cầu người dùng nhập API Key, chúng ta sẽ dùng tính năng Secrets của Streamlit
    # api_key = st.text_input("Nhập khóa API Gemini của bạn:", type="password")
    st.markdown("Ứng dụng này sử dụng Khóa API Gemini được cấu hình sẵn.")
    
    uploaded_pdf = st.file_uploader("1. Chọn tệp PDF của bạn", type="pdf")
    
    prompt = st.text_area("2. Nhập câu lệnh của bạn:", 
                          height=150, 
                          value="Tóm tắt tài liệu này trong 5 gạch đầu dòng. Liệt kê những nhân vật hoặc tổ chức quan trọng được đề cập.")

    submit_button = st.button("Bắt đầu xử lý")
    
# Lấy API Key từ Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# --- Khu vực hiển thị kết quả ---
if submit_button:
    if not api_key:
        st.error("Lỗi cấu hình: Không tìm thấy GEMINI_API_KEY. Quản trị viên cần thiết lập nó trong phần Secrets của Streamlit.")
    elif uploaded_pdf is None:
        st.error("Vui lòng tải lên một tệp PDF.")
    elif not prompt:
        st.error("Vui lòng nhập một câu lệnh.")
    else:
        with st.spinner("Đang xử lý... Quá trình này có thể mất một lúc tùy thuộc vào kích thước tệp."):
            # Lưu tệp tải lên vào một vị trí tạm thời để API có thể đọc
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_pdf.getvalue())
                tmp_file_path = tmp_file.name

            # Gọi hàm xử lý
            response = get_gemini_response(api_key, tmp_file_path, prompt)
            
            # Xóa tệp tạm
            os.remove(tmp_file_path)

            st.subheader("Kết quả từ Gemini:")
            st.markdown(response, unsafe_allow_html=True)
else:
    st.info("Vui lòng nhập thông tin vào thanh bên và nhấn 'Bắt đầu xử lý'.")