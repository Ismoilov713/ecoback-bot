import qrcode

# QR kod ichiga yoziladigan ma'lumot
data = "https://t.me/ecoback_bot"   # masalan bot havolasi

# QR kod obyektini yaratish
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)

qr.add_data(data)
qr.make(fit=True)

# Suratni yaratish
img = qr.make_image(fill_color="green", back_color="white")

# Saqlash
img.save("ecoback_qr.png")

print("✅ QR kod yaratildi va 'ecoback_qr.png' faylga saqlandi.")
