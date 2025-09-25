# generate_qr.py
import qrcode

for i in range(1, 11):
    code = f"ECO{i:03d}"  # ECO001, ECO002, ...
    img = qrcode.make(code)
    img.save(f"{code}.png")
    print(f"✅ {code} yaratildi")
