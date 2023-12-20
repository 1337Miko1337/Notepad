import threading
import tkinter as tk
from tkinter import ttk
import time
from tkinter.messagebox import showinfo

import schedule
from tkcalendar import DateEntry
from datetime import datetime
from win10toast import ToastNotifier

# Словник для зберігання записів
records = []
tasks = []
global stop
stop = False



# Функція для додавання запису
def add_record():
    title = title_entry.get()
    date = date_entry.get()
    hour = hour_spinbox.get()
    min = minute_spinbox.get()
    try:
        datetime.strptime(date + " " + hour + ":" + min, "%d/%m/%Y %H:%M")
    except ValueError:
        error_label.config(text="Некоректна дата або час")
        return
    if len(hour) == 1:
        hour = '0' + hour
    if len(min) == 1:
        min = '0' + min
    records.append({"Title": title, "Date": date, "Time": hour + ":" + min})
    update_table()
    clear_fields()
    error_label.config(text="")
    schedule_notification(date, hour, min, title)


# Функція для оновлення таблиці
def update_table():
    for i in tree.get_children():
        tree.delete(i)

    for idx, record in enumerate(records, start=1):
        tree.insert("", "end", values=(idx, record["Title"], record["Date"], record["Time"]))


def save_edit():
    selected_item = tree.selection()
    if selected_item:
        record_id = int(tree.item(selected_item[0])['values'][0]) - 1
        title = title_entry.get()
        date = date_entry.get()
        hour = hour_spinbox.get()
        min = minute_spinbox.get()
        try:
            datetime.strptime(date + " " + hour + ":" + min, "%d/%m/%Y %H:%M")
        except ValueError:
            error_label.config(text="Некоректна дата або час")
            return
        if len(hour) == 1:
            hour = '0' + hour
        if len(min) == 1:
            min = '0' + min
        records[record_id] = {"Title": title, "Date": date, "Time": hour + ":" + min}
        update_table()
        clear_fields()
        error_label.config(text="")
        schedule_notification(date, hour, min, title, record_id)


# Функція для видалення запису
def delete_record():
    selected_item = tree.selection()
    if selected_item:
        records.pop(int(tree.item(selected_item[0])['values'][0]) - 1)
        update_table()
    else:
        showinfo('Інформація',
                 'Для видалення потрібно натиснути на рядок, який потрібно видалити і знову натиснути кнопку "Видалити".')


# Функція для очищення полів вводу
def clear_fields():
    title_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    hour_spinbox.delete(0, tk.END)
    minute_spinbox.delete(0, tk.END)


# Функція для створення push-сповіщення
def create_notification(title, rec_id):
    toaster = ToastNotifier()
    toaster.show_toast("Записник з нагадуваннями", title, duration=10, icon_path='') # icon_path костиль
    records.pop(rec_id)
    update_table()
    return schedule.CancelJob


def schedule_notification(date, hour, min, title, rec_id=None):
    event_datetime = datetime.strptime(date + " " + hour + ":" + min, "%d/%m/%Y %H:%M")
    current_datetime = datetime.now()

    if current_datetime < event_datetime:
        time_difference = event_datetime - current_datetime
        seconds_until_event = time_difference.total_seconds()
        if rec_id != None:
            schedule.cancel_job(tasks[rec_id])
            tasks.insert(rec_id, schedule.every(int(seconds_until_event)).seconds.do(
                lambda: create_notification(title, rec_id))
                         )
        else:
            tasks.append(schedule.every(int(seconds_until_event)).seconds.do(
                lambda: create_notification(title, len(tasks) - 1)
            ))


# Функція для запуску розкладу подій у окремому потоці
def run_schedule_thread():
    while not stop:
        schedule.run_pending()
        time.sleep(1)


def edit_record():
    selected_item = tree.selection()
    if selected_item:
        record_id = int(tree.item(selected_item[0])['values'][0]) - 1
        record = records[record_id]
        title_entry.insert(0, record.get("Title", ""))
        date_entry.set_date(record.get("Date", ""))
        time_hrs_min = record['Time'].split(':')
        hour_spinbox.delete(0, tk.END)
        hour_spinbox.insert(0, time_hrs_min[0])
        minute_spinbox.delete(0, tk.END)
        minute_spinbox.insert(0, time_hrs_min[1])
    else:
        showinfo('Інформація',
                 'Для редагування потрібно натиснути на рядок, який потрібно змінити і знову натиснути кнопку "Редагувати". Після внесення змін потрібно натиснути кнопку "Зберегти".')


def finish():
    global stop
    stop = True
    root.destroy()


# Головне вікно
root = tk.Tk()
root.title("Записник з нагадуваннями")
root.protocol("WM_DELETE_WINDOW", finish)

# Заголовок
title_label = tk.Label(root, text="Записник з нагадуваннями", font=("Helvetica", 16))
title_label.pack(pady=10)

# Таблиця
columns = ("№", "Запис", "Дата", "Час")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree.column(col, anchor=tk.CENTER)
    tree.heading(col, text=col)
tree.pack()

# Поля вводу
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)

title_label = tk.Label(entry_frame, text="Запис:")
title_label.grid(row=0, column=2, padx=5)

title_entry = tk.Entry(entry_frame)
title_entry.grid(row=0, column=3, padx=5)

date_label = tk.Label(entry_frame, text="Дата:")
date_label.grid(row=0, column=4, padx=5)

date_entry = DateEntry(entry_frame, width=12, borderwidth=2, date_pattern='dd/MM/yyyy')
date_entry.grid(row=0, column=5, padx=5)

'''''
validation
'''''


def validate_time(hours):
    if hours == "":
        return True
    if hours.isdigit():
        if 0 <= int(hours) <= 23:
            time_str.set(hours)
            return True
        else:
            return False
    else:
        return False


def validate_time_min(min):
    if min == "":
        return True
    if min.isdigit():
        if 0 <= int(min) <= 59:
            time_str.set(' : ' + str(min))
            return True
        else:
            return False
    else:
        return False


''''''
''''''
time_str = tk.StringVar()

# Spinbox для вводу годин
hour_spinbox = tk.Spinbox(entry_frame, from_=0, to=23, width=2, justify=tk.RIGHT, validate="all",
                          validatecommand=(entry_frame.register(validate_time), "%P"))
hour_spinbox.grid(row=0, column=7, padx=5, pady=5)
tk.Label(entry_frame, text="годин").grid(row=0, column=6, padx=5, pady=5)

# Spinbox для вводу хвилин
minute_spinbox = tk.Spinbox(entry_frame, from_=0, to=59, width=2, justify=tk.RIGHT, validate="all",
                            validatecommand=(entry_frame.register(validate_time_min), "%P"))
minute_spinbox.grid(row=0, column=9, padx=5, pady=5)
tk.Label(entry_frame, text="хвилин").grid(row=0, column=8, padx=5, pady=5)

###
# Кнопки
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Додати", command=add_record)
add_button.grid(row=0, column=0, padx=5)

delete_button = tk.Button(button_frame, text="Видалити", command=delete_record)
delete_button.grid(row=0, column=1, padx=5)

edit_button = tk.Button(button_frame, text="Редагувати", command=edit_record)
edit_button.grid(row=0, column=2, padx=5)

save_button = tk.Button(button_frame, text="Зберегти", command=save_edit)
save_button.grid(row=0, column=3, padx=5)

# Помилка
error_label = tk.Label(root, text="", fg="red")
error_label.pack(pady=5)

# Запуск розкладу подій у окремому потоці
schedule_thread = threading.Thread(target=run_schedule_thread)
schedule_thread.start()

# Запуск GUI
root.mainloop()
