import pathlib
import tkinter as tk
from tkinter import ttk


class ChoiceFrame(tk.LabelFrame):

    def __init__(self, master, **kw):
        super(ChoiceFrame, self).__init__(master, **kw)
        self.info = tk.Label(self, text='正在加载...')
        self.music_listbox = tk.Listbox(self, width=42, height=20, selectmode=tk.EXTENDED)
        self.mlb_y_scrollbar = tk.Scrollbar(self, command=self.music_listbox.yview)
        self.mlb_x_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.music_listbox.xview)

        self.config_gui()
        self.layout_gui()

    def config_gui(self):
        self.music_listbox.config(xscrollcommand=self.mlb_x_scrollbar.set,
                                  yscrollcommand=self.mlb_y_scrollbar.set)

    def layout_gui(self):
        self.info.pack()
        self.mlb_y_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.mlb_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.music_listbox.pack()  # 务必放在scrollbar末尾


class DecorationFrame(tk.LabelFrame):

    def __init__(self, master, **kw):
        super(DecorationFrame, self).__init__(master, **kw)

        self.hello = tk.Label(self, text='Hello world!', font=('华文隶书', 16), fg='red')
        self.label = tk.Label(self, text='Please select a music.', font=('华文行楷', 10), fg='blue')

        self.layout_gui()

    def layout_gui(self):
        self.hello.pack()
        self.label.pack()


class ShowMusicFrame(tk.LabelFrame):

    def __init__(self, master, **kw):
        super(ShowMusicFrame, self).__init__(master, **kw)

        self.music_title = tk.Label(self, text='歌名',
                                    width=80,  # 保持 lyric_listbox 不变形
                                    font=('华文仿宋', 10),
                                    fg='#800080')

        self.lyric_listbox = tk.Listbox(self, width=80, height=16)
        self.llb_y_scrollbar = tk.Scrollbar(self, command=self.lyric_listbox.yview)
        self.llb_x_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.lyric_listbox.xview)

        self.config_gui()
        self.layout_gui()

    def config_gui(self):
        # 与Listbox联动
        self.lyric_listbox.config(xscrollcommand=self.llb_x_scrollbar.set,
                                  yscrollcommand=self.llb_y_scrollbar.set)

    def layout_gui(self):
        self.music_title.pack()
        self.llb_y_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.llb_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.lyric_listbox.pack()


class ButtonFrame(tk.LabelFrame):

    def __init__(self, master, **kw):
        super(ButtonFrame, self).__init__(master, **kw)

        self.add_music_button = ttk.Button(self, text='添 加', width=5)
        self.remove_music_button = ttk.Button(self, text='删 除', width=5)
        self.play_mode_box = ttk.Combobox(self, width=7,
                                          state=tk.DISABLED  # 'readonly'
                                          )
        self.pause_button = ttk.Button(self, text='暂 停', width=5, state=tk.DISABLED)

        self.set_time_scale = tk.Scale(self,
                                       label='播放进度（禁用）',
                                       from_=0, to=100,
                                       width=5, length=360,
                                       orient=tk.HORIZONTAL,
                                       sliderlength=10,
                                       digits=False,
                                       state=tk.DISABLED
                                       )
        self.set_volume_scale = ttk.Scale(self)

        self.layout_gui()

    def layout_gui(self):
        self.add_music_button.grid(row=0, column=0, padx=5, pady=5)
        self.remove_music_button.grid(row=0, column=1, padx=5, pady=5)
        self.play_mode_box.grid(row=0, column=2, padx=5)
        self.pause_button.grid(row=0, column=3, padx=5)
        self.set_time_scale.grid(row=0, column=4, padx=5, pady=5)
        self.set_volume_scale.grid(row=0, column=5, padx=5, pady=5)


class MainGUI(tk.Tk):

    def __init__(self):
        super().__init__()

        # Frame
        self.choices = ChoiceFrame(self)
        self.show_music = ShowMusicFrame(self)
        self.buttons = ButtonFrame(self)
        self.decoration = DecorationFrame(self)
        self.short_info = tk.Frame(self)

        self.config_gui()
        self.layout_gui()

    def run(self):
        self.mainloop()

    def config_gui(self):
        self.geometry('1000x600+200+100')
        self.title('Music Player')
        icon = pathlib.Path(__file__).parent / 'music.ico'
        self.iconbitmap(icon)  # 转换为ico格式才可以作图标，方法见文末
        self.resizable(False, False)

    def layout_gui(self):
        self.choices.place(x=30, y=70)
        self.show_music.place(x=380, y=100)
        self.buttons.place(x=100, y=500)
        self.decoration.place(x=120, y=10)
        self.short_info.place(x=400, y=100)


if __name__ == '__main__':
    MainGUI().run()
