import streamlit as st
from taxi_service import TaxiService

# Ініціалізація сервісу
if "service" not in st.session_state:
    st.session_state.service = TaxiService()
if "current_user" not in st.session_state:
    st.session_state.current_user = None

db = st.session_state.service

# Налаштування сторінки
st.set_page_config(page_title="Taxi Premium", page_icon="🚕", layout="wide")

# --- HEADER / NAVIGATION ---
st.markdown("""
<style>
.header {
    background-color: #1a1a1a;
    padding: 20px;
    color: white;
    text-align: center;
    border-radius: 8px;
}
.header a {
    color: #ffc107;
    text-decoration: none;
    margin: 0 15px;
    font-weight: bold;
}
.header a:hover {
    color: white;
}
</style>
<div class="header">
    <span style="font-size: 24px; font-weight: bold; margin-right: 30px; color: #ffc107;">🚕 Taxi Premium</span>
    <a href="#">Замовити таксі</a>
    <a href="#about">Про нас</a>
    <a href="#contacts">Контакти</a>
</div>
""", unsafe_allow_html=True)

st.write("") 

# --- АВТОРИЗАЦІЯ (Sidebar) ---
st.sidebar.subheader("🔑 Кабінет користувача")
if not st.session_state.current_user:
    tab1, tab2 = st.sidebar.tabs(["Увійти", "Реєстрація"])
    
    with tab1:
        login_user = st.text_input("Ваш нікнейм:", key="login_input").strip()
        if st.button("Увійти"):
            if login_user in db.users:
                st.session_state.current_user = db.users[login_user]
                st.rerun()
            else:
                st.error("Користувача не знайдено.")
                
    with tab2:
        new_user = st.text_input("Новий нікнейм:", key="reg_input").strip()
        phone = st.text_input("Номер телефону:")
        role = st.selectbox("Хто ви:", ["Пасажир", "Водій"])
        if st.button("Зареєструватися"):
            if db.register_user(new_user, phone, role):
                st.success("Успішно зареєстровано!")
                st.session_state.current_user = db.users[new_user]
                st.rerun()
            else:
                st.error("Цей нікнейм уже зайнятий.")
else:
    user = st.session_state.current_user
    st.sidebar.markdown(f"### 👋 Вітаємо, **{user.username}**!")
    st.sidebar.markdown(f"👤 **Роль:** {user.role}")
    if user.role == "Водій":
        st.sidebar.markdown(f"⭐ **Рейтинг:** {user.rating} ({user.ratings_count} оцінок)")
    if st.sidebar.button("🚪 Вийти"):
        st.session_state.current_user = None
        st.rerun()

# --- ГОЛОВНИЙ ФУНКЦІОНАЛ ---
if not st.session_state.current_user:
    st.info("💡 Будь ласка, увійдіть або зареєструйтесь у бічній панелі (зліва), щоб отримати доступ до замовлень.")

# --- ТАРИФИ ---
st.header("Наші тарифи")
st.write("Оберіть найкращий варіант для вашої поїздки:")

cols = st.columns(3)
for i, (t_name, t_info) in enumerate(db.tariffs.items()):
    with cols[i]:
        st.markdown(f"""
        <div style="background-color: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;">
            <h3 style="margin-top:0;">{t_info['emoji']} Тариф "{t_name}"</h3>
            <p><b>Автомобілі:</b> {t_info['car_type']}</p>
            <p><b>Подача:</b> {t_info['base_price']} грн</p>
            <p><b>Вартість:</b> {t_info['per_km']} грн / км</p>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# --- ЛОГІКА ПАСАЖИРА ---
if st.session_state.current_user and st.session_state.current_user.role == "Пасажир":
    st.header("🚖 Замовлення поїздки")
    
    col1, col2 = st.columns(2)
    with col1:
        start_pt = st.text_input("📍 Звідки (Адреса відправлення):", value="вул. Хрещатик, 1")
        end_pt = st.text_input("🏁 Куди (Адреса призначення):", value="Проспект Перемоги, 45")
        promocode = st.text_input("🎟️ Маєте промокод? Введіть сюди:", value="").strip()
    
    with col2:
        selected_tariff = st.selectbox("🚖 Оберіть тариф:", list(db.tariffs.keys()))
        distance = st.slider("📏 Приблизна відстань (км):", min_value=1, max_value=50, value=7)
        
    estimated_price = db.calculate_price(selected_tariff, distance)
    
    # Перевірка промокоду
    discount = 0.0
    if promocode.upper() == "TAXI2026":
        discount = estimated_price * 0.20
        st.caption("🎉 Промокод TAXI2026 активовано! Знижка 20%")
    elif promocode.upper() == "FREE50":
        discount = 50.0
        st.caption("🎉 Промокод FREE50 активовано! Знижка 50 грн")
        
    final_price = max(10.0, estimated_price - discount)
    
    if discount > 0:
        st.markdown(f"### 💰 Вартість: ~~{estimated_price} грн~~ 👉 <span style='color: #ffc107;'>**{final_price:.2f} грн**</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"### 💰 Орієнтовна вартість: **{final_price:.2f} грн**")
    
    if st.button("🚀 Викликати таксі", use_container_width=True):
        if not start_pt.strip() or not end_pt.strip():
            st.error("❌ Будь ласка, заповніть обидва поля: звідки і куди ви їдете!")
        else:
            order = db.create_order(st.session_state.current_user.username, start_pt, end_pt, selected_tariff, round(final_price, 2))
            st.success(f"🚖 Замовлення №{order.order_id} успішно створено! Шукаємо водія...")

    st.write("---")
    my_orders = [o for o in db.orders if o.passenger == st.session_state.current_user.username]
    
    tab_current, tab_history = st.tabs(["📋 Поточні поїздки", "📜 Історія завершених поїздок"])
    
    with tab_current:
        active_orders = [o for o in my_orders if o.status != "Завершено"]
        if not active_orders:
            st.write("У вас немає активних замовлень на цей момент.")
        else:
            for o in active_orders:
                status_color = "🟡" if o.status == "Очікує водія" else "🟢"
                st.write(f"{status_color} Замовлення **{o.order_id}**: {o.start_point} ➡️ {o.end_point} | Тариф: *{o.tariff}* | Сума: **{o.price} грн** | Статус: **{o.status}**")
                if o.driver:
                    st.write(f"   👨‍✈️ Вас везе водій: **{o.driver}**")
                    
    with tab_history:
        history_orders = [o for o in my_orders if o.status == "Завершено"]
        if not history_orders:
            st.write("Ви ще не здійснювали поїздок.")
        else:
            history_data = []
            for o in history_orders:
                history_data.append({
                    "ID Замовлення": o.order_id,
                    "Маршрут": f"{o.start_point} ➡️ {o.end_point}",
                    "Тариф": o.tariff,
                    "Водій": o.driver,
                    "Вартість (грн)": o.price,
                    "Статус": "✅ Виконано"
                })
            st.table(history_data)

# --- ЛОГІКА ВОДІЯ ---
elif st.session_state.current_user and st.session_state.current_user.role == "Водій":
st.header("🦺 Панель водія")

    # --- СТАТИСТИКА ВОДІЯ ---
    completed_orders = [o for o in db.orders if o.driver == st.session_state.current_user.username and o.status == "Виконано"]
    total_earned = sum(o.price for o in completed_orders)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="💰 Зароблено за зміну", value=f"{total_earned:.2f} грн")
    with col2:
        st.metric(label="✅ Виконано поїздок", value=len(completed_orders))
    # ------------------------

    tab_active, tab_my = st.tabs(["🌐 Доступні замовлення", "📂 Моя поточна поїздка"])
    
    with tab_active:
        available_orders = [o for o in db.orders if o.status == "Очікує водія"]
        if not available_orders:
            st.info("Наразі немає вільних замовлень. Очікуйте нових клієнтів!")
        else:
            for o in available_orders:
                st.markdown(f"""
                <div style="background-color: #31333F; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
                    <h4>Замовлення #{o.order_id}</h4>
                    <p>📍 <b>Звідки:</b> {o.start_point} | 🏁 <b>Куди:</b> {o.end_point}</p>
                    <p>💵 <b>Ціна:</b> {o.price} грн | 📦 <b>Тариф:</b> {o.tariff}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Прийняти замовлення #{o.order_id}", key=f"accept_{o.order_id}"):
                    db.accept_order(o.order_id, st.session_state.current_user.username)
                    st.success(f"Ви прийняли замовлення {o.order_id}!")
                    st.rerun()

    with tab_my:
        my_current = [o for o in db.orders if o.driver == st.session_state.current_user.username and o.status == "В дорозі"]
        if not my_current:
            st.write("Ви зараз не виконуєте жодного замовлення.")
        else:
            current_order = my_current[0]
            st.info(f"📍 Виконується рейс: **{current_order.start_point} ➡️ {current_order.end_point}**")
            st.write(f"Пасажир: **{current_order.passenger}** | До сплати: **{current_order.price} грн**")
            
            rating = st.slider("Оцініть пасажира (для рейтингу):", 1, 5, 5)
            if st.button("🏁 Завершити поїздку та отримати оплату"):
                db.complete_order(current_order.order_id, rating)
                st.success("Поїздку успішно завершено!")
                st.rerun()

# --- СЕКЦІЯ "ПРО НАС" ---
st.markdown("<div id='about'></div>", unsafe_allow_html=True)
st.write("---")
st.header("Про нас")
st.write("Ми — сучасний сервіс виклику таксі Taxi Premium. Ми поєднуємо зручність технологій із безпекою пасажирів.")

# --- СЕКЦІЯ "КОНТАКТИ" ---
st.markdown("<div id='contacts'></div>", unsafe_allow_html=True)
st.header("Контакти")
col1, col2 = st.columns(2)
with col1:
    st.write("📫 Наша адреса:")
    st.markdown("📍 Київ, Україна")
    st.markdown("📞 +380 44 111 22 33")
    st.markdown("✉️ support@taxipremium.com")
with col2:
    st.write("Ми в соціальних мережах:")
    st.markdown("[Facebook](https://www.facebook.com/) • [Instagram](https://www.instagram.com/) • [Telegram](https://t.me/)")

# --- FOOTER ---
st.markdown("""
<style>
.footer {
    background-color: #111;
    padding: 30px;
    color: #ccc;
    text-align: left;
    display: flex;
    justify-content: space-between;
    margin-top: 40px;
    border-radius: 8px;
}
.footer-section { width: 30%; }
.footer-logo { color: #ffc107; font-size: 1.5em; font-weight: bold; }
.footer a { color: #ccc; text-decoration: none; }
.footer a:hover { color: #ffc107; }
</style>
<div class="footer">
    <div class="footer-section">
        <span class="footer-logo">🚕 Taxi Premium</span><br><br>
        Сучасна та надійна система замовлення таксі.
    </div>
    <div class="footer-section">
        <b>Навігація</b><br><br>
        <a href="#">Замовити таксі</a><br>
        <a href="#about">Про нас</a><br>
        <a href="#contacts">Контакти</a>
    </div>
    <div class="footer-section">
        <b>Підтримка</b><br><br>
        📍 Київ, Україна<br>
        📞 +380 44 111 22 33<br>
    </div>
</div>
""", unsafe_allow_html=True)
