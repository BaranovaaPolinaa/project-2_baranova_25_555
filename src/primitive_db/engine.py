from prompt_toolkit import prompt


def welcome():
    """
    Приветственная функция с интерактивным циклом команд,
    использующая prompt_toolkit для ввода.
    """
    print("Первая попытка запустить проект!\n")
    print("\n<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        command = prompt("Введите команду: ").strip().lower()

        if command == "exit":
            print("Выход из программы...")
            break
        elif command == "help":
            print("\n<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        elif command == "":
            continue
        else:
            print(f"Неизвестная команда: {command}")
