import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pathlib
import random
import pydeck as pdk

SHEET_ID = "16BppQGDtoAKSelaxaZfhVgdpR7Q4cDj23ep3YO9bXU" 
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"

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

def load_from_gsheet():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if df.empty or "cls" not in df.columns:
            return pd.DataFrame(columns=["cls","save","dt","std","activity"])
        df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
        return df
    except Exception as e:
        return pd.DataFrame(columns=["cls","save","dt","std","activity"])

def save_to_gsheet(new_row):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row([new_row["cls"], new_row["save"], str(new_row["dt"]), new_row["std"], new_row["activity"]])
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

def get_risk_level(s):
    if s >= 150: return "آمن", "#2ECC71", "green"
    elif s >= 70: return "متوسط", "#F39C12", "yellow"
    else: return "خطر", "#E74C3C", "red"

if 'data' not in st.session_state:
    st.session_state.data = load_from_gsheet()

# ===== الشريط الجانبي =====
with st.sidebar:
    st.header("تسجيل نشاط حقيقي")
    cls_en = st.selectbox("الفصل", list(class_map.keys()), format_func=lambda x: class_map[x])
    act_en = st.selectbox("نوع النشاط", list(activities.keys()), format_func=lambda x: activities[x])
    save = st.number_input("التوفير لتر", value=55, min_value=1)
    std = st.number_input("عدد الطالبات", value=27, min_value=1)
    
    label, color, _ = get_risk_level(save)
    st.markdown(f'<div style="background:{color}; color:white; padding:10px; border-radius:8px; text-align:center; padding:16px; font-weight:bold; margin-top:10px;">مؤشر الخطر: {label}<br>{save} لتر</div>', unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 حفظ النشاط", use_container_width=True, type="primary"):
            new_row = {"cls": cls_en, "save": save, "dt": datetime.now().date(), "std": std, "activity": act_en}
            if save_to_gsheet(new_row):
                st.success("تم الحفظ!")
                st.session_state.data = load_from_gsheet()
            else:
                # حفظ محلي مؤقت لو مفيش مفتاح
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("تم الحفظ محليا")
    with col2:
        if st.button("🗑️ تصفير النشاط", use_container_width=True):
            st.session_state.data = pd.DataFrame(columns=["cls","save","dt","std","activity"])
            st.warning("تم التصفير")

# ===== الصفحة الرئيسية =====
df = st.session_state.data

if not df.empty:
    total = df["save"].sum()
    avg = df["save"].mean()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي التوفير", f"{total} لتر")
    c2.metric("متوسط التوفير", f"{int(avg)} لتر")
    c3.metric("عدد الأنشطة", f"{len(df)} نشاط")

    # الرسوم البيانية
    st.subheader("📊 الجداول والرسوم")
    tab1, tab2 = st.tabs(["حسب الفصل", "حسب النشاط"])
    with tab1:
        by_class = df.groupby("cls")["save"].sum().reset_index()
        by_class["الفصل"] = by_class["cls"].map(class_map)
        st.bar_chart(by_class, x="الفصل", y="save")
    with tab2:
        by_act = df.groupby("activity")["save"].sum().reset_index()
        by_act["النشاط"] = by_act["activity"].map(activities)
        st.bar_chart(by_act, x="النشاط", y="save")

    st.dataframe(df, use_container_width=True)

    # ===== الذكاء الاصطناعي =====
    st.subheader("🤖 الذكاء الاصطناعي - التوقعات")
    ai1, ai2, ai3 = st.columns(3)
    best_class = by_class.loc[by_class["save"].idxmax()]["الفصل"] if not by_class.empty else "لا يوجد"
    best_act = by_act.loc[by_act["save"].idxmax()]["النشاط"] if not by_act.empty else "لا يوجد"
    next_save = int(avg * 1.15) # توقع بزيادة 15%

    ai1.info(f"**التوفير القادم المتوقع:**\n\n{next_save} لتر")
    ai2.success(f"**أفضل فصل:**\n\n{best_class}")
    ai3.warning(f"**أكثر نشاط مؤثر:**\n\n{best_act}")

    # ===== الشهادة =====
    st.subheader("🏆 الشهادة")
    st.markdown(f"""
    <div style='border:3px solid #0A6E2F; padding:20px; text-align:center; border-radius:15px; background:#f0fff4;'>
    <h2>شهادة شكر وتقدير</h2>
    <p>تتقدم الابتدائية العاشرة بينبع البحر بشهادة شكر للطالبة</p>
    <h3>حفصة وائل</h3>
    <p>على مبادرة <b>نجدة</b> وتوفير <b>{total} لتر</b> من المياه</p>
    <p>#بترشيدنا_تدوم_نعمتنا - رؤية 2030</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("لا توجد بيانات بعد، ابدأي بتسجيل نشاط من الشريط الجانبي")

# الخريطة
st.subheader("📍 موقع المدرسة")
st.map(pd.DataFrame([{"lat":24.0896, "lon":38.0618}]), zoom=12)
