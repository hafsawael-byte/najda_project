import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pathlib
import random
import pydeck as pdk

BASE = pathlib.Path(__file__).parent
DATA_FILE = BASE / "najda_data.csv"
st.set_page_config(page_title="Najda - مبادرة الطالبة حفصة وائل", layout="wide")

bp = BASE / "banner_final.jpg"
if bp.exists():
    st.image(str(bp), use_container_width=True)

st.markdown("<div style='background:#0A6E2F; color:white; padding:12px; text-align:center; border-radius:10px;'><b>رؤية 2030 - #بترشيدنا_تدوم_نعمتنا</b><br>الابتدائية العاشرة بينبع البحر - مبادرة الطالبة حفصة وائل</div>", unsafe_allow_html=True)

# قائمة الانشطة المختلفة
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

# تحميل البيانات الحقيقية
if 'data' not in st.session_state:
    if DATA_FILE.exists():
        try:
            st.session_state.data = pd.read_csv(DATA_FILE)
            st.session_state.data["dt"] = pd.to_datetime(st.session_state.data["dt"]).dt.date
        except:
            st.session_state.data = pd.DataFrame(columns=["cls","save","dt","std","activity"])
    else:
        st.session_state.data = pd.DataFrame([
            {"cls":"Grade1","save":120,"dt":datetime.now().date()-timedelta(days=2),"std":25,"activity":"close_taps"},
            {"cls":"Grade3","save":54,"dt":datetime.now().date()-timedelta(days=1),"std":30,"activity":"awareness"},
            {"cls":"Grade5","save":200,"dt":datetime.now().date(),"std":28,"activity":"fix_leak"},
        ])
        st.session_state.data.to_csv(DATA_FILE, index=False)

def get_risk_level(s):
    if s >= 150:
        return "آمن", "#2ECC71", "green"
    elif s >= 70:
        return "متوسط", "#F39C12", "yellow"
    else:
        return "خطر", "#E74C3C", "red"

with st.sidebar:
    st.header("تسجيل نشاط حقيقي")
    cls_en = st.selectbox("الفصل", list(class_map.keys()), format_func=lambda x: class_map[x])
    act_en = st.selectbox("نوع النشاط", list(activities.keys()), format_func=lambda x: activities[x])
    save = st.number_input("التوفير لتر", value=54, min_value=1)
    std = st.number_input("عدد الطالبات", value=25, min_value=1)
    
    # مؤشر الخطر المباشر
    label, color, _ = get_risk_level(save)
    st.markdown(f"<div style='background:{color}; color:white; padding:10px; border-radius:8px; text-align:center;'><b>مؤشر الخطر: {label}</b><br>{save} لتر</div>", unsafe_allow_html=True)
    
    if st.button("حفظ", type="primary", use_container_width=True):
        nr = {"cls":cls_en, "save":save, "dt":datetime.now().date(), "std":std, "activity":act_en}
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([nr])], ignore_index=True)
        st.session_state.data.to_csv(DATA_FILE, index=False)
        st.balloons()
        st.success("تم الحفظ")
    st.divider()
    if st.button("تصفير البيانات", use_container_width=True):
        if DATA_FILE.exists():
            DATA_FILE.unlink()
        st.session_state.data = pd.DataFrame(columns=["cls","save","dt","std","activity"])
        st.success("تم تصفير كل البيانات")
        st.rerun()

df = st.session_state.data

# 1- الجداول
st.subheader("1- الجداول الحقيقية")
if not df.empty:
    df_show = df.copy()
    df_show["cls"] = df_show["cls"].map(class_map)
    df_show["activity"] = df_show["activity"].map(activities)
    st.dataframe(df_show, use_container_width=True, hide_index=True)

# 2- الرسم
st.subheader("2- الرسم البياني")
if not df.empty:
    chart = df.groupby("cls")["save"].sum().reset_index()
    chart["cls"] = chart["cls"].map(class_map)
    st.bar_chart(chart, x="cls", y="save")

# 3- الخريطة
st.subheader("3- الخريطة - نقط صغيرة")
map_data = pd.DataFrame({"lat":[24.0896],"lon":[38.0618],"name":["المدرسة"]})
st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(latitude=24.0896, longitude=38.0618, zoom=14.5),
    layers=[pdk.Layer("ScatterplotLayer", data=map_data, get_position='[lon, lat]', get_color='[10, 110, 47, 180]', get_radius=25)],
))
st.caption("نقط صغيرة خضرا")

# 4- مؤشر الخطر الكبير
st.subheader("4- مؤشر الخطر - اخضر اصفر احمر - بحسب معدل التوفير")
if not df.empty:
    cols = st.columns(len(df))
    for i, (_, row) in enumerate(df.tail(6).iterrows()):
        label, color, _ = get_risk_level(row['save'])
        with cols[i % 6]:
            st.markdown(f"<div style='background:{color}; color:white; padding:15px; border-radius:10px; text-align:center; margin:5px;'><b>{class_map.get(row['cls'])}</b><br>{row['save']} لتر<br><b>{label}</b></div>", unsafe_allow_html=True)
    st.markdown("**الشرح:** <span style='color:#2ECC71;'>■ اخضر >=150 لتر آمن</span> | <span style='color:#F39C12;'>■ اصفر 70-149 متوسط</span> | <span style='color:#E74C3C;'>■ احمر <70 خطر</span>", unsafe_allow_html=True)

# 5- الذكاء الاصطناعي
st.subheader("5- الذكاء الاصطناعي يتوقع")
if not df.empty:
    # 1- التوفير القادم
    avg = df['save'].mean()
    next_save = int(avg + random.randint(5,30))
    
    # 2- افضل فصل
    best_cls_en = df.groupby('cls')['save'].sum().idxmax()
    best_cls = class_map.get(best_cls_en)
    best_val = int(df.groupby('cls')['save'].sum().max())
    
    # 3- اكثر نشاط مؤثر
    best_act_en = df.groupby('activity')['save'].mean().idxmax()
    best_act = activities.get(best_act_en, best_act_en)
    best_act_val = int(df.groupby('activity')['save'].mean().max())

    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div style='background:#E8F6F3; padding:20px; border-radius:12px; text-align:center; border:2px solid #2ECC71;'><h3>التوفير القادم</h3><h1 style='color:#0A6E2F;'>{next_save} لتر</h1><p>الاسبوع القادم</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div style='background:#FEF9E7; padding:20px; border-radius:12px; text-align:center; border:2px solid #F39C12;'><h3>افضل فصل</h3><h1 style='color:#B7950B;'>{best_cls}</h1><p>{best_val} لتر اجمالي</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div style='background:#FDEDEC; padding:20px; border-radius:12px; text-align:center; border:2px solid #E74C3C;'><h3>اكثر نشاط مؤثر</h3><h1 style='font-size:18px;'>{best_act}</h1><p>متوسط {best_act_val} لتر</p></div>", unsafe_allow_html=True)
    
    # رسم توقع 5 ايام
    future = [{"اليوم":f"بعد {i} يوم","المتوقع": int(avg + i*8 + random.randint(-5,10))} for i in range(1,6)]
    st.line_chart(pd.DataFrame(future), x="اليوم", y="المتوقع")
else:
    st.info("سجلي بيانات ليبدأ الذكاء الاصطناعي التوقع")

# 6- الشهادة
st.subheader("6- شهادة شكر وتقدير للفصل المتميز")
if st.button("انشاء الشهادة الرسمية", type="primary", use_container_width=True):
    st.balloons()
    if not df.empty:
        top_en = df.groupby("cls")["save"].sum().idxmax()
        top_c = class_map.get(top_en, top_en)
        top_s = int(df.groupby("cls")["save"].sum().max())
    else:
        top_c = "اول ابتدائي"
        top_s = 54
    html = f"<div style='border:8px double #0A6E2F; padding:30px; text-align:center; background:#fff; border-radius:15px;'><h1 style='color:#0A6E2F;'>شهادة شكر و تقدير للفصل المتميز</h1><h1 style='color:#0A6E2F; font-size:58px; margin:25px 0;'>{top_c}</h1><p style='font-size:24px; font-weight:bold;'>شكرا لترشيدكم</p><p>توفير {top_s} لتر - مبادرة الطالبة حفصة وائل</p></div>"
    st.markdown(html, unsafe_allow_html=True)
