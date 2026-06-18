import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

def remove_white_background(image_bytes):
    """מנקה רקע לבן מהחותמת והופכת אותו לשקוף"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    out_bytes = io.BytesIO()
    img.save(out_bytes, format="PNG")
    return out_bytes.getvalue()

def sign_single_pdf(pdf_bytes, stamp_bytes, x, y, width, height):
    """חתימה על כל עמודי ה-PDF במיקום המבוקש"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        rect = fitz.Rect(x, y, x + width, y + height)
        page.insert_image(rect, stream=stamp_bytes)
    return doc.write()

# --- הגדרת שם האתר בלשונית הדפדפן ---
st.set_page_config(page_title="Automatic Signer", page_icon="📝")

# --- כותרת האפליקציה ---
st.title("Automatic Signer")
st.write("העלה חותמת ומסמכים, קבע את המידות ולחץ על הכפתור כדי לחתום.")

# אתחול משתני זיכרון במידה ואינם קיימים
if 'processed_pdfs' not in st.session_state:
    st.session_state.processed_pdfs = None
if 'success_msg' not in st.session_state:
    st.session_state.success_msg = ""

# קליטת קבצים
stamp_file = st.file_uploader("1. העלה את קובץ החותמת", type=["png", "jpg", "jpeg"])
uploaded_pdfs = st.file_uploader("2. העלה מסמכי PDF לחתימה (ניתן לבחור כמה יחד)", type=["pdf"], accept_multiple_files=True)

# תפריט צד לשינוי מידות ומיקום - עודכן לערכי ברירת המחדל החדשים
st.sidebar.header("הגדרות מיקום וגודל החותמת")
x_pos = st.sidebar.number_input("מיקום X (אופקי)", value=10)
y_pos = st.sidebar.number_input("מיקום Y (אנכי)", value=700)
stamp_width = st.sidebar.number_input("רוחב החותמת", value=200)
stamp_height = st.sidebar.number_input("גובה החותמת", value=200)

# ביצוע החתימה רק בלחיצת כפתור
if stamp_file and uploaded_pdfs:
    st.write("---")
    if st.button("החל מיקום וחתום על כל הקבצים", type="primary"):
        # איפוס מצבי קריאה של הקבצים
        stamp_file.seek(0)
        raw_stamp_bytes = stamp_file.read()
        
        with st.spinner("מעבד את החותמת ומייצר מסמכים חתומים..."):
            # הפיכת החותמת לשקופה
            processed_stamp_bytes = remove_white_background(raw_stamp_bytes)
            
            signed_output = []
            # ריצה על כל הקבצים שהועלו
            for pdf_file in uploaded_pdfs:
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
                
                # הפעלת פונקציית החתימה עם הפרמטרים מהסרגל הצידי
                signed_pdf = sign_single_pdf(
                    pdf_bytes, 
                    processed_stamp_bytes, 
                    x_pos, 
                    y_pos, 
                    stamp_width, 
                    stamp_height
                )
                # שמירה זמנית בתוך רשימה
                signed_output.append({"name": pdf_file.name, "bytes": signed_pdf})
            
            # שמירה בזיכרון של Streamlit כדי שהמידע לא יאבד במעברים
            st.session_state.processed_pdfs = signed_output
            st.session_state.success_msg = f"✅ כל המסמכים נחתמו בהצלחה (מיקום: {x_pos}, {y_pos} | גודל: {stamp_width}x{stamp_height})"

    # הצגת כפתורי ההורדה במידה ויש קבצים מוכנים בזיכרון
    if st.session_state.processed_pdfs:
        st.success(st.session_state.success_msg)
        st.write("### קבצים מוכנים להורדה:")
        
        for item in st.session_state.processed_pdfs:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📄 {item['name']}")
            with col2:
                st.download_button(
                    label="הורד קובץ חתום",
                    data=item['bytes'],
                    file_name=f"signed_{item['name']}",
                    mime="application/pdf",
                    key=f"dl_{item['name']}"  # מפתח ייחודי למניעת התנגשויות
                )

# --- חתימת יוצר בתחתית העמוד ---
st.markdown("<br><br><br><div style='text-align: center; color: gray; font-size: 14px;'>made by roy pivonia</div>", unsafe_allow_html=True)
