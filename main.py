import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

def remove_white_background(image_bytes):
    """
    פונקציה שמקבלת את קובץ החותמת, מזהה פיקסלים לבנים
    או קרובים ללבן, והופכת אותם לשקופים לחלוטין.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        # בדיקה האם הפיקסל לבן או קרוב מאוד ללבן (ערכי RGB גבוהים מ-240)
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            # הפיכת הפיקסל לשקוף (ערך ה-Alpha נקבע ל-0)
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    out_bytes = io.BytesIO()
    img.save(out_bytes, format="PNG")
    return out_bytes.getvalue()

def sign_single_pdf(pdf_bytes, stamp_bytes, x, y, width, height):
    """
    פונקציה החותמת על כל העמודים של מסמך PDF בודד.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page in doc:
        # הגדרת מלבן המיקום שבו תושתל החותמת
        rect = fitz.Rect(x, y, x + width, y + height)
        # הכנסת החותמת השקופה
        page.insert_image(rect, stream=stamp_bytes)
        
    return doc.write()

# --- ממשק האפליקציה ב-Streamlit ---
st.title("מערכת חתימה אוטומטית ומבוזרת")
st.write("העלה חותמת ומספר קבצים כדי לחתום על כולם בבת אחת במיקום קבוע.")

# 1. העלאת קובץ החותמת
stamp_file = st.file_uploader("העלה את קובץ החותמת (מומלץ פורמט PNG)", type=["png", "jpg", "jpeg"])

# 2. העלאת מספר מסמכים במקביל
uploaded_pdfs = st.file_uploader(
    "העלה מסמכי PDF לחתימה (ניתן לבחור מספר קבצים יחד)", 
    type=["pdf"], 
    accept_multiple_files=True
)

# הגדרות מיקום דינמיות לחותמת (ניתן לשנות ערכים אלו לפי הצורך)
st.sidebar.header("הגדרות מיקום החותמת")
x_pos = st.sidebar.number_input("מיקום X (אופקי)", value=450)
y_pos = st.sidebar.number_input("מיקום Y (אנכי)", value=700)
stamp_width = st.sidebar.number_input("רוחב החותמת", value=100)
stamp_height = st.sidebar.number_input("גובה החותמת", value=50)

if stamp_file and uploaded_pdfs:
    # קריאת החותמת מהזיכרון
    raw_stamp_bytes = stamp_file.read()
    
    # הסרת הרקע הלבן באופן אוטומטי
    with st.spinner("מעבד את החותמת לשקיפות מלאה..."):
        processed_stamp_bytes = remove_white_background(raw_stamp_bytes)
    
    st.success("החותמת מוכנה! להלן המסמכים החתומים להורדה:")
    st.write("---")
    
    # לולאה שעוברת על כל אחד מהקבצים שהועלו בנפרד
    for pdf_file in uploaded_pdfs:
        pdf_bytes = pdf_file.read()
        
        # חתימה על המסמך הנוכחי
        signed_pdf = sign_single_pdf(
            pdf_bytes, 
            processed_stamp_bytes, 
            x_pos, 
            y_pos, 
            stamp_width, 
            stamp_height
        )
        
        # יצירת שורת הורדה נפרדת עם כפתור לכל קובץ
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(f"📄 {pdf_file.name}")
        with col2:
            st.download_button(
                label="הורד קובץ חתום",
                data=signed_pdf,
                file_name=f"signed_{pdf_file.name}",
                mime="application/pdf",
                key=pdf_file.name # מפתח ייחודי לכל כפתור ברשימה
            )
