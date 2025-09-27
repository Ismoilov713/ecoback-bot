import csv
import qrcode
import os

# CSV fayl manzili
csv_file = "codes.csv"

# QR kodlarni saqlash uchun papka
output_dir = "qr_codes"
os.makedirs(output_dir, exist_ok=True)

# CSV faylni ochish
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        code = row["kod"]
        status = row["status"]

        if status == "unused":  # faqat ishlatilmagan kodlar uchun
            img = qrcode.make(code)
            img.save(f"{output_dir}/{code}.png")
            print(f"✅ QR yaratildi: {code}")
