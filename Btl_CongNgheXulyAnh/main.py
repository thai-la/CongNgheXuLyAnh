import os
import time
import cv2
import face_recognition
import threading
import winsound
from PIL import Image, ImageTk
import requests
import tkinter as tk
from tkinter import ttk
import queue

# -------- Cấu hình Telegram --------
TELEGRAM_BOT_TOKEN = "7754333051:AAEnVQL5XK-c15gi2Ap8GySrLJURLB4XTNc"
TELEGRAM_CHAT_ID = "7743560797"

def send_telegram_alert_bytes(image_bytes):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        files = {'photo': ('alert.jpg', image_bytes, 'image/jpeg')}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': '🚨 Phát hiện người lạ!'}
        requests.post(url, files=files, data=data)
    except Exception as e:
        print("❌ Lỗi gửi Telegram:", e)

# -------- Load khuôn mặt đã biết --------
KNOWN_FACES_DIR = 'known_faces'
TOLERANCE = 0.6
MODEL = 'hog'

known_faces, known_names = [], []
for name in os.listdir(KNOWN_FACES_DIR):
    for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
        image_path = f"{KNOWN_FACES_DIR}/{name}/{filename}"
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(name)

# -------- Biến toàn cục --------
alarm_playing = False
recording = False
video, out = None, None
fourcc = cv2.VideoWriter_fourcc(*'XVID')
alert_mode = False
stop_flag = False
frame_queue = queue.Queue(maxsize=1)
status_queue = queue.Queue(maxsize=1)

# -------- Hàm báo động --------
def play_alarm():
    while alarm_playing and not stop_flag:
        winsound.PlaySound("alarm_new.wav", winsound.SND_FILENAME)
        time.sleep(1)

# -------- Cập nhật giao diện --------
def update_gui():
    try:
        frame = frame_queue.get_nowait()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        camera_label.imgtk = img
        camera_label.configure(image=img)
    except:
        pass
    if not stop_flag:
        root.after(30, update_gui)

def update_status():
    try:
        msg, color = status_queue.get_nowait()
        status_label.config(text=msg, foreground=color)
    except:
        pass
    if not stop_flag:
        root.after(100, update_status)

def update_video_list():
    video_listbox.delete(0, 'end')
    for f in sorted([f for f in os.listdir('.') if f.endswith('.avi')], reverse=True):
        video_listbox.insert('end', f)

def play_saved_video(filename):
    cap = cv2.VideoCapture(filename)
    while cap.isOpened() and not stop_flag:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(cv2.resize(frame, (320, 240)), cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        video_display_label.imgtk = img
        video_display_label.configure(image=img)
        time.sleep(0.03)
    cap.release()

def open_camera():
    for attempt in range(3):
        cap = cv2.VideoCapture("rtsp://admin:abc12345@192.168.1.113:554/onvif1", cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv2.CAP_PROP_FPS, 8)

        if cap.isOpened():
            print("✅ Đã kết nối camera RTSP.")
            return cap
        else:
            print(f"⚠️ Lỗi kết nối camera, thử lại ({attempt + 1}/3)...")
            cap.release()
            time.sleep(2)

    print("❌ Không thể kết nối đến camera sau 3 lần thử.")
    return None

def run_face_recognition():
    global alarm_playing, recording, video, out, stop_flag
    video = open_camera()
    if video is None:
        status_queue.put(("❌ Không thể kết nối camera.", "red"))
        return

    sent_alert, frame_count = False, 0

    while not stop_flag:
        ret, frame = video.read()

        if not ret or frame is None:
            print("⚠️ Không đọc được frame hoặc frame lỗi, đang thử kết nối lại...")
            status_queue.put(("❌ Mất kết nối camera, đang thử lại...", "orange"))
            time.sleep(2)
            video.release()
            video = open_camera()
            if video is None:
                status_queue.put(("❌ Không thể kết nối lại camera.", "red"))
                break
            continue

        frame_count += 1
        if frame_count % 3 != 0:
            while not frame_queue.empty():
                frame_queue.get_nowait()
            frame_queue.put(frame)
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model=MODEL)
        encodings = face_recognition.face_encodings(rgb, locations)

        unknown_detected = False
        for encoding, loc in zip(encodings, locations):
            matches = face_recognition.compare_faces(known_faces, encoding, TOLERANCE)
            name = known_names[matches.index(True)] if True in matches else "Unknown"
            if name == "Unknown":
                unknown_detected = True
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            top, right, bottom, left = loc
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if alert_mode and unknown_detected and not alarm_playing:
            alarm_playing = True
            threading.Thread(target=play_alarm, daemon=True).start()
            status_queue.put(("⚠️ Phát hiện người lạ!", "red"))

            if not recording:
                filename = f"unknown_{time.strftime('%Y%m%d-%H%M%S')}.avi"
                out = cv2.VideoWriter(filename, fourcc, 8.0, (frame.shape[1], frame.shape[0]))
                recording = True
                root.after(0, update_video_list)

            if not sent_alert:
                _, img_encoded = cv2.imencode('.jpg', frame)
                img_bytes = img_encoded.tobytes()
                threading.Thread(target=send_telegram_alert_bytes, args=(img_bytes,), daemon=True).start()
                sent_alert = True

        elif not unknown_detected:
            alarm_playing = False
            winsound.PlaySound(None, winsound.SND_PURGE)
            sent_alert = False
            status_queue.put(("✅ Đã nhận diện tất cả khuôn mặt", "green"))

        if recording and out:
            out.write(frame)
        else:
            if out:
                out.release()
                out = None

        while not frame_queue.empty():
            frame_queue.get_nowait()
        frame_queue.put(frame)

    video.release()
    if out:
        out.release()

# -------- GUI --------
def start_recognition():
    global stop_flag
    stop_flag = False
    threading.Thread(target=run_face_recognition, daemon=True).start()
    update_gui()
    update_status()

def stop_program():
    global stop_flag, alarm_playing, video, out, recording
    stop_flag = True
    alarm_playing = False
    winsound.PlaySound(None, winsound.SND_PURGE)
    if video and video.isOpened():
        video.release()
    if out:
        out.release()
    recording = False
    root.destroy()

def toggle_alert():
    global alert_mode
    alert_mode = alert_var.get()

def on_video_select(event):
    if event.widget.curselection():
        filename = event.widget.get(event.widget.curselection()[0])
        threading.Thread(target=play_saved_video, args=(filename,), daemon=True).start()

def create_interface():
    global root, camera_label, status_label, alert_var, video_listbox, video_display_label

    root = tk.Tk()
    root.title("Nhận diện khuôn mặt cảnh báo người lạ")
    root.geometry("800x500")

    frame_left = ttk.Frame(root, padding=10)
    frame_left.pack(side=tk.LEFT, fill=tk.Y)

    camera_label = ttk.Label(frame_left, border=1, relief="solid")
    camera_label.pack(pady=5)

    status_label = ttk.Label(frame_left, text="📹 Chưa khởi động", font=("Arial", 12), foreground="gray")
    status_label.pack(pady=10)

    alert_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(frame_left, text="Bật cảnh báo người lạ", variable=alert_var, command=toggle_alert).pack(pady=5)

    ttk.Button(frame_left, text="Bắt đầu nhận diện", command=start_recognition).pack(pady=5, fill=tk.X)
    ttk.Button(frame_left, text="Dừng chương trình", command=stop_program).pack(pady=5, fill=tk.X)

    frame_right = ttk.Frame(root, padding=10)
    frame_right.pack(side=tk.RIGHT, fill=tk.Y)

    ttk.Label(frame_right, text="Danh sách video lưu:").pack(anchor="w")

    video_listbox = tk.Listbox(frame_right, width=35, height=15)
    video_listbox.pack(pady=5)
    video_listbox.bind('<<ListboxSelect>>', on_video_select)

    video_display_label = ttk.Label(frame_right, border=1, relief="solid")
    video_display_label.pack(pady=10)

    return root

# -------- Chạy chương trình --------
root = create_interface()
update_video_list()
root.protocol("WM_DELETE_WINDOW", stop_program)
root.mainloop()
