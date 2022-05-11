"""
20201216
"""
import json
import os
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog as fdl
from tkinter import messagebox as mb
from tkinter import ttk

import pygame


class MusicPlayer(tk.Tk):
    def __init__(self, path):
        if not os.path.exists(path):
            print(f'PathNotExistsError: {path}')
            return
        self.path = path

        super(MusicPlayer, self).__init__()
        self.protocol('WM_DELETE_WINDOW', self.exit)

        self.playing = False
        self.types = ('.mp3', '.flac')  # 支持的音乐格式
        self.lyric_encoding = ('utf-8', 'gbk', 'gb2312')  # 支持的歌词编码格式
        self.music_list_file = 'music-list.json'
        self.music_list = []
        self.thread_pool = ThreadPoolExecutor()

        self.geometry('1000x600+200+100')
        self.title('Music Player')
        self.iconbitmap('music.ico')  # 转换为ico格式才可以作图标，方法见文末
        self.resizable(False, False)

        # Frame
        self.choices = tk.LabelFrame(self)
        self.show_music = tk.LabelFrame(self)
        self.buttons = tk.LabelFrame(self)
        self.decoration = tk.LabelFrame(self)
        self.short_info = tk.Frame(self)

        # Label
        self.info = tk.Label(self.choices, text='正在加载...')
        self.hello = tk.Label(self.decoration,
                              text='Hello world!',
                              font=('华文隶书', 16),
                              fg='red')
        self.label = tk.Label(self.decoration,
                              text='Please select a music.',
                              font=('华文楷书', 10),
                              fg='blue')
        self.music_title = tk.Label(self.show_music,
                                    text='歌名',
                                    width=80,  # 保持lyric_listbox不变形
                                    font=('华文楷书', 10))
        # Listbox
        self.music_listbox = tk.Listbox(self.choices,
                                        width=42,
                                        height=20,
                                        selectmode=tk.EXTENDED)
        self.mlb_y_scrollbar = tk.Scrollbar(self.choices,
                                            command=self.music_listbox.yview)
        self.mlb_x_scrollbar = tk.Scrollbar(self.choices,
                                            orient=tk.HORIZONTAL,
                                            command=self.music_listbox.xview)
        self.lyric_listbox = tk.Listbox(self.show_music, width=80, height=16)
        self.llb_y_scrollbar = tk.Scrollbar(self.show_music,
                                            command=self.lyric_listbox.yview)
        self.llb_x_scrollbar = tk.Scrollbar(self.show_music,
                                            orient=tk.HORIZONTAL,
                                            command=self.lyric_listbox.xview)
        # Button
        self.add_music_button = ttk.Button(self.buttons,
                                           text='添 加',
                                           width=5)
        self.remove_music_button = ttk.Button(self.buttons,
                                              text='删 除',
                                              width=5)
        # Scale
        self.set_time_scale = tk.Scale(self.buttons,
                                       label='播放进度（禁用）',
                                       from_=0, to=100,
                                       width=5, length=360,
                                       orient=tk.HORIZONTAL,
                                       sliderlength=10,
                                       digits=False
                                       )
        self.set_volume_scale = ttk.Scale(self.buttons)

        self.set_gui()
        self.config_gui()

        self.thread_pool.submit(self.load_music_list)

        pygame.mixer.init()
        # 初始音量
        self.set_volume(0.5)
        self.set_volume_scale.set(0.5)

    def run(self):
        self.mainloop()

    def exit(self):
        msg = mb.askyesnocancel('退出', '是否保存播放列表？')
        if msg is None:
            return
        elif msg:
            json.dump(self.music_list, open(self.music_list_file, 'w'))

        pygame.mixer.music.stop()
        # self.thread_pool.shutdown()  # 此处会无响应
        self.destroy()

    def set_gui(self):
        # Frame
        self.choices.place(x=30, y=70)
        self.show_music.place(x=380, y=100)
        self.buttons.place(x=200, y=500)
        self.decoration.place(x=120, y=10)
        self.short_info.place(x=400, y=100)
        # Label
        self.info.pack()
        self.hello.pack()
        self.label.pack()
        self.music_title.pack()
        # Listbox
        self.mlb_y_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.mlb_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.music_listbox.pack()  # 务必放在scrollbar末尾
        self.llb_y_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.llb_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.lyric_listbox.pack()
        # Button
        self.add_music_button.grid(row=0, column=0, padx=5, pady=5)
        self.remove_music_button.grid(row=0, column=1, padx=5, pady=5)
        self.set_time_scale.grid(row=0, column=2, padx=5, pady=5)
        self.set_volume_scale.grid(row=0, column=3, padx=5, pady=5)

    def config_gui(self):
        self.music_listbox.bind(
            # "<<ListboxSelection>>",
            # "<ButtonRelease-1>",
            "<Double-Button-1>",  # 双击鼠标
            self.select)
        # 与Listbox联动
        self.music_listbox.config(xscrollcommand=self.mlb_x_scrollbar.set,
                                  yscrollcommand=self.mlb_y_scrollbar.set)
        self.lyric_listbox.config(xscrollcommand=self.llb_x_scrollbar.set,
                                  yscrollcommand=self.llb_y_scrollbar.set)
        self.add_music_button.config(command=lambda: self.add_music(fdl.askdirectory(initialdir=self.path)))
        self.remove_music_button.config(command=self.remove_music)
        self.set_volume_scale.config(command=self.set_volume)

    def load_music_list(self):
        if os.path.exists(self.music_list_file):
            try:
                self.music_list = json.load(open(self.music_list_file, 'rb'))
                for music in self.music_list:
                    self.music_listbox.insert(tk.END, os.path.basename(music))
                self.info.config(text=f"加载完毕！共有音频文件 {len(self.music_list)} 个。")
            except json.decoder.JSONDecodeError:
                self.add_music(self.path)
        else:
            self.add_music(self.path)

    def add_music(self, path):
        if path is None:
            return
        count = 0
        for t, ds, fs in os.walk(path):
            for file in fs:
                if os.path.splitext(file)[1] in self.types:
                    self.music_list.append(os.path.join(t, file))
                    self.music_listbox.insert('end', file)
                    count += 1
        self.info.config(text=f"检索完毕！共搜索到音频文件 {count} 个。")

    def remove_music(self):
        index = self.music_listbox.curselection()
        if bool(index):
            self.music_list.pop(index[0])
            self.music_listbox.delete(index[0])

    def pause(self):
        if pygame.mixer.music.get_busy() and self.playing:
            pygame.mixer.music.pause()
            self.playing = False
        else:
            pygame.mixer.music.unpause()
            self.playing = True

    def play(self, music):
        if not os.path.exists(music):
            return
        # self.pause_button['state'] = 'normal'
        pygame.mixer.music.load(music)
        pygame.mixer.music.play()
        self.playing = True

    @staticmethod
    def set_volume(value):
        pygame.mixer.music.set_volume(float(value))

    def select(self, event):
        index = self.music_listbox.curselection()
        if bool(index):
            path = self.music_list[index[0]]
            # 判断列表音乐是否存在
            if os.path.exists(path):
                self.music_title.config(text=os.path.basename(path))
                self.thread_pool.submit(self.play, path)
                self.thread_pool.submit(self.load_lyric, path)
            else:
                if mb.askyesno('无效文件', '是否删除？'):
                    self.remove_music()

    def set_lyric(self, lyric_list):
        self.lyric_listbox.delete(0, tk.END)  # 清空内容
        self.lyric_listbox.insert(tk.END, *lyric_list)  # 插入新内容

    def reset_lyric(self):
        self.set_lyric(('暂无歌词',))

    def active_lyric(self, index, max_len, start_perf, timer):
        # 每隔一段时间，更新歌词框
        if index >= max_len:
            return
        if abs(time.perf_counter() - start_perf - timer[index]) > 5e-2:
            self.after(10, lambda: self.active_lyric(index, max_len, start_perf, timer))
            return
        self.lyric_listbox.see(index + 1)  # 正在播放歌词
        self.lyric_listbox.itemconfig(index, fg='black', bg='white')
        self.lyric_listbox.itemconfig(index + 1, fg='green', bg='silver')
        self.after(20, lambda: self.active_lyric(index + 1, max_len, start_perf, timer))

    def read_file(self, path):
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
            lyric_text = self.read_file(lyric_path)
            if lyric_text is None:
                self.reset_lyric()
                return
            timer = []
            lyric_lines = ['']
            for line in lyric_text.strip().split('\n'):
                times, lyric = line.split(']')
                m, s = times[1:].split(':')
                if not m.isdigit():  # 过滤非时间点
                    continue
                timer.append(int(m) * 60 + float(s))
                lyric_lines.append(lyric)
            self.set_lyric(lyric_lines)
            self.active_lyric(0, len(timer), time.perf_counter(), timer)
        else:
            self.reset_lyric()


if __name__ == '__main__':
    player = MusicPlayer('D:/Music')
    player.run()
