import streamlit as st
import easyocr
import numpy as np
import pymysql
import re
from PIL import Image

st.set_page_config(page_title="ATM Card Reader", layout="centered")
st.title("💳 ATM Card Reader (OCR using EasyOCR)")

# ====== File Upload ======
upl_img = st.file_uploader("Upload ATM Card Image", type=["jpg", "jpeg", "png"])

# ====== Extract Card Info Function ======
def extract_card_info(text):
    cardno = re.search(r'\b(?:\d[ -]*?){13,19}\b', text)
    exdate = re.search(r'(0[0-9]|1[0-2])/([0-9]{2})', text)
    name = None

    lines = text.split('\n')
    for line in lines:
        if re.match(r'[A-Z\s]{5,}', line.strip()) and not line.strip().isdigit():
            name = line.strip()
            break

    return {
        "cardno": cardno.group() if cardno else None,
        "exdate": exdate.group() if exdate else None,
        "name": name
    }

# ====== OCR + DB Logic ======
if upl_img:
    image = Image.open(upl_img)
    img_np = np.array(image)

    # OCR using EasyOCR
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img_np, detail=0)
    text = "\n".join(result)

    st.subheader("🧾 Extracted Text")
    st.text(text)

    # extract info
    card_info = extract_card_info(text)

    st.subheader("📌 Card Details")
    st.write(f"**Card Number:** {card_info['cardno']}")
    st.write(f"**Expiry Date:** {card_info['exdate']}")
    st.write(f"**Card Holder Name:** {card_info['name']}")

    # Save to DB if all fields available
    if all(card_info.values()):
        try:
            db = pymysql.connect(
                host='localhost',      # ⚠ Must change when deployed online
                user='root',
                password='root@123',
                database='atm_cards'
            )
            cursor = db.cursor()

            sql = "INSERT INTO card_data (card_number, expiry_date, name) VALUES (%s, %s, %s)"
            values = (card_info["cardno"], card_info["exdate"], card_info["name"])

            cursor.execute(sql, values)
            db.commit()

            st.success("🎉 Data saved in MySQL database!")

        except Exception as e:
            st.error(f"⚠ Database Error: {e}")
        finally:
            cursor.close()
            db.close()
    else:
        st.warning("⚠ Could not extract all fields. Try uploading a clearer ATM card image.")
