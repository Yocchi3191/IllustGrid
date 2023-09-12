import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class IllustGrid:
    def __init__(self, root, folder_path, thumbnail_width):
        """
        ウィンドウ構造
        root
        |-- main_frame
            |-- canvas ...並べた画像を描画
            |-- sidebar_frame ...シャッフル、スライダー等のボタンを表示
        """

        self.root = root
        self.root.title("IllustGrid")

        self.folder_path = folder_path  # 引数で渡したパスの取得
        self.image_files = self.load_image_files(
            self.folder_path)  # フォルダから画像データを取得
        self.shuffled_files = self.shuffle_images(
            self.image_files)  # 取得したデータをランダムに並べ替え

        # 画像配置に使う変数
        self.thumbnail_width = thumbnail_width
        self.dy = 20
        self.dx = 15

        # GUIの描画
        self.main_frame = ttk.Frame(self.root)  # キャンバスとサイドバーを内包するフレーム
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        # ウィンドウサイズ変化時、キャンバス描画エリアを調整するように
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # キャンバス
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
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
        self.main_frame.bind("<Configure>", self.on_canvas_configure)
        # マウスホイールに対応
        self.main_frame.bind_all("<MouseWheel>", self.y_scrolling)

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

            ・配置処理
                1. キャンバスサイズ取得
                2. サムネサイズ取得
                3. (canvas_width + dx) // (thumbnail_width + dx) で、列数求める
                4. col_maxをmax列として、current_col = 0で宣言
                5. リスト型 x, y に、列ごとの座標を格納
                6. imageラベルを(pos_x[current_col], pos_y[current_col])の座標に配置。配置後current_col += 1
                7. current_col >= col_maxまで列ずらして配置したら、current_col = 0で1列目から再配置
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

        thumbnail_width = self.thumbnail_width

        # 画像同士の距離
        dx = self.dx
        dy = self.dy

        col_max = (canvas_width + dx) // (thumbnail_width + dx)  # 列数
        current_col = 0
        # 配置する位置を計算
        x = [dx + (thumbnail_width + dx) * col for col in range(col_max)]
        y = [0 for _ in range(col_max)]

        for image_file in self.shuffled_files:
            image_path = os.path.join(folder_path, image_file)
            image = Image.open(image_path)
            image.thumbnail((thumbnail_width, 600))

            photo = ImageTk.PhotoImage(image)

            label = tk.Label(self.canvas, image=photo)
            label.image = photo

            # 画像をキャンバス内に配置
            label.place(x=x[current_col], y=y[current_col])
            y[current_col] += image.height + dy

            # ウィンドウの高さ更新
            canvas_height = self.canvas.winfo_height()
            if canvas_height < y[current_col]:
                canvas_height = y[current_col]
            self.canvas.config(scrollregion=(
                0, 0, canvas_width, canvas_height))

            # 折り返し処理
            current_col += 1
            if current_col >= col_max:
                current_col = 0

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
        self.dx = int(value)
        self.on_canvas_configure(None)


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=True, height=True)  # ウィンドウのサイズ変更を許可
    folder_path = r"Images"  # 画像フォルダのパス
    thumbnail_width = 300  # 表示される画像の初期幅が変えられます
    app = IllustGrid(root, folder_path, thumbnail_width)
    app.run()
