"""QR CODE GENERATOR"""

import qrcode


code = qrcode.make("Hello World")
code.save("QR.png")
