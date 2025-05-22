import json
class Contact:
    def __init__(self, id_, name, phone, comment):
        self.id = id_
        self.name = name
        self.phone = phone
        self.comment = comment

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'comment': self.comment
        }

class PhoneBookModel:
    def __init__(self):
        self.contacts = []
        self.current_file = None
        self.modified = False

    def open_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.contacts = [
                    Contact(
                        item['id'],
                        item['name'],
                        item['phone'],
                        item['comment']
                    ) for item in data
                ]
                self.current_file = filename
                self.modified = False
                return True
        except Exception as e:
            raise Exception(f"Ошибка загрузки: {str(e)}")

    def save_file(self, filename=None):
        try:
            filename = filename or self.current_file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(
                    [contact.to_dict() for contact in self.contacts],
                    f,
                    ensure_ascii=False,
                    indent=4
                )
            self.current_file = filename
            self.modified = False
            return True
        except Exception as e:
            raise Exception(f"Ошибка сохранения: {str(e)}")

    def add_contact(self, name, phone, comment):
        new_id = max([c.id for c in self.contacts], default=0) + 1
        self.contacts.append(Contact(new_id, name.strip(), phone.strip(), comment.strip()))
        self.modified = True

    def find_contacts(self, search_term):
        search_term = search_term.lower()
        return [
            c for c in self.contacts
            if (search_term in c.name.lower() or
                search_term in c.phone or
                search_term in c.comment.lower())
        ]

    def update_contact(self, contact_id, **kwargs):
        contact = next((c for c in self.contacts if c.id == contact_id), None)
        if contact:
            for key, value in kwargs.items():
                if value and hasattr(contact, key):
                    setattr(contact, key, value.strip())
            self.modified = True
            return True
        return False

    def delete_contact(self, contact_id):
        contact = next((c for c in self.contacts if c.id == contact_id), None)
        if contact:
            self.contacts.remove(contact)
            self.modified = True
            return True
        return False


class PhoneBookView:
    @staticmethod
    def show_menu():
        print("\nТелефонный справочник")
        print("1. Открыть файл")
        print("2. Сохранить файл")
        print("3. Показать все контакты")
        print("4. Создать контакт")
        print("5. Найти контакт")
        print("6. Изменить контакт")
        print("7. Удалить контакт")
        print("8. Выход")

    @staticmethod
    def show_contacts(contacts):
        if not contacts:
            print("Контактов нет.")
            return
        for contact in contacts:
            print(f"\nID: {contact.id}")
            print(f"Имя: {contact.name}")
            print(f"Телефон: {contact.phone}")
            print(f"Комментарий: {contact.comment}")
        print("-------------------")

    @staticmethod
    def get_input(prompt):
        return input(prompt).strip()

    @staticmethod
    def show_message(message):
        print(message)

    @staticmethod
    def confirm_action(prompt):
        return input(prompt).strip().lower() == 'y'


class PhoneBookController:
    def __init__(self):
        self.model = PhoneBookModel()
        self.view = PhoneBookView()

    def run(self):
        while True:
            self.view.show_menu()
            choice = self.view.get_input("Выберите действие: ")

            try:
                if choice == '1':
                    self.load_file()
                elif choice == '2':
                    self.save_file()
                elif choice == '3':
                    self.show_all_contacts()
                elif choice == '4':
                    self.create_contact()
                elif choice == '5':
                    self.find_contacts()
                elif choice == '6':
                    self.update_contact()
                elif choice == '7':
                    self.delete_contact()
                elif choice == '8':
                    self.exit()
                    break
                else:
                    self.view.show_message("Неверный выбор. Попробуйте снова.")
            except Exception as e:
                self.view.show_message(f"Ошибка: {str(e)}")

    def load_file(self):
        filename = self.view.get_input("Введите имя файла: ")
        self.model.open_file(filename)
        self.view.show_message("Файл успешно загружен.")

    def save_file(self):
        filename = self.model.current_file or self.view.get_input("Введите имя файла для сохранения: ")
        self.model.save_file(filename)
        self.view.show_message("Файл успешно сохранен.")

    def show_all_contacts(self):
        self.view.show_contacts(self.model.contacts)

    def create_contact(self):
        name = self.view.get_input("Введите имя: ")
        phone = self.view.get_input("Введите телефон: ")
        comment = self.view.get_input("Введите комментарий: ")

        if not name or not phone:
            raise ValueError("Имя и телефон обязательны")

        self.model.add_contact(name, phone, comment)
        self.view.show_message("Контакт успешно создан.")

    def find_contacts(self):
        search_term = self.view.get_input("Введите поисковый запрос: ")
        found = self.model.find_contacts(search_term)
        self.view.show_contacts(found)

    def update_contact(self):
        contact_id = self.view.get_input("Введите ID контакта: ")
        if not contact_id.isdigit():
            raise ValueError("Неверный формат ID")

        contact = next((c for c in self.model.contacts if c.id == int(contact_id)), None)
        if not contact:
            raise ValueError("Контакт не найден")

        new_name = self.view.get_input("Новое имя (оставьте пустым чтобы не менять): ")
        new_phone = self.view.get_input("Новый телефон (оставьте пустым чтобы не менять): ")
        new_comment = self.view.get_input("Новый комментарий (оставьте пустым чтобы не менять): ")

        updates = {}
        if new_name: updates['name'] = new_name
        if new_phone: updates['phone'] = new_phone
        if new_comment: updates['comment'] = new_comment

        self.model.update_contact(int(contact_id), **updates)
        self.view.show_message("Контакт обновлен")

    def delete_contact(self):
        contact_id = self.view.get_input("Введите ID контакта: ")
        if not contact_id.isdigit():
            raise ValueError("Неверный формат ID")

        if self.view.confirm_action("Вы уверены? (y/n): "):
            self.model.delete_contact(int(contact_id))
            self.view.show_message("Контакт удален")

    def exit(self):
        if self.model.modified:
            if self.view.confirm_action("Сохранить изменения перед выходом? (y/n): "):
                self.save_file()

if __name__ == "__main__":
    app = PhoneBookController()
    app.run()
