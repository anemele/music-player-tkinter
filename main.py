"""
20201206
"""

import os
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter.scrolledtext import ScrolledText

import pygame


class MusicPlayer(tk.Tk):
    def __init__(self, path):
        if not os.path.exists(path):
            print(f'PathNotExistsError: {path}')
            return
        self.path = path

        super(MusicPlayer, self).__init__()

        self.playing = False
        self.types = ('.mp3', '.flac')  # 支持的音乐格式
        self.lyric_encoding = ('utf-8', 'gbk', 'gb2312')  # 支持的歌词编码格式
        self.dic = dict()  # self.music_list
        self.thread_pool = ThreadPoolExecutor()

        self.geometry('1000x600+200+100')
        self.title('Music Player')
        self.iconbitmap('music.ico')  # 转换为ico格式才可以作图标，方法见文末
        self.resizable(False, False)

        self.choices = tk.LabelFrame(self)
        self.lyrics = tk.LabelFrame(self)
        self.buttons = tk.LabelFrame(self)
        self.decoration = tk.LabelFrame(self)
        self.short_info = tk.Frame(self)

        self.info = tk.Label(self.choices)
        self.music_listbox = tk.Listbox(self.choices,
                                        width=42,
                                        height=25,
                                        selectmode=tk.SINGLE)
        self.mlb_y_scrollbar = tk.Scrollbar(self.choices,
                                            command=self.music_listbox.yview)
        self.mlb_x_scrollbar = tk.Scrollbar(self.choices,
                                            orient=tk.HORIZONTAL,
                                            command=self.music_listbox.xview)

        self.music_title = tk.Label(self.short_info,
                                    text='歌名',
                                    width=80,
                                    font=('华文楷书', 10))
        self.lyric_line = tk.Label(self.short_info,
                                   text='歌词',
                                   font=('华文楷书', 10),
                                   fg='green')
        self.lyric = ScrolledText(self.lyrics)
        self.hello = tk.Label(self.decoration,
                              text='Hello world!',
                              font=('华文隶书', 16),
                              fg='red')
        self.label = tk.Label(self.decoration,
                              text='Please select a music.',
                              font=('华文楷书', 10),
                              fg='blue')
        self.prev_music = tk.Button(self.buttons, text='上一首')
        self.pause_button = tk.Button(self.buttons,
                                      text='暂 停',
                                      # state='disabled',
                                      command=self.pause,
                                      fg='green')
        self.next_music = tk.Button(self.buttons, text='下一首')

        self.set_gui()
        self.config_gui()

        self.add_music()

        pygame.mixer.init()

    def run(self):
        self.mainloop()

    def set_gui(self):
        # Frame
        self.choices.place(x=30, y=30)
        self.lyrics.place(x=400, y=150)
        self.buttons.place(x=640, y=500)
        self.decoration.place(x=620, y=30)
        self.short_info.place(x=400, y=100)
        # Label
        self.info.pack()
        self.hello.pack()
        self.label.pack()
        self.music_title.pack()
        self.lyric_line.pack()
        # Listbox
        self.mlb_y_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.mlb_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.music_listbox.pack()  # 务必放在scrollbar末尾
        # Scroll-text
        self.lyric.pack()
        # Button
        self.prev_music.grid(row=0, column=0)
        self.pause_button.grid(row=0, column=1, padx=5)
        self.next_music.grid(row=0, column=2)

    def config_gui(self):
        self.music_listbox.bind(
            # "<<ListboxSelection>>",
            # "<ButtonRelease-1>",
            "<Double-Button-1>",  # 双击鼠标
            self.select)
        # 与Listbox联动
        self.music_listbox.config(xscrollcommand=self.mlb_x_scrollbar.set,
                                  yscrollcommand=self.mlb_y_scrollbar.set)

    def add_music(self):
        for t, ds, fs in os.walk(self.path):
            for file in fs:
                if os.path.splitext(file)[1] in self.types:
                    self.dic[file] = t
                    self.music_listbox.insert('end', file)
        self.info.config(text=f"检索完毕！共搜索到音频文件 {len(self.dic)} 个。")

    def pause(self):
        if pygame.mixer.music.get_busy() and self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.pause_button.config(text='播 放')
        else:
            pygame.mixer.music.unpause()
            self.playing = True
            self.pause_button.config(text='暂 停')

    def play(self, music):
        if not os.path.exists(music):
            return
        # self.pause_button['state'] = 'normal'
        pygame.mixer.music.load(music)
        pygame.mixer.music.play()
        self.playing = True
        self.pause_button.config(text='暂 停')

    def select(self, event):
        music = self.music_listbox.get(self.music_listbox.curselection())
        path = os.path.join(self.dic[music], music)
        self.music_title.config(text=music)
        self.thread_pool.submit(self.play, path)
        self.thread_pool.submit(self.load_lyric, path)

    def set_lyric(self, lyric_text):
        self.lyric.config(state=tk.NORMAL)
        self.lyric.delete('1.0', tk.END)  # 清空内容
        self.lyric.insert(tk.END, lyric_text)  # 插入新内容
        self.lyric.config(state=tk.DISABLED)

    def reset_lyric(self):
        self.set_lyric('暂无歌词')
        self.lyric_line.config(text='暂无歌词')

    def active_lyric(self, lyric_lines):
        # 每隔一段时间，更新歌词框
        times = tuple(lyric_lines)
        time.sleep(times[0])
        self.lyric_line.config(text=lyric_lines[times[0]])
        for index in range(1, len(times)):
            time.sleep(times[index] - times[index - 1])
            self.lyric_line.config(text=lyric_lines[times[index]])

    def read_lyric(self, path):
        # 自动选择编码格式
        for encoding in self.lyric_encoding:
            try:
                with open(path, encoding=encoding) as lyric:
                    return lyric.read()  # 歌词内容
            except UnicodeDecodeError:
                pass

    def load_lyric(self, path):
        lyric_path = '%s.lrc' % os.path.splitext(path)[0]
        if os.path.exists(lyric_path):
            lyric_text = self.read_lyric(lyric_path)
            if lyric_text is None:
                self.reset_lyric()
                return
            lyric_lines = dict()
            for line in lyric_text.strip().split('\n'):
                times, lyric = line.split(']')
                m, s = times[1:].split(':')
                if not m.isdigit():  # 过滤非时间点
                    continue
                lyric_lines[int(m) * 60 + float(s)] = lyric
            self.set_lyric('\n'.join(lyric_lines.values()))
            self.active_lyric(lyric_lines, )
        else:
            self.reset_lyric()


if __name__ == '__main__':
    player = MusicPlayer('D:/Music')
    player.run()
