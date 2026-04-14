import streamlit as st
import fitz  # PyMuPDF
import io

def sign_pdf(pdf_bytes, sig_bytes, sig_width, sig_height, offset_x, offset_y):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    try:
        sig_doc = fitz.open(stream=sig_bytes, filetype="pdf")
        page_sig = sig_doc[0]
        pix = page_sig.get_pixmap(alpha=True)
        sig_img_for_fitz = pix.tobytes()
    except:
        sig_img_for_fitz = sig_bytes

    for page in doc:
        page_rect = page.rect
        x1 = offset_x
        y1 = page_rect.height - sig_height - offset_y
        x2 = x1 + sig_width
        y2 = y1 + sig_height
        
        rect = fitz.Rect(x1, y1, x2, y2)
        
        # כאן השינוי המרכזי: הוספת overlay=True ושימוש ב-mask אם צריך
        # בגרסאות חדשות של PyMuPDF, התמונה משתלבת טוב יותר עם overlay
        page.insert_image(rect, stream=sig_img_for_fitz, overlay=True)
        
    return doc.write()

# --- ממשק המשתמש ---
st.set_page_config(page_title="חתמנית מקצועית", layout="centered")

st.title("✍️ חתמנית PDF שקופה")
st.write("החתימה תוטמע על גבי הטקסט בצד שמאל למטה.")

col1, col2 = st.columns(2)
with col1:
    doc_file = st.file_uploader("1. מסמך PDF", type="pdf")
with col2:
    sig_file = st.file_uploader("2. חתימה (עדיף PNG שקוף)", type=["pdf", "png", "jpg"])

with st.expander("⚙️ כיוונון מיקום וגודל"):
    sig_width = st.slider("רוחב חתימה", 20, 250, 100)
    sig_height = st.slider("גובה חתימה", 10, 200, 50)
    offset_x = st.number_input("מרחק מהשמאל", value=50)
    offset_y = st.number_input("מרחק מהתחתית", value=50)

if st.button("🚀 צור מסמך חתום", use_container_width=True):
    if doc_file and sig_file:
        try:
            with st.spinner("מטמיע חתימה..."):
                output = sign_pdf(doc_file.read(), sig_file.read(), sig_width, sig_height, offset_x, offset_y)
            st.success("המסמך חתום!")
            st.download_button("📥 הורד PDF חתום", output, file_name=f"signed_{doc_file.name}")
        except Exception as e:
            st.error(f"שגיאה: {e}")
