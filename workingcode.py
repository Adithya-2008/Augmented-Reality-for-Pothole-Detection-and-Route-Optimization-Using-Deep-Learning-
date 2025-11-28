import cv2
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from ultralytics import YOLO

# Load YOLO model
pothole_model = YOLO(r"C:\Users\adith\OneDrive\Desktop\potholecode\best.pt")
print("✅ Model loaded successfully!")

# Parameters
line_width = 250
line_height_ratio = 0.85
top_shift_x = 0
corridor_center_x = None

# Camera setup
camera_index = 0
cap = cv2.VideoCapture(camera_index)

VIDEO_WIDTH = 1700
VIDEO_HEIGHT = 1200

#VIDEO_WIDTH = 1000
#VIDEO_HEIGHT = 800

# GUI setup
root = tk.Tk()
root.title("Pothole Detection Interface")
root.attributes('-fullscreen', True)
root.configure(bg="black")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

video_frame = tk.Frame(root, bg="black", width=VIDEO_WIDTH, height=VIDEO_HEIGHT)
video_frame.place(x=0, y=(screen_height - VIDEO_HEIGHT)//2)

video_label = tk.Label(video_frame, bg="black", width=VIDEO_WIDTH, height=VIDEO_HEIGHT)
video_label.pack(fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root, bg="#222", width=300, height=screen_height)
button_frame.place(x=screen_width - 300, y=0)
button_frame.pack_propagate(False)

# Detection logic
def polygons_intersect(poly1, poly2):
    poly1 = np.array(poly1, dtype=np.float32).reshape((-1, 1, 2))
    poly2 = np.array(poly2, dtype=np.float32).reshape((-1, 1, 2))
    for pt in poly1:
        pt_tuple = (float(pt[0][0]), float(pt[0][1]))
        if cv2.pointPolygonTest(poly2, pt_tuple, False) >= 0:
            return True
    for pt in poly2:
        pt_tuple = (float(pt[0][0]), float(pt[0][1]))
        if cv2.pointPolygonTest(poly1, pt_tuple, False) >= 0:
            return True
    return False

def shift_lines_evasion(frame, pothole_results):
    global line_width, corridor_center_x, line_height_ratio, top_shift_x
    h, w, _ = frame.shape
    if corridor_center_x is None:
        corridor_center_x = w // 2

    bl = (corridor_center_x - line_width, h)
    br = (corridor_center_x + line_width, h)
    tl = (corridor_center_x - line_width + top_shift_x, int(h * line_height_ratio))
    tr = (corridor_center_x + line_width + top_shift_x, int(h * line_height_ratio))
    corridor = np.array([bl, br, tr, tl])

    obstacle_polys = []
    obstacle_boxes = []
    pothole_centers = []

    for r in pothole_results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box.tolist())
            poly = np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
            obstacle_polys.append(poly)
            obstacle_boxes.append((x1, y1, x2, y2))
            pothole_centers.append((x1 + x2) // 2)
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
            cv2.putText(frame, "Pothole", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    intersects = any(polygons_intersect(corridor, poly) for poly in obstacle_polys)

    if intersects and pothole_centers:
        avg_x = int(np.mean(pothole_centers))
        if avg_x < corridor_center_x:
            top_shift_x += 120
        else:
            top_shift_x -= 120
    else:
        if top_shift_x > 0:
            top_shift_x = max(0, top_shift_x - 20)
        elif top_shift_x < 0:
            top_shift_x = min(0, top_shift_x + 20)

    tl = (corridor_center_x - line_width + top_shift_x, int(h * line_height_ratio))
    tr = (corridor_center_x + line_width + top_shift_x, int(h * line_height_ratio))
    corridor = np.array([bl, br, tr, tl])
    intersects = any(polygons_intersect(corridor, poly) for poly in obstacle_polys)

    if intersects:
        for (x1, y1, x2, y2) in obstacle_boxes:
            roi = frame[y1:y2, x1:x2]
            darkened = cv2.convertScaleAbs(roi, alpha=0.5, beta=0)
            frame[y1:y2, x1:x2] = darkened
        cv2.putText(frame, "WARNING: Obstacle ahead!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    cv2.line(frame, bl, tl, (0,255,255), 3)
    cv2.line(frame, br, tr, (0,255,255), 3)
    return frame

# Button functions
def widen_corridor(): 
    global line_width
    line_width = min(400, line_width + 10)

def narrow_corridor(): 
    global line_width
    line_width = max(100, line_width - 10)

def tilt_forward():
    global line_height_ratio
    line_height_ratio = max(0.5, line_height_ratio - 0.01)

def tilt_backward():
    global line_height_ratio
    line_height_ratio = min(0.95, line_height_ratio + 0.01)

def reset_guidelines():
    global line_width, corridor_center_x, line_height_ratio, top_shift_x
    line_width = 250
    corridor_center_x = None
    line_height_ratio = 0.85
    top_shift_x = 0
    print("🔄 Guidelines reset to default")

def switch_camera():
    global camera_index, cap
    cap.release()
    camera_index = (camera_index + 1) % 3
    cap = cv2.VideoCapture(camera_index)
    print(f"🔄 Switched to camera {camera_index}")

def quit_app():
    cap.release()
    root.destroy()

# Button layout
btn_style = {
    "width": 20,
    "height": 2,
    "bg": "#333",
    "fg": "white",
    "font": ("Segoe UI", 12, "bold"),
    "activebackground": "#555",
    "activeforeground": "white",
    "bd": 0,
    "relief": tk.FLAT
}

tk.Label(button_frame, text="🛠️ Controls", bg="#222", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))
tk.Button(button_frame, text="➡️ Widen Corridor", command=widen_corridor, **btn_style).pack(pady=5)
tk.Button(button_frame, text="⬅️ Narrow Corridor", command=narrow_corridor, **btn_style).pack(pady=5)
tk.Button(button_frame, text="⏫ Tilt Forward", command=tilt_forward, **btn_style).pack(pady=5)
tk.Button(button_frame, text="⏬ Tilt Backward", command=tilt_backward, **btn_style).pack(pady=5)
tk.Button(button_frame, text="🔄 Reset Guidelines", command=reset_guidelines, **btn_style).pack(pady=20)

tk.Label(button_frame, text="📷 Camera", bg="#222", fg="white", font=("Segoe UI", 14, "bold")).pack(pady=(30, 10))
tk.Button(button_frame, text="🔄 Switch Camera", command=switch_camera, **btn_style).pack(pady=5)
tk.Button(button_frame, text="❌ Quit", command=quit_app, **btn_style).pack(pady=20)

# Live video loop
def update_frame():
    ret, frame = cap.read()
    if ret:
        pothole_results = pothole_model.predict(frame, conf=0.03, verbose=False)
        frame = shift_lines_evasion(frame, pothole_results)
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        video_label.config(image=img)
        video_label.image = img
    root.after(10, update_frame)

update_frame()
root.mainloop()