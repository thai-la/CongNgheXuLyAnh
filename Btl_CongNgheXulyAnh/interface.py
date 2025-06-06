import tkinter as tk
from tkinter import ttk

def create_interface(start_func, stop_func, alert_toggle_func, play_video_callback):
    root = tk.Tk()
    root.title("Nhận diện người lạ qua khuôn mặt")
    root.geometry("780x480")
    root.resizable(False, False)

    def on_closing():
        stop_func()  # Đảm bảo tắt camera/video trước khi thoát
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Frame bên trái: Camera, trạng thái, điều khiển
    frame_left = ttk.Frame(root, padding=8)
    frame_left.pack(side=tk.LEFT, fill=tk.Y)

    ttk.Label(frame_left, text="📡 Điều khiển", font=("Arial", 10, "bold")).pack(pady=(0,5))

    camera_label = ttk.Label(frame_left, border=1, relief="solid", width=48, height=16)
    camera_label.pack(pady=5)

    status_label = ttk.Label(
        frame_left,
        text="📷 Camera chưa hoạt động",
        font=("Arial", 11),
        foreground="gray"
    )
    status_label.pack(pady=10, padx=5, fill=tk.X)

    alert_var = tk.BooleanVar(value=False)
    alert_check = ttk.Checkbutton(
        frame_left,
        text="Bật cảnh báo người lạ",
        variable=alert_var,
        command=alert_toggle_func
    )
    alert_check.pack(pady=5)

    ttk.Button(frame_left, text="▶️ Bắt đầu", command=start_func).pack(pady=5, fill=tk.X)
    ttk.Button(frame_left, text="⛔ Dừng", command=stop_func).pack(pady=5, fill=tk.X)

    # Frame bên phải: Danh sách video & xem lại
    frame_right = ttk.Frame(root, padding=8)
    frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    ttk.Label(frame_right, text="🎞️ Video đã lưu:", font=("Arial", 10)).pack(anchor="w")

    video_listbox = tk.Listbox(
        frame_right,
        width=35,
        height=12,
        activestyle="dotbox",
        selectmode=tk.SINGLE
    )
    video_listbox.pack(pady=5, fill=tk.X)
    video_listbox.bind('<<ListboxSelect>>', play_video_callback)

    scrollbar = ttk.Scrollbar(frame_right, orient=tk.VERTICAL, command=video_listbox.yview)
    scrollbar.place(in_=video_listbox, relx=1.0, rely=0, relheight=1.0, anchor='ne')
    video_listbox.config(yscrollcommand=scrollbar.set)

    video_display_label = ttk.Label(frame_right, border=1, relief="solid", width=45, height=12)
    video_display_label.pack(pady=10)

    return root, camera_label, status_label, alert_var, video_listbox, video_display_label
