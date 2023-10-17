from application import Application
import easygui


def main():
    filepath = easygui.fileopenbox(default="*.xlsx")
    save_filepath = easygui.diropenbox(msg="Папка куда сохранить результаты")

    app = Application(filepath, save_filepath)
    app.run()


if __name__ == '__main__':
    main()

