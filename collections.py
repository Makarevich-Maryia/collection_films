import sys, requests, sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QRadioButton, QPushButton,
                             QMessageBox, QLabel,
                             QGraphicsDropShadowEffect, QVBoxLayout, QInputDialog,QScrollArea)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QRect,QSize
from bs4 import BeautifulSoup
from Style import Stylesheet

con = sqlite3.connect("films_collection.db")
cursor = con.cursor()


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Окно программы
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')
        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)

        self.setStyleSheet(Stylesheet)
        self.setFixedSize(900, 900)
        self.setWindowFlags(Qt.FramelessWindowHint) #Создает безрамочное окно.
        self.setAttribute(Qt.WA_TranslucentBackground) #Включаем прозрачность главной формы..
        self.setWindowTitle('Коллекция фильмов.')

        # полоса ввода
        self.input_window = QLineEdit(self, objectName='input_window')
        self.input_window.setGeometry(50, 80, 680, 30)

        # кнопки
        # добавить
        self.add_button = QPushButton('', self, objectName='Button_icon')
        self.add_button.setGeometry(740, 79, 33, 33)
        self.add_button.clicked.connect(self.parser)
        self.add_button.setIcon(QIcon('add.png'))
        self.add_button.setToolTip('Добавить фильм в коллекцию.')

        # поиск
        self.find_button = QPushButton('', self, objectName='Button_icon')
        self.find_button.setGeometry(780, 79, 33, 33)
        self.find_button.clicked.connect(self.find_bd)
        self.find_button.setIcon(QIcon('find.png'))
        self.find_button.setToolTip('Найти фильм в коллекции.')

        # список
        self.list_button = QPushButton('', self, objectName='Button_icon')
        self.list_button.setGeometry(820, 79, 33, 33)
        self.list_button.clicked.connect(self.history)
        self.list_button.setIcon(QIcon('list.png'))
        self.list_button.setToolTip('Открыть коллекцию фильмов.')

        #создать коллекцю
        self.new_collection = QPushButton('Создать', self, objectName='Button')
        self.new_collection.setGeometry(50, 40, 60, 30)
        self.new_collection.setToolTip('Создайте новую коллекцию.')
        self.new_collection.clicked.connect(self.bd)

        #выбрать коллекцию
        self.list_collections = QPushButton('Выбрать', self, objectName='Button')
        self.list_collections.setGeometry(140, 40, 60, 30)
        self.list_collections.setToolTip('Выбрать коллекцию из списка созданных.')
        self.list_collections.clicked.connect(self.fun_list_collections)

        # Очистить коллекцию
        self.clear_collection = QPushButton('Очистить коллекцию', self, objectName='Button')
        self.clear_collection.setGeometry(230, 40, 150, 30)
        self.clear_collection.clicked.connect(self.clear)
        self.clear_collection.setToolTip('Удалить все данные из коллекции.')

        # удалить
        self.del_collection = QPushButton('Удалить', self, objectName='Button')
        self.del_collection.setGeometry(410, 40, 60, 30)
        self.del_collection.clicked.connect(self.delete)
        self.del_collection.setToolTip('Удалить коллекцию.')

        #инструкция
        self.manual = QPushButton('Инструкция', self, objectName='Button')
        self.manual.setGeometry(500, 40, 90, 30)
        self.manual.clicked.connect(self.instruction)
        self.manual.setToolTip('Как пользоваться программой.')

        # закрыть
        self.close_program = QPushButton('X', self, objectName='close')
        self.close_program.setGeometry(840, 30, 30, 30)
        self.close_program.clicked.connect(self.closeEvent)

        # фильм просмотрен
        self.film_viewed = QRadioButton('Фильм просмотрен', self, objectName='film_viewed')
        self.film_viewed.setGeometry(50, 115, 150, 30)

        # окно вывода со скроллом
        self.scrollArea = QScrollArea(self, objectName='scrollarea')
        self.scrollArea.move(50,150)
        self.scrollArea.setMinimumSize(QSize(800, 700))
        self.scrollArea.setWidgetResizable(True)

        self.output_window = QLabel(self, objectName='Label')
        self.output_window.setAlignment(Qt.AlignTop)
        self.output_window.setWordWrap(True)
        self.output_window.setGeometry(QRect(50, 150, 800, 700))
        self.scrollArea.setWidget(self.output_window)
        self.output_window.setIndent(10)

        for children in self.findChildren(QWidget):
            shadow = QGraphicsDropShadowEffect(blurRadius=15, xOffset=3, yOffset=3)
            shadow.setColor(Qt.black)
            children.setGraphicsEffect(shadow)

        self.collection_name = QLabel(self, objectName='TitleWindow')
        self.collection_name.setGeometry(50, 20, 700, 20)
        self.name = ''
        self.show()

    def parser(self): #поиск информации о фильме на сайте kinopoisk.ru, выведение в QLabel и добавление в коллекцию (таблицу БД)
        self.k = self.input_window.text()
        if self.name == '':
            self.output_window.setText('Выберите или создайте коллекцию.')
        else:
            try:
                url = f'https://www.kinopoisk.ru/index.php?kp_query={self.k}'
                r = requests.get(url)
                soup = BeautifulSoup(r.text, 'lxml')
                name = soup.find('div', class_='search_results').find('p', class_='name').find('a', class_='js-serp-metrika').text
                name_f = name.lower()
                year = soup.find('div', class_='search_results').find('p', class_='name').find('span', class_='year').text
                ganr_country = soup.find('div', class_='search_results').findAll('span', class_='gray')[1].text
                ganr1 = ganr_country.split('\n')
                country = ganr_country.split(',')
                country_f = ''
                gan = ''

                for i in ganr1[1]:
                    if i.isalpha():
                        gan += str(i)
                    elif i == ' ':
                        gan += ','

                for i in country[0]:
                    country_f += i
                    if i == '.':
                        break
                see = ''
                if self.film_viewed.isChecked():
                    see += 'просмотрен'
                else:
                    see += 'не просмотрен'

                cursor.execute(f'''INSERT INTO {self.name}(name,release_year, genre, country, see) VALUES(?,?,?,?,?)''',
                               (name_f, year, gan, country_f, see))
                con.commit()
                cursor.execute(f'''SELECT * FROM {self.name}''')
                con.commit()
                self.output_window.setText(
                    f" Название фильма: {name}, год выхода {year}, жанр: {gan}, страна: {country_f},фильм {see}.")
            except AttributeError:
                self.output_window.setText('Название фильма введено неккоректно.')

    def find_bd(self): #поиск фильма в выбранной коллекции (таблице БД) и выведение информации о нём
        self.output_window.setText('')
        if self.name == '':
            self.output_window.setText('Выберите или создайте коллекцию.')
        else:
            try:
                self.f = self.input_window.text()
                self.f = self.f.lower()
                cursor.execute(f'''SELECT*FROM {self.name} WHERE name LIKE '{self.f}%' ''')
                con.commit()
                k = cursor.fetchall()
                if self.film_viewed.isChecked():
                    cursor.execute(f'''UPDATE {self.name} SET see='просмотрен' WHERE movie_id={k[0][0]}''')
                    con.commit()
                cursor.execute(f'''SELECT*FROM {self.name} WHERE name LIKE '{self.f}%' ''')
                con.commit()
                k_f = cursor.fetchall()
                film = k_f[0]
                self.output_window.setText(f" Название фильма: {film[1]}, год выхода {film[2]}, жанр: {film[3]}, страна: {film[4]}, фильм {film[5]}")
            except IndexError:
                self.output_window.setText('Такого фильма не в коллекции.')

    def history(self):# выведение из выбранной коллекции (таблицы БД) списка всех фильмов и информации о них
        if self.name == '':
            self.output_window.setText('Выберите или создайте коллекцию.')
        else:
            h = ''
            cursor.execute(f'''SELECT * FROM {self.name}''')
            con.commit()
            p = cursor.fetchall()
            if len(p) > 0:
                for i in p:
                    h += f" ID {i[0]}. Название фильма: {i[1]}, год выхода {i[2]}, жанр: {i[3]}, страна: {i[4]}, фильм {i[5]}.\n"
                    h += "_" * 90
                self.output_window.setText(h)
            else:
                self.output_window.setText(f'Коллекция фильмов "{self.name}" пуста.')


    def bd(self): #создание новой коллекции (таблицы БД) с заданным именем
        self.output_window.setText('')
        self.name = ''
        text, ok = QInputDialog().getText(self, " ", "Введите название коллекции:", QLineEdit.Normal,"Имя коллекции без пробелов:")
        if ok and text != "":
            self.name += str(text)
            cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.name}(movie_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, release_year int, genre TEXT, country TEXT,see TEXT)''')
            con.commit()
        self.collection_name.setText(f'''Коллекция: "{self.name}"''')

    def fun_list_collections(self):# список всех созданных коллекций
        self.output_window.setText('')
        names = []
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        con.commit()
        f = cursor.fetchall()
        for i in f:
            if i[0] != 'sqlite_sequence':
                names.append(i[0])

        self.name, okPressed = QInputDialog.getItem(self, " ", "Выберите коллекцию:", names, 0, True)
        if okPressed and self.name:
            cursor.execute(f'''SELECT * FROM {self.name}''')
            con.commit()
            f = cursor.fetchall()
        self.collection_name.setText(f'''Коллекция: "{self.name}"''')


    def clear(self):#Удалить все данные из коллекции(таблицы БД), чтобы в дальнейшем id шли с 1, таблица удалены и создана новая с таким же названием
        try:
            cursor.execute(f'''DROP TABLE {self.name}''')
            con.commit()
            self.output_window.setText(f'Коллекция фильмов "{self.name}"очищена.')
            cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.name}(movie_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, release_year int, genre TEXT, country TEXT,see TEXT)''')
        except AttributeError:
            self.output_window.setText(f'Выберите коллекцию фильмов.')

    def delete(self): #Удаление коллекции (таблицы БД)
        try:
            cursor.execute(f'''DROP TABLE {self.name}''')
            con.commit()
            self.output_window.setText(f'Коллекция фильмов "{self.name}" удалена.')
            self.collection_name.setText('')
        except AttributeError:
            self.output_window.setText(f'Выберите коллекцию фильмов.')

    def instruction(self):#Вывести инструкцию
        f = open('manual.txt', 'r+', encoding='utf-8')
        s = f.readlines()
        f.close()
        text = ''
        n = 1
        for i in s:
            i = i.replace('\n', '')
            text += i + "\n"
            n += 1
        self.output_window.setText(text)

    def closeEvent(self, event):#Окно при закрытии программы

        w = QPushButton()
        w.setStyleSheet('background: white; font: 14px Georgia; font-align: center')

        msgBox = QMessageBox(w)
        msgBox.setWindowIcon(QIcon('empty.png'))
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText('Вы уверены, что хотите выйти?')
        no = msgBox.addButton('Нет', QMessageBox.NoRole)
        yes = msgBox.addButton('Да', QMessageBox.YesRole)
        msgBox.setWindowTitle(' ')
        msgBox.exec_()

        if msgBox.clickedButton() == yes:
            event.accept()

     # Перемещение окна мышкой
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return

        delta = event.pos() - self.old_pos
        self.move(self.pos() + delta)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
