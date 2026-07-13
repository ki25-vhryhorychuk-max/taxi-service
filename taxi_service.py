import json
import os
from models import User, Order

DB_FILE = "taxi_db.json"

class TaxiService:
    def __init__(self):
        self.users = {}
        self.orders = []
        # Наші тарифи таксі
        self.tariffs = {
            "Економ": {"base_price": 50, "per_km": 10, "car_type": "Hyundai Accent, Renault Logan", "emoji": "🚗"},
            "Комфорт": {"base_price": 80, "per_km": 15, "car_type": "Toyota Camry, Skoda Octavia", "emoji": "🚕"},
            "Бізнес": {"base_price": 150, "per_km": 30, "car_type": "Mercedes-Benz E-Class, BMW 5 Series", "emoji": "🖤"}
        }
        self.load_data()

    def load_data(self):
        if not os.path.exists(DB_FILE):
            # Початкові демо-користувачі
            self.users = {
                "driver_vasyl": User("driver_vasyl", "+380671112233", "Водій"),
                "maryna_pass": User("maryna_pass", "+380934445566", "Пасажир")
            }
            self.save_data()
            return

        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.users = {}
            for u_data in data.get("users", []):
                self.users[u_data["username"]] = User(**u_data)
            self.orders = []
            for o_data in data.get("orders", []):
                self.orders.append(Order(**o_data))

    def save_data(self):
        data = {
            "users": [u.to_dict() for u in self.users.values()],
            "orders": [o.to_dict() for o in self.orders]
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def register_user(self, username: str, phone: str, role: str) -> bool:
        if username in self.users or not username:
            return False
        self.users[username] = User(username, phone, role)
        self.save_data()
        return True

    def calculate_price(self, tariff_name: str, distance: float = 5.0) -> float:
        tariff = self.tariffs.get(tariff_name)
        if not tariff:
            return 0.0
        return tariff["base_price"] + (tariff["per_km"] * distance)

    def create_order(self, passenger: str, start_point: str, end_point: str, tariff: str, price: float) -> Order:
        order = Order(passenger, start_point, end_point, price, tariff)
        self.orders.append(order)
        self.save_data()
        return order

    def accept_order(self, order_id: str, driver_username: str) -> bool:
        for order in self.orders:
            if order.order_id == order_id and order.status == "Очікує водія":
                order.driver = driver_username
                order.status = "В дорозі"
                self.save_data()
                return True
        return False

    def complete_order(self, order_id: str, rating: int) -> bool:
        for order in self.orders:
            if order.order_id == order_id and order.status == "В дорозі":
                order.status = "Завершено"
                driver = self.users.get(order.driver)
                if driver:
                    total_score = (driver.rating * driver.ratings_count) + rating
                    driver.ratings_count += 1
                    driver.rating = round(total_score / driver.ratings_count, 2)
                self.save_data()
                return True
        return False