import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pathlib
import random
import pydeck as pdk

# --- إعدادات جوجل شيت ---
# حطي ID الشيت بتاعك هنا (اللي عملتيه najda_data)
SHEET_ID = "16BppQGDtoAKSelaxaZfhVgdpR7Q4cDj23ep3YO9bXU" 
# حاولي تغيري عنوان الشيت في جوجل شيت نفسه ليكون كده بالظبط
# cls | save | dt | std | activity
# عشان الكود القديم يشتغل

SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

BASE = pathlib.Path(__file__).parent
st.set_page_config(page_title="Najda - مبادرة الطالبة حفصة وائل", layout="wide")

bp = BASE / "banner_final.jpg"
if bp.exists():
    st.image(str(bp), use_container_width=True)

st.markdown("<div style='background:#0A6E2F; color:white; padding:12px; text-align:center; border-radius:10px;'><b>رؤية 2030 - #بترشيدنا_تدوم_نعمتنا</b><br>الابتدائية العاشرة بينبع البحر - مبادرة الطالبة حفصة وائل</div>", unsafe_allow_html=True)

activities = {
    "close_taps": "إغلاق الصنابير بعد الاستخدام",
    "fix_leak": "إصلاح تسريب مياه",
    "awareness": "حملة توعية داخل الفصل",
    "bottles": "استخدام قارورات قابلة لإعادة التعبئة",
    "garden": "تقليل سقي الحديقة",
    "wudu": "ترشيد مياه الوضوء",
    "clean": "تنظيف بدون هدر",
    "report": "الإبلاغ عن هدر"
}
class_map = {"Grade1":"اول ابتدائي","Grade2":"ثاني ابتدائي","Grade3":"ثالث ابتدائي","Grade4":"رابع ابتدائي","Grade5":"خامس ابتدائي","Grade6":"سادس ابتدائي","Grade1M":"اول متوسط","Grade2M":"ثاني متوسط","Grade3M":"ثالث متوسط"}

# --- دوال جوجل شيت ---
def load_from_gsheet():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # لو الشيت فاضي او فيه عناوين عربي قديمة نحوله
        if df.empty or "cls" not in df.columns:
            return pd.DataFrame(columns=["cls","save","dt","std","activity"])
        df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
        return df
    except Exception as e:
        st.warning(f"مش قادر اقرأ من الشيت: {e}")
        return pd.DataFrame(columns=["cls","save","dt","std","activity"])

def save_to_gsheet(new_row):
    try:
        # نحاول الكتابة المباشرة لو فيه مفتاح الخدمة
        import gspread
        from google.oauth2.service_account import Credentials
        
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row([new_row["cls"], new_row["save"], str(new_row["dt"]), new_row["std"], new_row["activity"]])
        return True
    except Exception as e:
        # لو مفيش مفتاح، هنقول للطالبة تضيف يدوي مؤقتا
        st.error(f"للكتابة التلقائية لازم نضيف مفتاح في Streamlit Secrets. الخطأ: {e}")
        st.info("مؤقتا: روحي للشيت واكتبي البيانات يدوي في آخر صف")
        return False

def get_risk_level(s):
    if s >= 150: return "آمن", "#2ECC71", "green"
    elif s >= 70: return "متوسط", "#F39C12", "yellow"
    else: return "خطر", "#E74C3C", "red"

# تحميل البيانات
if 'data' not in st.session_state:
    st.session_state.data = load_from_gsheet()

with st.sidebar:
    st.header("تسجيل نشاط حقيقي")
    cls_en = st.selectbox("الفصل", list(class_map.keys()), format_func=lambda x: class_map[x])
    act_en = st.selectbox("نوع النشاط", list(activities.keys()), format_func=lambda x: activities[x])
    save = st.number_input("التوفير لتر", value=54, min_value=1)
    std = st.number_input("عدد الطالبات", value=25, min_value=1)
    
    label, color, _ = get_risk_level(save)
   st.markdown(f'<div style="background:{color}; color:white; padding:10px; border-radius:8px; text-align:center; padding:16px;">{label} - {save} لتر</div>', unsafe_allow_html=True)
