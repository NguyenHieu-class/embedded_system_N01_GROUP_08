# from PIL import ImageFont, ImageDraw, Image
# import numpy as np
# from easyocr import Reader
# import cv2

# # loading images and resizing
# img = cv2.imread('image8.jpg')
# img = cv2.resize(img, (800, 600))
# # load font
# fontpath = "./arial.ttf"
# font = ImageFont.truetype(fontpath, 32)
# b,g,r,a = 0,255,0,0
# # making the image grayscale
# grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
# edged = cv2.Canny(blurred, 10, 200)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]

# for c in contours:
#     perimeter = cv2.arcLength(c, True)
#     approximation = cv2.approxPolyDP(c, 0.02 * perimeter, True)
#     print(approximation)
#     if len(approximation) == 4: # rectangle
#         number_plate_shape = approximation
#         break

# (x, y, w, h) = cv2.boundingRect(number_plate_shape)
# number_plate = grayscale[y:y + h, x:x + w]

# reader = Reader(['en'])
# detection = reader.readtext(number_plate)

# if len(detection) == 0:
#     text = "Không thấy bảng số xe"
#     img_pil = Image.fromarray(img) #image biến lấy khung hình từ webcam
#     draw = ImageDraw.Draw(img_pil)
#     draw.text((150, 500), text, font = font, fill = (b, g, r, a))
#     img = np.array(img_pil) #hiển thị ra window
#     #cv2.putText(img, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 3)
#     cv2.waitKey(0)
# else:
#     cv2.drawContours(img, [number_plate_shape], -1, (255, 0, 0), 3)
#     text ="Biển số: " + f"{detection[0][1]}"
#     img_pil = Image.fromarray(img) #image biến lấy khung hình từ webcam
#     draw = ImageDraw.Draw(img_pil)
#     draw.text((200, 500), text, font = font, fill = (b, g, r, a))
#     img = np.array(img_pil) #hiển thị ra window
#     #cv2.putText(img, text, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
#     cv2.imshow('Plate Detection', img)
#     cv2.waitKey(0)
#     #cv2.waitKey(5)

import cv2
import numpy as np
from easyocr import Reader
from PIL import ImageFont, ImageDraw, Image
import tkinter as tk
from tkinter import filedialog, Label, Button
from tkinter import ttk

# Khởi tạo EasyOCR
reader = Reader(['en'])

# Tải font chữ
fontpath = "./arial.ttf"
font = ImageFont.truetype(fontpath, 32)
b, g, r, a = 0, 255, 0, 0

def process_image(img_path):
    # Đọc và resize ảnh
    img = cv2.imread(img_path)
    img = cv2.resize(img, (800, 600))

    # Xử lý ảnh grayscale và edge detection
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
    edged = cv2.Canny(blurred, 10, 200)

    # Tìm contour
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    number_plate_shape = None
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        approximation = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        if len(approximation) == 4:  # nhận diện hình chữ nhật (biển số)
            number_plate_shape = approximation
            break

    result_text = "Không tìm thấy biển số"

    if number_plate_shape is not None:
        (x, y, w, h) = cv2.boundingRect(number_plate_shape)
        number_plate = grayscale[y:y + h, x:x + w]
        detection = reader.readtext(number_plate)

        if detection:
            result_text = f"Biển số: {detection[0][1]}"
            cv2.drawContours(img, [number_plate_shape], -1, (255, 0, 0), 3)

    # Chuyển đổi để vẽ text lên ảnh
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text((50, 50), result_text, font=font, fill=(b, g, r, a))
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # Hiển thị ảnh kết quả
    cv2.imshow('Kết quả nhận diện', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        process_image(file_path)

# Giao diện Tkinter
root = tk.Tk()
root.title("Nhận diện biển số xe")
root.geometry("400x200")

upload_btn = Button(root, text="Tải ảnh lên", command=upload_image)
upload_btn.pack(pady=20)

result_label = Label(root, text="Kết quả sẽ hiển thị trong cửa sổ ảnh")
result_label.pack(pady=10)

root.mainloop()