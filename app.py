import streamlit as st
import pytesseract
import numpy as np
import pymysql
import re
from PIL import Image



st.title("ATM Card Reader")


upl_img = st.file_uploader("Upload ATM card image", type=["jpg", "jpeg", "png"])

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
        'cardno': cardno.group() if cardno else None,
        'exdate': exdate.group() if exdate else None,
        'name': name
    }

if upl_img:
   
    image = Image.open(upl_img)
    img_np = np.array(image)
    text = pytesseract.image_to_string(img_np)

    st.subheader("Extracted Text")
    st.text(text)

    
    card_info = extract_card_info(text)
    
    
    st.subheader("Card Details")
    st.write(f"**Card Number:** {card_info['cardno']}")
    st.write(f"**Expiry Date:** {card_info['exdate']}")
    st.write(f"**Card Holder Name:** {card_info['name']}")

    
    if all(card_info.values()):
        
        try:
            db = pymysql.connect(host='localhost',user='root',password='root@123', database='atm_cards')
            cursor = db.cursor()

            
            #cursor.execute("CREATE TABLE card_data (id INT AUTO_INCREMENT PRIMARY KEY,card_number VARCHAR(30),expiry_date VARCHAR(10),name VARCHAR(100))")

            
            s2=("INSERT INTO card_data (card_number, expiry_date, name)VALUES (%s, %s, %s)")
            s3=(card_info['cardno'], card_info['exdate'], card_info['name'])
            cursor.execute(s2,s3)
            db.commit()
            st.success("Card data saved to database!")
            
        except Exception as e:
            st.error(f"Database error: {e}")
        finally:
            cursor.close()
            db.close()
    else:
        st.warning("Some card details could not be extracted. Please upload a clearer image.")
