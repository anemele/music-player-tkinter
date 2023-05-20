import json
import os
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox, filedialog

import pygame

from .gui import MainGUI


class Player(MainGUI):
    def __init__(self, path):
        if not os.path.exists(path):
            print(f'PathNotExistsError: {path}')
            return

        super().__init__()
        super(Player, self).config()

        self.path = path

        self.protocol('WM_DELETE_WINDOW', self.exit)
        self.playing = False
        self.types = ('.mp3', '.flac')  # 支持的音乐格式
        self.lyric_encoding = ('utf-8', 'gbk', 'gb2312')  # 支持的歌词编码格式
        self.music_list_file = 'music-list.json'
        self.music_list = []
        self.thread_pool = ThreadPoolExecutor()

        self.thread_pool.submit(self.load_music_list)

        pygame.mixer.init()
        # 初始音量
        self.set_volume(0.5)
        self.buttons.set_volume_scale.set(0.5)

        super(Player, self).config_gui()
        self.config_gui()

    def exit(self):
        msg = messagebox.askyesnocancel('退出', '是否保存播放列表？')
        if msg is None:
            return
        elif msg:
            json.dump(self.music_list, open(self.music_list_file, 'w'))

        pygame.mixer.music.stop()
        # self.thread_pool.shutdown()  # 此处会无响应
        self.destroy()

    def config_gui(self):
        self.choices.music_listbox.bind(
            # "<<ListboxSelection>>",
            # "<ButtonRelease-1>",
            "<Double-Button-1>",  # 双击鼠标
            self.select,
        )
        self.buttons.add_music_button.config(
            command=lambda: self.add_music(
                filedialog.askdirectory(initialdir=self.path)
            )
        )
        self.buttons.remove_music_button.config(command=self.remove_music)
        self.buttons.play_mode_box.config(values=('顺序播放', '循环播放', '单曲循环', '随机播放'))
        self.buttons.play_mode_box.current(0)
        self.buttons.set_volume_scale.config(command=self.set_volume)

    def load_music_list(self):
        if os.path.exists(self.music_list_file):
            try:
                self.music_list = json.load(open(self.music_list_file, 'rb'))
                for music in self.music_list:
                    self.choices.insert_name(os.path.basename(music))
                self.short_info.info.config(
                    text=f"加载完毕！共有音频文件 {len(self.music_list)} 个。"
                )
            except json.decoder.JSONDecodeError:
                self.add_music(self.path)
        else:
            self.add_music(self.path)

    def add_music(self, path):
        if path is None:
            return
        count = 0
        for t, _, fs in os.walk(path):
            for file in fs:
                if os.path.splitext(file)[1] in self.types:
                    self.music_list.append(os.path.join(t, file))
                    self.choices.music_listbox.insert('end', file)
                    count += 1
        self.short_info.info.config(text=f"检索完毕！共搜索到音频文件 {count} 个。")

    def remove_music(self):
        index = self.choices.music_listbox.curselection()
        if bool(index):
            self.music_list.pop(index[0])
            self.choices.music_listbox.delete(index[0])

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

    def select(self, _):
        index = self.choices.music_listbox.curselection()
        if not index:
            return
        path = self.music_list[index[0]]
        # 判断列表音乐是否存在
        if os.path.exists(path):
            self.show_music.music_title.config(text=pathlib.Path(path).name)
            self.thread_pool.submit(self.play, path)
            self.thread_pool.submit(self.load_lyric, path)
        elif messagebox.askyesno('无效文件', '是否删除？'):
            self.remove_music()

    def reset_lyric(self):
        self.show_music.set_lyric(('暂无歌词',))

    def active_lyric(self, index, max_len, start_perf, timer):
        # 每隔一段时间，更新歌词框
        if index >= max_len:
            return
        if abs(time.perf_counter() - start_perf - timer[index]) > 5e-2:
            self.after(10, lambda: self.active_lyric(index, max_len, start_perf, timer))
            return
        self.show_music.lyric_listbox.see(index + 1)  # 正在播放歌词
        self.show_music.lyric_listbox.itemconfig(index, fg='black', bg='white')
        self.show_music.lyric_listbox.itemconfig(index + 1, fg='green', bg='silver')
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
        path = pathlib.Path(path)

        lyric_path_list = [
            path.with_suffix('lrc'),
            path.parent / 'lyric' / f'{path.stem}.lrc',
        ]

        for lyric_path in lyric_path_list:
            print(lyric_path)
            if not os.path.exists(lyric_path):
                continue
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
            self.show_music.set_lyric(lyric_lines)
            self.active_lyric(0, len(timer), time.perf_counter(), timer)
            break
        else:
            self.reset_lyric()
