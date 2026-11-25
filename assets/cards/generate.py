"""Genera la hoja A4 de siluetas de monumentos que utiliza el lector del juego.

Requiere Pillow para dibujar los rótulos de impresión.
"""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.monumentos import COLORES, LUGARES, NOMBRES, render_card


def main():
    sheet = Image.new("RGB", (2480, 3508), "white")
    draw = ImageDraw.Draw(sheet)
    fonts = ROOT / "assets" / "cards"

    def font(size):
        return ImageFont.truetype(str(fonts / "Inter.ttf"), size)

    draw.text((160, 125), "SIMÓN DICE", font=font(108), fill="#172B3D")
    draw.text((165, 270), "MONUMENTOS DEL MUNDO", font=font(44), fill="#455767")
    draw.line((160, 370, 2320, 370), fill="#172B3D", width=5)
    for number in range(1, 5):
        row, column = divmod(number - 1, 2)
        x, y = 160 + column * 1160, 470 + row * 1280
        card = render_card(number, 1000)
        sheet.paste(Image.fromarray(card[:, :, ::-1]), (x, y))
        rgb = tuple(reversed(COLORES[number]))
        draw.rounded_rectangle((x + 30, y + 1020, x + 125, y + 1115), radius=18, fill=rgb)
        draw.text((x + 78, y + 1066), str(number), font=font(56), fill="#102030", anchor="mm")
        draw.text((x + 155, y + 1037), NOMBRES[number], font=font(36), fill="#172B3D")
        draw.text((x + 155, y + 1094), LUGARES[number], font=font(24), fill="#455767")
    draw.line((160, 3080, 2320, 3080), fill="#172B3D", width=3)
    draw.text((160, 3150), "Recorta cada tarjeta con su marco negro y su margen blanco.",
              font=font(34), fill="#172B3D")
    draw.text((160, 3212), "Presenta una tarjeta completa y retírala cuando el juego la lea.",
              font=font(34), fill="#455767")
    sheet.save(ROOT / "assets" / "cards" / "tarjetas.png", dpi=(300, 300))


if __name__ == "__main__":
    main()
