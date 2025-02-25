# Калькулятор
from tkinter import *
operation, first_value, value = '', '', ''


def set(value):
    entry.delete(0, END)
    if '.' in str(value) and str(value)[len(str(value)) - 1] != '0':
        entry.insert(0, str(round(float(value), 12)))
    else:
        entry.insert(0, str(int(value)))
def set_symbol(value):
    entry.delete(0, END)
    entry.insert(0, value)
def click(symbol):
    global operation, first_value, value
    value = entry.get()
    if symbol in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        if value[0] in ['0', '+', '-', '×', '÷', '%'] and '.' not in value:
            value = value[1:]
        set_symbol(value + symbol)
    elif symbol == ',':
        set_symbol(value + '.')
    elif symbol == '⌫':
        if len(value) > 1:
            set(value[:-1])
        else:
            if value[0] in ['+', '-', '×', '÷', '%']:
                set(first_value)
            else:
                set_symbol('0')
    elif symbol == 'С':
        first_value = 0
        set_symbol('0')
    elif symbol == 'СЕ':
        set_symbol('0')
    else:
        value = float(value)
        if symbol == 'x²':
            value = value**2
            set(value)
        elif symbol == '√':
            if value > 0:
                value = value**0.5
                set(value)
            else:
                set_symbol('Ошибка ввода!')
        elif symbol == '1/x':
            value = 1/value
            set(value)
        elif symbol == '±':
            set(-value)
        elif symbol == '=':
            entry.delete(0, END)
            if operation == '+':
                value = value + first_value
                set(value)
            if operation == '-':
                value = first_value - value
                set(value)
            if operation == '×':
                value = first_value * value
                set(value)
            if operation == '÷':
                if value == 0:
                    set_symbol('Ошибка ввода!')
                else:
                    value = first_value / value
                    set(value)
            if operation == '%':
                value = (value / 100) * first_value
                set(value)
            if operation == '':
                set(value)
        else:
            first_value = float(value)
            if symbol in ['+', '-', '×', '÷', '%']:
                operation = symbol
                set_symbol(symbol)
window = Tk()
W, H = 330, 390
L, T = (window.winfo_screenwidth()-W)//2, (window.winfo_screenheight()-H)//2
window.geometry(f"{W}x{H}+{L}+{T}")
window.title('Калькулятор')
entry = Entry(bg='light blue', justify=RIGHT,  font=('Arial', 18, 'bold'))
entry.grid(row=0, column=0, columnspan=4, sticky="NSEW")
entry.insert(0, '0')
buttons = [['%', '√', 'x²', '1/x'], ['СЕ', 'С', '⌫', '÷'], ['7', '8', '9', '×'], ['4', '5', '6', '-'], ['1', '2', '3', '+'], ['±', '0', ',', '=']]
for x in range(7):
    window.rowconfigure(x, weight=1)
    for x in range(1, 7):
        for y in range(4):
            command = lambda t=buttons[x-1][y]: click(t)
            window.columnconfigure(y, weight=1)
            Button(window, text=buttons[x-1][y], bg='light blue', borderwidth=0, font=('Arial', 12, 'bold'), command=command).grid(row=x, column=y, padx=1, pady=1,sticky="NSEW")
window.mainloop()