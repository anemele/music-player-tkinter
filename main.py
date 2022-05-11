"""
20201206
"""

import os
import time
import tkinter as tk
from tkinter import ttk
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
        self.types = ('.mp3', '.flac')  # 支持的格式
        self.dic = dict()  # self.music_list

        self.geometry('1000x600+200+100')
        self.title('Music Player')
        self.iconbitmap('music.ico')  # 转换为ico格式才可以作图标，方法见文末
        self.resizable(False, False)

        self.choices = tk.LabelFrame(self)
        self.lyrics = tk.LabelFrame(self)
        self.buttons = tk.LabelFrame(self)
        self.decoration = tk.LabelFrame(self)

        self.info = tk.Label(self.choices)
        self.cmb = ttk.Combobox(self.choices, width=45)
        self.lyric_line = tk.Label(self.lyrics,
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
        self.choices.place(x=30, y=30)
        self.lyrics.place(x=400, y=100)
        self.buttons.place(x=640, y=500)
        self.decoration.place(x=620, y=30)
        self.info.pack()
        self.cmb.pack()
        self.lyric_line.pack()
        self.lyric.pack()
        self.hello.pack()
        self.label.pack()
        self.prev_music.grid(row=0, column=0)
        self.pause_button.grid(row=0, column=2)
        self.next_music.grid(row=0, column=4)

    def config_gui(self):
        self.cmb['state'] = 'readonly'
        self.cmb.bind("<<ComboboxSelected>>", self.select)

    def add_music(self):
        temp_list = []
        for t, ds, fs in os.walk(self.path):
            for file in fs:
                if os.path.splitext(file)[1] in self.types:
                    temp_list.append(file)
                    self.dic[file] = t
        self.cmb['value'] = temp_list
        self.info.config(text=f"检索完毕！共搜索到音频文件{len(self.dic)}个。")
        # print(f"检索完毕！共搜索到音频文件{len(self.dic)}个。")

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
        music = self.cmb.get()
        path = os.path.join(self.dic[music], music)
        self.play(path)
        lyric_lines = self.add_lyric(path)
        self.active_lyric(lyric_lines)

    def add_lyric(self, music):
        self.lyric.delete('1.0', 'end')  # 清空内容
        path = '%s.lrc' % os.path.splitext(music)[0]
        if os.path.exists(path):
            with open(path, encoding='utf8') as lyric:
                lyric_text = lyric.read()  # 歌词内容
            self.lyric.insert('end', lyric_text)
            return lyric_text.strip().split('\n')
        else:
            self.lyric.insert('end', '暂无歌词')
            return []

    def active_lyric(self, ll):
        start = time.perf_counter()
        for lyric in ll:
            m_s, lrc = lyric[1:].split(']')
            m, s = m_s.split(':')
            add_time = eval('%.6f' % (start + int(m) * 60 + eval(s)))

            # while 循环随着时间积累产生误差会不同步甚至陷入死循环、停滞
            # 还存在问题，暂停后歌词不暂停。
            while True:
                if abs(time.perf_counter() - add_time) < 1e-3:  # 浮点误差法
                    self.lyric_line['text'] = lrc
                    break


if __name__ == '__main__':
    player = MusicPlayer('D:/Music')
    player.run()
