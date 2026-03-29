import streamlit as st
import fitz  # PyMuPDF
import io


def sign_pdf(pdf_bytes, sig_bytes, sig_width, sig_height, offset_x, offset_y):
    # פתיחת מסמך המקור מהזיכרון
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # בדיקה האם החתימה היא PDF או תמונה
    # ננסה לפתוח כ-PDF, אם נכשל נתייחס כאל תמונה
    try:
        sig_doc = fitz.open(stream=sig_bytes, filetype="pdf")
        # הופך את העמוד הראשון של ה-PDF של החתימה לתמונה (Pixmap)
        page_sig = sig_doc[0]
        pix = page_sig.get_pixmap(alpha=True)
        sig_img_for_fitz = pix.tobytes()
    except:
        # אם זו כבר תמונה (PNG/JPG)
        sig_img_for_fitz = sig_bytes

    for page in doc:
        # חישוב המיקום: צד שמאל (offset_x) למטה (גובה העמוד פחות גובה החתימה פחות offset_y)
        page_rect = page.rect
        x1 = offset_x
        y1 = page_rect.height - sig_height - offset_y
        x2 = x1 + sig_width
        y2 = y1 + sig_height

        rect = fitz.Rect(x1, y1, x2, y2)

        # הוספת החתימה
        page.insert_image(rect, stream=sig_img_for_fitz)

    # שמירה לזיכרון והחזרה
    return doc.write()


# --- ממשק המשתמש (Streamlit) ---
st.set_page_config(page_title="חתימה אוטומטית על PDF", layout="centered")

st.title("✍️ חתמנית PDF אוטומטית")
st.write("העלה מסמך וחתימה, וקבל את המסמך חתום בכל העמודים בצד שמאל למטה.")

col1, col2 = st.columns(2)

with col1:
    doc_file = st.file_uploader("1. העלה מסמך PDF", type="pdf")
with col2:
    sig_file = st.file_uploader("2. העלה חתימה (PDF/PNG/JPG)", type=["pdf", "png", "jpg"])

st.divider()

# הגדרות מתקדמות
with st.expander("⚙️ הגדרות מיקום וגודל"):
    sig_width = st.slider("רוחב חתימה", 20, 200, 80)
    sig_height = st.slider("גובה חתימה", 10, 150, 40)
    offset_x = st.number_input("מרחק מהשמאל", value=30)
    offset_y = st.number_input("מרחק מהתחתית", value=30)

if st.button("🚀 צור מסמך חתום", use_container_width=True):
    if doc_file and sig_file:
        try:
            with st.spinner("מעבד את המסמך..."):
                signed_pdf_bytes = sign_pdf(
                    doc_file.read(),
                    sig_file.read(),
                    sig_width,
                    sig_height,
                    offset_x,
                    offset_y
                )

            st.success("המסמך מוכן!")
            st.download_button(
                label="📥 הורד PDF חתום",
                data=signed_pdf_bytes,
                file_name=f"signed_{doc_file.name}",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"אופס, קרתה שגיאה: {e}")
    else:
        st.warning("נא להעלות את שני הקבצים.")

st.info("💡 טיפ: אם החתימה מסתירה טקסט, כדאי להשתמש בקובץ PNG עם רקע שקוף.")