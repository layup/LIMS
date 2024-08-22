
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

def apply_drop_shadow_effect(widget):
    # Create drop shadow effect
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setColor(QColor(0, 0, 0, 150))  # Set shadow color
    shadow.setBlurRadius(10)  # Set shadow blur radius
    shadow.setOffset(0, 0)  # Set shadow offset (no offset)

    widget.raise_()
    widget.setAutoFillBackground(True) 
    widget.setGraphicsEffect(shadow)