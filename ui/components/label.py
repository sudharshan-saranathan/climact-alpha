# Encoding: utf-8
# Module name: string
# Description: A QGraphicsTextItem subclass with customizable options.

# Imports (standard)
from __future__ import annotations


from PySide6 import QtGui, QtCore, QtWidgets

LabelOpts = {
    "const": False,  # Whether the string is immutable.
    "round": 4,  # Radius for rounded corners.
    "coord": QtCore.QPointF(
        0, 0
    ),  # Default position of the label with respect to its parent.
    "style": {
        "border": QtCore.Qt.GlobalColor.transparent,
        "background": QtCore.Qt.GlobalColor.transparent,
    },
    "label": {
        "font": QtGui.QFont("Trebuchet MS", 7),  # Default text font.
        "color": QtCore.Qt.GlobalColor.black,  # Default text color.
        "align": QtCore.Qt.AlignmentFlag.AlignCenter,  # Default text alignment.
        "width": 80,  # Default text width.
    },
}


# Class String: A custom-QGraphicsTextItem
class Label(QtWidgets.QGraphicsTextItem):

    # Signals:
    sig_text_changed = QtCore.Signal(str, name="String.sig_text_changed")

    # Initializer:
    def __init__(
        self, label: str, parent: QtWidgets.QGraphicsItem | None = None, **kwargs
    ):

        # Initialize base-class:
        super().__init__(label, parent)
        super().setAcceptHoverEvents(True)

        # Retrieve keywords:
        self.setProperty("const", kwargs.get("const", LabelOpts["const"]))
        self.setProperty("round", kwargs.get("round", LabelOpts["round"]))
        self.setProperty("style", kwargs.get("style", LabelOpts["style"]))

        # Text properties:
        self.setProperty("text-color", kwargs.get("color", LabelOpts["label"]["color"]))
        self.setProperty("text-width", kwargs.get("width", LabelOpts["label"]["width"]))
        self.setProperty("text-align", kwargs.get("align", LabelOpts["label"]["align"]))
        self.setProperty("text-font", kwargs.get("font", LabelOpts["label"]["font"]))

        # Customize attribute(s):
        self.setFont(self.property("text-font"))
        self.setTextWidth(self.property("text-width"))
        self.setDefaultTextColor(self.property("text-color"))
        self.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextEditorInteraction
            if not self.property("const")
            else QtCore.Qt.TextInteractionFlag.NoTextInteraction
        )

        # Set text-alignment:
        option = self.document().defaultTextOption()
        option.setAlignment(self.property("text-align"))
        self.document().setDefaultTextOption(option)

    # Reimplementation of QGraphicsTextItem.paint():
    def paint(self, painter, option, widget):

        # Reset the state-flag to prevent the dashed-line selection style.
        option.state = QtGui.QStyle.StateFlag.State_None

        # Paint the border and background:
        painter.setPen(QtGui.QPen(self.property("style")["border"], 0.75))
        painter.setBrush(self.property("style")["background"])
        painter.drawRoundedRect(
            self.boundingRect(), self.property("round"), self.property("round")
        )

        # Invoke base-class implementation to paint the text:
        super().paint(painter, option, widget)

    # Edit text:
    def edit(self):

        # If the item is immutable, return immediately:
        if self.property("const"):
            return

        # Make label edit:
        self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
        self.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextEditorInteraction
        )

        # Highlight text:
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
        cursor.movePosition(
            QtGui.QTextCursor.MoveOperation.End, QtGui.QTextCursor.MoveMode.KeepAnchor
        )
        self.setTextCursor(cursor)

    # Reimplementation of QGraphicsTextItem.keyPressEvent():
    def keyPressEvent(self, event):
        """
        Handles key press events for the text item.
        :param event:
        :return:
        """

        # If the key pressed is `Return`, finish editing and clear focus:
        if event.key() == QtCore.Qt.Key.Key_Return:
            self.clearFocus()
            event.accept()
            return

        # Otherwise, call super-class implementation:
        super().keyPressEvent(event)

    # Reimplementation of QGraphicsTextItem.focusInEvent():
    def focusInEvent(self, event):
        """
        This method is called when the text item gains focus.
        :param event:
        :return:
        """

        # If the item is immutable, return immediately:
        if self.property("const"):
            return

        # Super-class implementation:
        super().focusInEvent(event)

    # Reimplementation of QGraphicsTextItem.focusOutEvent():
    def focusOutEvent(self, event):

        # Clear text-selection and emit signal:
        string = self.toPlainText().strip()  # Get the text and strip whitespace
        self.sig_text_changed.emit(string)  # Emit signal with new text as the argument
        self.textCursor().clearSelection()  # Clear text-selection

        # Super-class implementation:
        super().focusOutEvent(event)

    # Reimplementation of QGraphicsTextItem.hoverEnterEvent():
    def hoverEnterEvent(self, event):
        """
        Handles the hover enter event to change the cursor shape.
        :param event: QGraphicsSceneHoverEvent
        """

        if not self.property("const"):
            self.setCursor(QtCore.Qt.CursorShape.IBeamCursor)
            self.update()

        super().hoverEnterEvent(event)

    # Reimplementation of QGraphicsTextItem.hoverEnterEvent():
    def hoverLeaveEvent(self, event):
        """
        Handles the hover enter event to change the cursor shape.
        """

        if not self.property("const"):
            self.setCursor(QtCore.Qt.CursorShape.IBeamCursor)
            self.update()

        super().hoverLeaveEvent(event)

    @property
    def const(self):
        return self.property("const")

    @const.setter
    def const(self, value: bool):
        """
        Set the const property of the string.
        :param value: bool
        """
        self.setProperty("const", value)
        self.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.NoTextInteraction
            if value
            else QtCore.Qt.TextInteractionFlag.TextEditorInteraction
        )
        self.update()
