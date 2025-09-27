import csv
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# CSV fayl
csv_file = "bins.csv"

# QR kodlarni saqlash papkasi
output_dir = "bin_qr_codes"
os.makedirs(output_dir, exist_ok=True)

# Shrift (agar sizda Arial bo‘lmasa, "DejaVuSans" dan foydalaning)
try:
    font = ImageFont.truetype("arial.ttf", 30)
except:
    font = ImageFont.load_default()

# CSV faylni o‘qish
with open(csv_file, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        bin_id = row["bin_id"]

        # QR kod yaratish
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(f"ECOBACK_BIN_{bin_id}")
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Brend yozuv qo‘shish
        width, height = img_qr.size
        new_img = Image.new("RGB", (width, height + 60), "white")
        new_img.paste(img_qr, (0, 0))

        draw = ImageDraw.Draw(new_img)
        text = f"EcoBack Bin {bin_id}"
        text_width = draw.textlength(text, font=font)
        draw.text(((width - text_width) / 2, height + 10), text, fill="black", font=font)

        # Faylni saqlash
        file_path = os.path.join(output_dir, f"ECOBACK_BIN_{bin_id}.png")
        new_img.save(file_path)
        print(f"✅ QR yaratildi: {file_path}")
