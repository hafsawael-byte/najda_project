import streamlit as st
import pandas as pd
from datetime import datetime
import pathlib

# =========================
# Google Sheet
# =========================
SHEET_ID = "16BppQGDtoAKSelaxaZfhVgdpR7Q4cDj23ep3YO9bXU"

SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
)

BASE = pathlib.Path(__file__).parent

st.set_page_config(
    page_title="Najda - مبادرة الطالبة حفصة وائل",
    layout="wide"
)

# =========================
# Banner
# =========================
bp = BASE / "banner_final.jpg"

if bp.exists():
    st.image(str(bp), use_container_width=True)

st.markdown(
    """
    <div style='background:#0A6E2F;
                color:white;
                padding:12px;
                text-align:center;
                border-radius:10px;'>
        <b>رؤية 2030 - #بترشيدنا_تدوم_نعمتنا</b><br>
        الابتدائية العاشرة بينبع البحر - مبادرة الطالبة حفصة وائل
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Data
# =========================
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

class_map = {
    "Grade1": "أول ابتدائي",
    "Grade2": "ثاني ابتدائي",
    "Grade3": "ثالث ابتدائي",
    "Grade4": "رابع ابتدائي",
    "Grade5": "خامس ابتدائي",
    "Grade6": "سادس ابتدائي",
    "Grade1M": "أول متوسط",
    "Grade2M": "ثاني متوسط",
    "Grade3M": "ثالث متوسط"
}

# =========================
# Load Data
# =========================
def load_from_gsheet():
    try:
        df = pd.read_csv(SHEET_CSV_URL)

        if df.empty or "cls" not in df.columns:
            return pd.DataFrame(
                columns=["cls", "save", "dt", "std", "activity"]
            )

        df["dt"] = pd.to_datetime(
            df["dt"],
            errors="coerce"
        ).dt.date

        return df

    except Exception:
        return pd.DataFrame(
            columns=["cls", "save", "dt", "std", "activity"]
        )

# =========================
# Save Data
# =========================
def save_to_gsheet(new_row):
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = st.secrets["gcp_service_account"]

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
 
