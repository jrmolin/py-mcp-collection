CALCULATOR_CODE = """
class Calculator:
    '''This is a class'''
    def __init__(self, name):
        self.name = name

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        return a / b

    def power(self, a, b):
        return a ** b
"""
CALCULATOR_CODE_METADATA = {"topic": "calculators"}

EMPLOYEE_CODE = """
class Employee:
    '''This represents an employee'''
    def __init__(self, name, age, salary):
        self.name = name
        self.age = age
        self.salary = salary

    def first_name(self):
        return self.name.split()[0]

    def last_name(self):
        return self.name.split()[-1]

    def full_name(self):
        return f"{self.first_name()} {self.last_name()}"

    def email(self):
        return f"{self.first_name()}.{self.last_name()}@example.com"

    def tenure(self):
        return self.age / 10

    def age_group(self):
        if self.age < 25:
            return "young"
        elif self.age < 40:
            return "middle-aged"
        else:
            return "old"
"""
EMPLOYEE_CODE_METADATA = {"topic": "employees"}

POTATO_OR_TOMATO_CODE = """

class Vegetable:
    '''This is a vegetable'''
    def __init__(self, name, shape, color, taste, texture, smell):
        self.name = name
        self.shape = shape
        self.color = color
        self.taste = taste
        self.texture = texture
        self.smell = smell

    def is_vegetable(self):
        return True

    def get_shape(self):
        return self.shape

    def get_color(self):
        return self.color

    def get_taste(self):
        return self.taste

    def get_texture(self):
        return self.texture

    def get_smell(self):
        return self.smell

class Potato(Vegetable):
    '''This is a potato'''
    def __init__(self, name):
        self.name = name
        self.shape = "round"
        self.color = "brown"
        self.taste = "sweet"
        self.texture = "soft"
        self.smell = "earthy"

    def is_potato(self):
        return True

class Tomato(Vegetable):
    '''This is a tomato'''
    def __init__(self, name):
        self.name = name
        self.shape = "round"
        self.color = "red"
        self.taste = "sweet"
        self.texture = "soft"
        self.smell = "earthy"

    def is_tomato(self):
        return True

def is_potato_or_tomato(not_sure_what_this_is: Vegetable):
    return not_sure_what_this_is.is_potato() or not_sure_what_this_is.is_tomato()
"""
POTATO_OR_TOMATO_CODE_METADATA = {"topic": "vegetables"}

CAR_CODE = """
class Car:
    '''This is a car'''
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def get_make(self):
        return self.make

    def get_model(self):
        return self.model

    def get_year(self):
        return self.year

    def get_top_speed(self):
        return 100

    def get_color(self):
        return "red"

    def get_price(self):
        return 10000

    def get_age(self):
        return datetime.now().year - self.year
"""
CAR_CODE_METADATA = {"topic": "cars"}


CODE_DOCS = [
    (CALCULATOR_CODE, CALCULATOR_CODE_METADATA),
    (EMPLOYEE_CODE, EMPLOYEE_CODE_METADATA),
    (POTATO_OR_TOMATO_CODE, POTATO_OR_TOMATO_CODE_METADATA),
    (CAR_CODE, CAR_CODE_METADATA),
]
