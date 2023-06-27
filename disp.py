from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font
from utils import *


class MainWindow:
    def __init__(self, root) -> None:
        self.root = root

        self.style = ttk.Style()
        self.style.configure('my.TButton', font=('helvetica', 35))
        # self.large_button_font = font.Font(size=35)

        # Frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame['padding'] = 5
        self.main_frame.pack()

        # Menu Stuff
        root.option_add('*tearOff', FALSE)
        self.menubar = Menu(root)
        root['menu'] = self.menubar

        # File Menu
        self.menu_file = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menu_file.add_command(label='Open Set...', command=self.placeholder_command)
        self.menu_file.add_command(label='Save Set', command=self.placeholder_command)
        self.menu_file.add_command(label='Save Set As...', command=self.placeholder_command)

        # Documents Submenu
        self.menu_documents = Menu(self.menu_file)
        self.menu_documents.add_command(label='Add Document Type...', command=self.placeholder_command)
        self.menu_documents.add_command(label='Add Document Set...', command=self.placeholder_command)
        self.menu_documents.add_command(label='Remove Document Type', command=self.placeholder_command)
        
        # Authors Submenu
        self.menu_authors = Menu(self.menu_file)
        self.menu_authors.add_command(label='Add Author Style...', command=self.placeholder_command)
        self.menu_authors.add_command(label='Assign Author Style...', command=self.placeholder_command)

        # Adding Submenus to File Menu
        self.menu_file.add_cascade(label='Document Types', menu=self.menu_documents)
        self.menu_file.add_cascade(label='Author Styles', menu=self.menu_authors)

        # Edit Menu
        self.menu_edit = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menu_edit.add_command(label='Generate', command=self.placeholder_command)
        
        # GUI - Frames
        


    def placeholder_command(self):
        pass