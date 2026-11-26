import tkinter as tk
from controller import ClinicaController
from interface_tkinter import SistemaClinicaApp


def main():
    root = tk.Tk()
    controller = ClinicaController()
    SistemaClinicaApp(root, controller)
    root.mainloop()


if __name__ == "__main__":
    main()
