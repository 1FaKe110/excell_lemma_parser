from application import Application
import easygui


def main():
    filepath = easygui.fileopenbox(default="*.xlsx")

    app = Application(filepath)
    app.run()


if __name__ == '__main__':
    main()
