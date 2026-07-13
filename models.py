import uuid

class User:
    def __init__(self, username: str, phone: str, role: str, rating: float = 5.0, ratings_count: int = 0):
        self.username = username
        self.phone = phone
        self.role = role  # "Пасажир" або "Водій"
        self.rating = rating
        self.ratings_count = ratings_count

    def to_dict(self):
        return {
            "username": self.username,
            "phone": self.phone,
            "role": self.role,
            "rating": self.rating,
            "ratings_count": self.ratings_count
        }

class Order:
    def __init__(self, passenger: str, start_point: str, end_point: str, price: float, tariff: str,
                 order_id: str = None, driver: str = None, status: str = "Очікує водія"):
        self.order_id = order_id if order_id else str(uuid.uuid4())[:8]
        self.passenger = passenger
        self.driver = driver
        self.start_point = start_point
        self.end_point = end_point
        self.price = price
        self.tariff = tariff  # "Економ", "Комфорт", "Бізнес"
        self.status = status  # "Очікує водія", "В дорозі", "Завершено"

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "passenger": self.passenger,
            "driver": self.driver,
            "start_point": self.start_point,
            "end_point": self.end_point,
            "price": self.price,
            "tariff": self.tariff,
            "status": self.status
        }