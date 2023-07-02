import re
import pickle
from datetime import date, datetime
from collections import UserDict

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass

class Name(Field):
    pass

class Phone(Field):
    PHONE_REGEX = re.compile(r"^\+?(\d{2})?\(?\d{3}\)?[\d\-\s]{7,10}$")

    def validate(self, phone):
        if not self.PHONE_REGEX.match(phone):
            raise ValueError(f"Phone number {phone} is invalid.")

class Birthday(Field):
    DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def validate(self, date_str):
        if not self.DATE_REGEX.match(date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD.")

    @property
    def value(self):
        if self._value:
            return datetime.strptime(self._value, "%Y-%m-%d").date()
        return None

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

class Record:
    def __init__(self, name, birthday=None):
        self.name = name
        self.phones = []
        self.birthday = birthday

    def add(self, phone):
        self.phones.append(phone)

    def days_to_birthday(self):
        if self.birthday and self.birthday.value:
            today = date.today()
            next_birthday = date(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = date(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_left = (next_birthday - today).days
            return days_left
        return None

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, name):
        self.data.pop(name, None)

    def get_all_records(self):
        return self.data.values()

    def search(self, query):
        result = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower() or any(query in phone.value for phone in record.phones):
                result.append(record)
        return result

def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except (IndexError, ValueError):
            return "Помилка введення. Спробуйте ще раз."
        except KeyError:
            return "Контакту з таким ім'ям не знайдено."
    return inner

class Assistant:
    SAVE_FILE = "address_book.pickle"

    def __init__(self):
        self.address_book = AddressBook()

    @input_error
    def hello(self, command_args):
        return "Привіт! Я можу допомогти Вам з наступними командами: add, change name, phone name, show_all, birthday name, exit."

    @input_error
    def add(self, command_args):
        name = input("Введіть ім'я: ")
        birthday = input("Введіть день народження (у форматі YYYY-MM-DD): ")
        record = Record(Name(name), Birthday(birthday))
        phone = input("Введіть номер телефону: ")
        record.add(Phone(phone))
        self.address_book.add_record(record)
        return "Запис додано."

    @input_error
    def change(self, command_args):
        name = command_args.strip()
        record = self.address_book.data.get(name)
        if not record:
            return "Контакту з таким ім'ям не знайдено."
        phone = input("Введіть новий номер телефону: ")
        record.phones = [Phone(phone)]
        return "Зміни збережено."

    @input_error
    def phone(self, command_args):
        name = command_args.strip()
        record = self.address_book.data.get(name)
        if not record:
            return "Контакту з таким ім'ям не знайдено."
        return ', '.join([str(phone.value) for phone in record.phones])

    @input_error
    def show_all(self, command_args):
        return "\n".join([str(record.name.value) + ": " + ', '.join([str(phone.value) for phone in record.phones]) for record in self.address_book.get_all_records()])

    @input_error
    def birthday(self, command_args):
        name = command_args.strip()
        record = self.address_book.data.get(name)
        if not record:
            return "Контакту з таким ім'ям не знайдено."
        days = record.days_to_birthday()
        if days:
            return f"До дня народження залишилося {days} днів."
        else:
            return "Дата народження не вказана."

    @input_error
    def exit(self, command_args):
        self.save_data()
        return "До побачення!"

    def load_data(self):
        try:
            with open(self.SAVE_FILE, "rb") as file:
                self.address_book = pickle.load(file)
        except FileNotFoundError:
            pass

    def save_data(self):
        with open(self.SAVE_FILE, "wb") as file:
            pickle.dump(self.address_book, file)

if __name__ == "__main__":
    assistant = Assistant()
    assistant.load_data()
    print("Введіть команду:")
    while True:
        command = input("> ")
        command_name, command_args = command.split(" ", 1) if " " in command else (command, "")
        function = getattr(assistant, command_name, None)
        if function:
            print(function(command_args))
        else:
            print("Невідома команда. Спробуйте ще раз.")
        if command_name == 'exit':
            break
