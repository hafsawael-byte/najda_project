import streamlit as st
import pandas as pd
from datetime import datetime
import pathlib
import requests

SHEET_ID = "16BppQGDtoAK5eIaxaZFhJVgdpR7Q4cDj23ep3YO9bXU" 
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"

# رابطك انتي - جاهز
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwz1NSUP4I0yn765VEy-yJpeZ_qq9c0-JIrUP-kSZVDBoRCsEcSGp81spksvQxGLcPenA/exec"

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

@st.cache_data(ttl=5)
def load_from_gsheet():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if df.empty or "cls" not in df.columns:
            return pd.DataFrame(columns=["cls","save","dt","std","activity"])
        df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
        return df
    except:
        return pd.DataFrame(columns=["cls","save","dt","std","activity"])

def save_permanent(new_row):
    try:
        payload = {"cls": new_row["cls"], "save": int(new_row["save"]), "dt": str(new_row["dt"]), "std": int(new_row["std"]), "activity": new_row["activity"]}
        requests.post(WEB_APP_URL, json=payload, timeout=20)
        return True
    except Exception as e:
        st.error(f"خطأ: {e}")
        return False

def get_risk_level(s):
    if s >= 150: return "آمن ✅", "#2ECC71"
    elif s >= 70: return "متوسط ⚠️", "#F39C12"
    else: return "خطر ❗", "#E74C3C"

if 'data' not in st.session_state:
    st.session_state.data = load_from_gsheet()

with st.sidebar:
    st.header("تسجيل نشاط حقيقي")
    cls_en = st.selectbox("الفصل", list(class_map.keys()), format_func=lambda x: class_map[x])
    act_en = st.selectbox("نوع النشاط", list(activities.keys()), format_func=lambda x: activities[x])
    save = st.number_input("التوفير لتر", value=55, min_value=1)
    std = st.number_input("عدد الطالبات", value=27, min_value=1)
    
    label, color = get_risk_level(save)
    st.markdown(f'<div style="background:{color}; color:white; padding:16px; border-radius:8px; text-align:center; font-weight:bold;">{label}<br>{save} لتر</div>', unsafe_allow_html=True)
    st.write("")
    
    if st.button("💾 حفظ دائم - ما يضيعش", use_container_width=True, type="primary"):
        new_row = {"cls": cls_en, "save": save, "dt": datetime.now().date(), "std": std, "activity": act_en}
        with st.spinner("جاري الحفظ في الشيت للأبد..."):
            save_permanent(new_row)
        st.cache_data.clear()
        st.session_state.data = load_from_gsheet()
        st.success(f"تم حفظ {save} لتر للأبد! 🎉")
        st.rerun()

    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.cache_data.clear()
        st.session_state.data = load_from_gsheet()
        st.rerun()

df = st.session_state.data
if not df.empty:
    total = df["save"].sum()
    avg = df["save"].mean()
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي التوفير", f"{total} لتر")
    m2.metric("المتوسط", f"{int(avg)} لتر")
    m3.metric("الأنشطة", f"{len(df)}")

    st.subheader("📊 الجداول")
    t1, t2 = st.tabs(["حسب الفصل", "حسب النشاط"])
    with t1:
        by_class = df.groupby("cls")["save"].sum().reset_index()
        by_class["الفصل"] = by_class["cls"].map(class_map)
        st.bar_chart(by_class, x="الفصل", y="save")
    with t2:
        by_act = df.groupby("activity")["save"].sum().reset_index()
        by_act["النشاط"] = by_act["activity"].map(activities)
        st.bar_chart(by_act, x="النشاط", y="save")
    st.dataframe(df, use_container_width=True)

    st.subheader("🏆 الشهادة")
    last_class = class_map.get(df.iloc[-1]["cls"], df.iloc[-1]["cls"])
    st.markdown(f"""
    <div style='border:3px solid #0A6E2F; padding:20px; text-align:center; border-radius:15px; background:#f0fff4;'>
    <h2>شهادة شكر وتقدير</h2>
    <p>تتقدم إدارة المدرسة بالشكر للصف</p>
    <h3>{last_class}</h3>
    <p>على تميزه وتوفير <b>{total} لتر</b></p>
    <p>#بترشيدنا_تدوم_نعمتنا - رؤية 2030</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("لا توجد بيانات بعد - سجلي أول نشاط")

st.subheader("📍 موقع المدرسة")
st.map(pd.DataFrame([{"lat":24.0896, "lon":38.0618}]), zoom=12)
