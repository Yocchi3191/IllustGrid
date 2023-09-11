import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class IllustGrid:
    def __init__(self, root, folder_path, thumbnail_width):
        self.root = root
        self.root.title("IllustGrid")

        self.folder_path = folder_path  # 引数で渡したパスの取得
        self.image_files = self.load_image_files(
            self.folder_path)  # フォルダから画像データを取得
        self.shuffled_files = self.shuffle_images(
            self.image_files)  # 取得したデータをランダムに並べ替え

        self.thumbnail_width = thumbnail_width
        self.dy = 20
        self.dx = 15

        # GUIの描画
        self.main_frame = ttk.Frame(self.root)  # キャンバスとサイドバーを内包するフレーム
        self.main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        # キャンバスを配置
        self.canvas = tk.Canvas(self.main_frame, bg="#555555")
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.canvas.config(width=960, height=600)  # キャンバスの初期サイズ設定

        # サイドバーフレーム
        self.sidebar_frame = ttk.Frame(self.main_frame)
        self.sidebar_frame.grid(row=0, column=1, sticky=tk.NS)

        # スクロールバーの描画
        self.scroll_x = tk.Scrollbar(
            self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.grid(row=1, column=0, sticky=tk.EW)
        self.scroll_y = tk.Scrollbar(
            self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.grid(row=0, column=2, sticky=tk.NS)
        self.canvas.config(
            xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # キャンバスのサイズ変更に対応させる処理
        self.canvas.bind(
            "<Configure>", self.on_canvas_configure)
        # マウスホイールに対応
        self.canvas.bind_all("<MouseWheel>", self.y_scrolling)

        # 再シャッフルボタン
        # ボタンの位置を指定（例：x座標は100、y座標は500）
        self.shuffle_button = ttk.Button(
            self.sidebar_frame,
            text="シャッフル",
            command=self.re_shuffle,
            padding=(30, 10))
        self.shuffle_button.grid(row=0, column=0, sticky=tk.EW)

        # 背景色調整スライダー
        self.bg_color_slider_label = ttk.Label(self.sidebar_frame, text="背景色:")
        self.bg_color_slider_label.grid(row=1, column=0)
        self.bg_color_slider = ttk.Scale(
            self.sidebar_frame,
            from_=0, to=255,
            command=self.update_background_color)
        self.bg_color_slider.grid(row=1, column=1)

        # 画像幅調整スライダー
        self.image_width_slider_label = ttk.Label(
            self.sidebar_frame, text="画像幅:")
        self.image_width_slider_label.grid(row=2, column=0)
        self.image_width_slider = ttk.Scale(
            self.sidebar_frame,
            from_=50, to=1000,
            command=self.update_thumbnail_width)
        self.image_width_slider.grid(row=2, column=1)
        # 値を表示
        thumbnail_var = tk.IntVar(value=thumbnail_width)
        self.image_width_value = ttk.Label(
            self.sidebar_frame, textvariable=thumbnail_var)
        self.image_width_value.grid(row=2, column=2)

        # グリッド幅調整スライダー
        self.grid_width_slider_label = ttk.Label(
            self.sidebar_frame, text="グリッド幅:")
        self.grid_width_slider_label.grid(row=3, column=0)
        self.grid_width_slider = ttk.Scale(
            self.sidebar_frame, from_=0, to=100, command=self.update_dx)
        self.grid_width_slider.grid(row=3, column=1)

        # スライダーの初期値を設定
        self.bg_color_slider.set(85)  # 初期背景色
        self.image_width_slider.set(self.thumbnail_width)  # 初期画像幅
        self.grid_width_slider.set(self.dx)  # 初期グリッド幅

    def load_image_files(self, images_path):
        """
        画像データを配列に格納して返す

        Args:
            images_path (str): 画像フォルダのパス

        Returns:
            list(images): フォルダから読み込んだ画像データ群を配列として返す
        """
        image_files = [f for f in os.listdir(images_path)
                       if f.endswith(('.jpg', '.png', '.jpeg'))]
        return image_files

    def shuffle_images(self, image_files):
        """
        引数で渡した配列の要素をシャッフルして返す

        Args:
            image_files (image): _description_

        Returns:
            _type_: _description_
        """
        random.shuffle(image_files)
        return image_files

    def re_shuffle(self):
        """
        画像リストを再シャッフル
        """
        self.shuffled_images = self.shuffle_images(self.image_files)
        self.on_canvas_configure(None)

    def on_canvas_configure(self, event):
        """
        取得した画像データを描画

        Args:
            event (_type_): _description_
        """
        # キャンバスをクリア
        self.canvas.delete("all")

        # キャンバスサイズ
        if event:
            canvas_width = event.width
        else:
            canvas_width = self.canvas.winfo_width()  # イベントがない場合、現在のキャンバスの幅を取得
        canvas_height = 0
        thumbnail_width = self.thumbnail_width
        col_num = canvas_width // thumbnail_width  # 列数。キャンバスと画像幅から計算

        dy = self.dy
        dx = self.dx
        y = [0 for _ in range(col_num)]  # レイアウトする画像のy座標
        x = [(thumbnail_width + dx) * coef + dx
             for coef in range(col_num)]  # 画像のx座標

        current_col = 0

        # 画像レイアウト
        for image_file in self.shuffled_files:
            # 画像をキャンバスに描画
            image_path = os.path.join(folder_path, image_file)  # 画像パスの生成
            image = Image.open(image_path)  # 変数に画像データを格納
            image.thumbnail((thumbnail_width, 600))  # 幅だけ列幅に合わせる
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.canvas, image=photo)
            label.image = photo
            self.canvas.create_window(x[current_col], y[current_col],
                                      anchor=tk.NW, window=label)

            # 折り返し処理
            y[current_col] += image.height + dy
            current_col += 1  # レイアウトする行をずらす
            if (current_col >= col_num):  # もし最終行を越えた場合折り返す
                current_col = 0

            # ウィンドウの高さ更新
            max_canv_height = y[current_col] + image.height
            if (canvas_height < max_canv_height):
                canvas_height = max_canv_height

        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

    def run(self):
        """
        GUIの起動
        """
        self.root.mainloop()

    def y_scrolling(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    # スライダーのコールバック関数
    def update_background_color(self, value):
        self.background_color = f"#{int(float(value)):02X}{int(float(value)):02X}{int(float(value)):02X}"
        self.canvas.configure(bg=self.background_color)

    def update_thumbnail_width(self, value):
        self.thumbnail_width = int(float(value))
        self.on_canvas_configure(None)

    def update_dx(self, value):
        self.dx = int(float(value))
        self.on_canvas_configure(None)


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=True, height=True)  # ウィンドウのサイズ変更を許可
    folder_path = r"Images"
    thumbnail_width = 300  # 表示される画像の初期幅が変えられます
    app = IllustGrid(root, folder_path, thumbnail_width)
    app.run()
