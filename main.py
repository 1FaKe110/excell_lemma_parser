from application import Application
from application import ErrorMessageBox
import easygui


def main():
    filepath = easygui.fileopenbox(msg="Файл с исходными данными", default="*.xlsx")
    if filepath is None:
        message = "Не указан файл с исходными данными"
        ErrorMessageBox(message)
        raise SystemExit(message)

    save_filepath = easygui.diropenbox(msg="Папка куда сохранить результаты")
    if save_filepath is None:
        message = "Не указана директория для сохранения результатов"
        ErrorMessageBox(message)
        raise SystemExit(message)

    app = Application(filepath, save_filepath)
    app.run()


if __name__ == '__main__':
    main()

