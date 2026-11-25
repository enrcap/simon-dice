"""Siluetas de monumentos compartidas por la impresión y el lector."""
import cv2
import numpy as np


NOMBRES = {1: "PIRÁMIDE DE GIZA", 2: "PUERTA DE BRANDENBURGO",
           3: "CRISTO REDENTOR", 4: "COLISEO DE ROMA"}
COLORES = {1: (25, 195, 250), 2: (220, 105, 25), 3: (60, 165, 20), 4: (55, 55, 225)}
LUGARES = {1: "GIZA / EGIPTO", 2: "BERLÍN / ALEMANIA",
           3: "RÍO DE JANEIRO / BRASIL", 4: "ROMA / ITALIA"}


def symbol_mask(number, size=128):
    """Dibuja una silueta plana con huecos amplios para la lectura por webcam."""
    mask = np.zeros((size, size), dtype=np.uint8)
    scale = size - 1

    def rectangle(left, top, right, bottom, color=255):
        cv2.rectangle(mask, (round(left * scale), round(top * scale)),
                      (round(right * scale), round(bottom * scale)), color, -1)

    def polygon(points, color=255):
        pixels = np.rint(np.array(points) * scale).astype(np.int32)
        cv2.fillPoly(mask, [pixels], color)

    def circle(x, y, radius, color=255):
        cv2.circle(mask, (round(x * scale), round(y * scale)), round(radius * scale), color, -1)

    if number == 1:
        polygon([(.08, .84), (.50, .17), (.92, .84)])
        rectangle(.07, .84, .93, .87)
    elif number == 2:
        # Seis columnas dóricas, entablamento y cuadriga central.
        rectangle(.07, .86, .93, .91)
        rectangle(.11, .81, .89, .86)
        for x in (.15, .29, .43, .57, .71, .85):
            rectangle(x - .025, .40, x + .025, .82)
            rectangle(x - .04, .38, x + .04, .43)
            rectangle(x - .04, .78, x + .04, .82)
        rectangle(.10, .29, .90, .39)
        rectangle(.15, .24, .85, .29)
        rectangle(.36, .20, .64, .24)
        for x in (.39, .46, .54, .61):
            polygon([(x - .023, .20), (x - .023, .13), (x, .10),
                     (x + .022, .14), (x + .018, .20)])
        rectangle(.485, .09, .515, .19)
        circle(.5, .065, .022)
        polygon([(.49, .11), (.43, .065), (.46, .14), (.54, .14), (.57, .065), (.51, .11)])
    elif number == 3:
        # Brazos abiertos y túnica sobre el pedestal del Corcovado.
        circle(.50, .20, .06)
        rectangle(.47, .24, .53, .35)
        polygon([(.08, .32), (.43, .34), (.47, .31), (.53, .31),
                 (.57, .34), (.92, .32), (.92, .38), (.56, .43),
                 (.65, .80), (.35, .80), (.44, .43), (.08, .38)])
        rectangle(.36, .79, .64, .84)
        rectangle(.29, .84, .71, .89)
    elif number == 4:
        # Perfil elíptico y dos niveles de grandes arcos en la fachada.
        polygon([(.07, .39), (.14, .29), (.20, .29), (.20, .20),
                 (.35, .15), (.58, .16), (.80, .23), (.93, .37),
                 (.93, .78), (.82, .86), (.60, .90), (.35, .89),
                 (.15, .84), (.07, .77)])
        for y in (.44, .65):
            for x in (.17, .28, .39, .50, .61, .72, .83):
                circle(x, y, .035, 0)
                rectangle(x - .035, y, x + .035, y + .11, 0)
        for x in (.31, .43, .55, .67):
            rectangle(x - .022, .24, x + .022, .30, 0)
    else:
        raise ValueError("Número de tarjeta desconocido")
    return mask


def render_card(number, size=600):
    card = np.full((size, size, 3), 255, dtype=np.uint8)
    margin = round(.08 * size)
    cv2.rectangle(card, (margin, margin), (size - 1 - margin, size - 1 - margin),
                  (0, 0, 0), round(.04 * size))
    extent = round(.68 * size)
    start = (size - extent) // 2
    symbol = symbol_mask(number, extent)
    region = card[start:start + extent, start:start + extent]
    region[symbol > 0] = (0, 0, 0)
    return card
