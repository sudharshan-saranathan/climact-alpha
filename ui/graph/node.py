# Encoding: utf-8
# Module name: vertex
# Description: A QtWidgets.QGraphicsObject-based vertex for the Climact application that represents a generic node in a schematic.

# Imports:
import copy
import opts
import types

from PySide6 import QtGui, QtCore, QtWidgets

from ui.components import *
from schematic.anchor import AnchorItem
from schematic.handle import HandleItem, HandleRole

# Default vertex options:
VERTEX_OPTS = {
    "corner-radius": 4,
    "frame": QtCore.QRectF(-36, -40, 72, 68),
    "board": {
        "corner-radius": 4,
        "frame": QtCore.QRectF(-36, -28, 72, 56),
        "brush": QtGui.QBrush(QtGui.QColor(0xFFFFFF)),
    },
    "style": {
        "pen": {
            "normal": QtGui.QPen(QtGui.QColor(0x3A4043), 2.0),
            "select": QtGui.QPen(QtGui.QColor(0xFFCB00), 2.0),
        },
        "brush": {
            "normal": QtGui.QBrush(QtGui.QColor(0x3A4043)),
            "select": QtGui.QBrush(QtGui.QColor(0xFFCB00)),
        },
    },
}


# Class Resizing handle:
class ResizeHandle(QtWidgets.QGraphicsObject):

    # QtCore.Signal(s):
    sig_resize_handle_moved = QtCore.Signal()

    # Default constructor:
    def __init__(self, **kwargs):

        # Base-class initialization:
        super().__init__(kwargs.get("parent", None))

        # Set class-level attribute(s):
        self.setProperty("frame", kwargs.get("frame", QtCore.QRectF(-32, -2, 64, 4)))
        self.sig_resize_handle_moved.connect(kwargs.get("callback", None))

        # Customize behavior:
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(
            QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemSendsScenePositionChanges
        )

    # Reimplement boundingRect(...):
    def boundingRect(self) -> QtCore.QRectF:
        return self.property("frame").adjusted(-2, -2, 2, 2)

    # Reimplement paint(...):
    def paint(self, painter, option, /, widget=...):
        painter.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.boundingRect(), 2, 2)

    # Reimplement itemChange(...):
    def itemChange(self, change, value, /):

        # Emit a QtCore.Signal when the resize-handle is moved:
        if (
            change
            == QtWidgets.QGraphicsObject.GraphicsItemChange.ItemPositionHasChanged
        ):
            if self.scene():
                self.scene().clearSelection()

            self.sig_resize_handle_moved.emit()

        return value

    # Reimplement hoverEnterEvent(...):
    def hoverEnterEvent(self, event, /):
        super().setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
        super().hoverEnterEvent(event)

    # Reimplement hoverLeaveEvent(...):
    def hoverLeaveEvent(self, event, /):
        super().unsetCursor()
        super().hoverLeaveEvent(event)


# Class Vertex:
class VertexItem(QtWidgets.QGraphicsObject):

    # QtCore.Signal(s):
    sig_item_updated = QtCore.Signal(QtWidgets.QGraphicsObject)
    sig_item_focused = QtCore.Signal(QtWidgets.QGraphicsObject)

    sig_handle_created = QtCore.Signal(HandleItem)
    sig_handle_clicked = QtCore.Signal(HandleItem)

    # Default constructor:
    def __init__(
        self,
        cpos: QtCore.QPointF,  # The vertex's position in scene coordinates.
        parent: QtWidgets.QGraphicsObject | None = None,
        **kwargs,  # Additional keyword arguments for customization.
    ):

        # Base-class initialization:
        super().__init__(parent)

        self.setPos(cpos)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsSelectable)

        # Handle database:
        self.setProperty("style", VERTEX_OPTS["style"])
        self.database = types.SimpleNamespace(
            inp=dict(), out=dict(), par=dict(), eqn=list()
        )

        # Initialize an attribute dictionary for serialization and deserialization.
        # This is simpler and faster than using Qt's property system:
        self.attr = {
            "id": id(self),
            "name": kwargs.get("name", "Process"),
            "icon": kwargs.get("icon", None),
            "limit": VERTEX_OPTS["frame"].bottom(),
            "frame": QtCore.QRectF(kwargs.get("frame", VERTEX_OPTS["frame"])),
        }

        # Add anchor(s):
        self._inp_anchor = AnchorItem(
            HandleRole.INP.value,
            parent=self,
            cpos=QtCore.QPointF(self.attr["frame"].left(), 0),
            callback=self.on_anchor_clicked,
        )
        self._out_anchor = AnchorItem(
            HandleRole.OUT.value,
            parent=self,
            cpos=QtCore.QPointF(self.attr["frame"].right(), 0),
            callback=self.on_anchor_clicked,
        )

        # Add a resize-handle at the bottom:
        self._resize_handle = ResizeHandle(
            parent=self, callback=self.on_resize_handle_moved
        )
        self._resize_handle.moveBy(0, self.attr["frame"].bottom())

        # Vertex-icon:
        self._image = Image(
            parent=self,
            buffer=opts.CLIMACT_CONFIG["svg"] + "component.svg",
            size=QtCore.QSize(32, 32),
        )
        self._image.setOpacity(0.20)

        # Vertex-label:
        self._label = Label(
            parent=self,
            label=self.attr["name"],
            color=QtCore.Qt.GlobalColor.white,
            width=self.attr["frame"].width() - 4,
        )
        self._label.setX(self.attr["frame"].left() + 2)
        self._label.setY(self.attr["frame"].top() - 2)
        self._label.sig_text_changed.connect(self.on_text_changed)

        # Initialize configurator and menu:
        self._config = VertexConfig(self, parent=None)
        self._menu = self._init_menu()
        self._register_with_bus()

    # Context-menu initializer:
    def _init_menu(self):

        # Imports:
        import util

        menu = QtWidgets.QMenu()
        edit = menu.addAction(util.qta_icon("mdi.pencil"), "Configure", self.configure)
        lock = menu.addAction(util.qta_icon("mdi.lock"), "Lock")
        delete = menu.addAction(util.qta_icon("mdi.delete"), "Delete")

        edit.setIconVisibleInMenu(True)
        lock.setIconVisibleInMenu(True)
        delete.setIconVisibleInMenu(True)

        lock.setCheckable(True)
        lock.setChecked(False)

        return menu

    # Register this class' signals with the event-bus:
    def _register_with_bus(self):

        # Import bus:
        from schematic import Bus

        bus = Bus.instance()
        self.sig_item_updated.connect(bus.sig_item_updated)
        self.sig_item_focused.connect(bus.sig_item_focused)

    # Method to set coordinate bounds on handles:
    def _set_limit(self, handle: HandleItem):

        ymin = self.mapRectFromItem(
            self._inp_anchor, self._inp_anchor.boundingRect()
        ).top()
        ymax = self.attr["frame"].bottom() - 6

        handle.setProperty("ymin", ymin)
        handle.setProperty("ymax", ymax)

    # Reimplementation of QtWidgets.QGraphicsObject.boundingRect():
    def boundingRect(self) -> QtCore.QRectF:
        return self.attr["frame"].adjusted(-4, -4, 4, 4)

    # Reimplementation of QtWidgets.QGraphicsObject.paint():
    def paint(self, painter, option, /, widget=...):

        # Stylize the painter:
        pen = self.property("style")["pen"]["select" if self.isSelected() else "normal"]
        brush = self.property("style")["brush"][
            "select" if self.isSelected() else "normal"
        ]

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(
            self.attr["frame"],
            VERTEX_OPTS["corner-radius"],
            VERTEX_OPTS["corner-radius"],
        )

        # Draw a white board
        painter.setBrush(VERTEX_OPTS["board"]["brush"])
        painter.drawRoundedRect(
            self.attr["frame"].adjusted(0, 16, -0, -0),
            VERTEX_OPTS["board"]["corner-radius"],
            VERTEX_OPTS["board"]["corner-radius"],
        )

    # Reimplementation of QtWidgets.QGraphicsObject.itemChange():
    def itemChange(self, change, value, /):

        # Import:
        from schematic import Canvas

        # Flag alias:
        scene_flag = QtWidgets.QGraphicsObject.GraphicsItemChange.ItemSceneHasChanged

        # Connect to the canvas's begin_transient() method when added to a scene:
        if change == scene_flag and isinstance(value, Canvas):
            self.sig_item_updated.connect(value.sig_canvas_updated)
            self.sig_handle_created.connect(value.sig_canvas_updated)
            self.sig_handle_clicked.connect(value.begin_transient)

        # Invoke the base-class implementation:
        return super().itemChange(change, value)

    # ------------------------------------------------------------------------------------------------------------------
    # Event handler(s):

    # Reimplementation of QtWidgets.QGraphicsObject.contextMenuEvent():
    def contextMenuEvent(self, event) -> None:

        # Invoke base-class implementation:
        super().contextMenuEvent(event)
        if event.isAccepted():
            return

        if self.scene():
            self.scene().clearSelection()
            self.setSelected(True)

        # Display context-menu:
        if hasattr(self, "_menu"):
            self._menu.exec(event.screenPos())
            event.accept()

    # Reimplementation of QtWidgets.QGraphicsObject.hoverEnterEvent():
    def hoverEnterEvent(self, event) -> None:
        super().setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super().hoverEnterEvent(event)

    # Reimplementation of QtWidgets.QGraphicsObject.hoverLeaveEvent():
    def hoverLeaveEvent(self, event, /):
        super().unsetCursor()
        super().hoverLeaveEvent(event)

    # Reimplement mouseDoubleClickEvent():
    def mouseDoubleClickEvent(self, event, /):

        self.configure()
        super().mouseDoubleClickEvent(event)

    # ------------------------------------------------------------------------------------------------------------------
    # Callback function(s) for user-driven events like resizing, handle-creation, etc.

    # When the vertex's resize-handle is moved:
    def on_resize_handle_moved(self):

        limit = self.attr["limit"]
        frame = self.attr["frame"]
        floor = max(
            [
                handle.y()
                for handle in list(self.database.inp.keys())
                + list(self.database.out.keys())
            ]
            or [limit]
        )

        # Update the frame's bottom based on the handle's position:
        frame.setBottom(max(self._resize_handle.y(), max(floor, limit) + 6))
        self.attr["frame"] = frame

        # Reposition the resize-handle and anchors:
        self._resize_handle.setX(0)
        self._resize_handle.setY(frame.bottom())
        self._inp_anchor.resize(frame.bottom() - 6)
        self._out_anchor.resize(frame.bottom() - 6)

        # Update the floor limit for all handles:
        for handle in list(self.database.inp.keys()) + list(self.database.out.keys()):
            self._set_limit(handle)

        # Redraw to avoid artifacts:
        self.update(self.boundingRect().adjusted(-2, -48, 2, 48))

    # When an anchor is clicked:
    def on_anchor_clicked(self, cpos: QtCore.QPointF):

        anchor = self.sender()  # The anchor that sent the QtCore.Signal
        coords = self.mapFromItem(
            anchor, cpos
        )  # Map the clicked coordinates to the vertex's coordinate system

        # Create a new handle at the clicked position:
        handle = self.create_handle(
            HandleRole.INP if anchor is self._inp_anchor else HandleRole.OUT, coords
        )

        # Set handle limits:
        self._set_limit(handle)

        # Emit QtCore.Signals:
        self.sig_handle_created.emit(
            handle
        )  # This notifies the scene that a new handle has been created.
        self.sig_handle_clicked.emit(
            handle
        )  # This allows users to create the handle and begin a transient with a single click.

    # When the label text is changed:
    def on_text_changed(self, text: str):

        # Update the label property:
        self.attr["name"] = text
        self.sig_item_updated.emit(self)

    # ------------------------------------------------------------------------------------------------------------------
    # Functions that allow programmatic state change. These may return complex objects, and therefore cannot be directly
    # used with LLMs' function-calling frameworks.

    # Serialize the vertex to a JSON-compatible dictionary:
    def serialize_to_dict(self) -> dict:

        # Serialize handles:
        inp = [handle.serialize_to_dict() for handle in self.database.inp.keys()]
        out = [handle.serialize_to_dict() for handle in self.database.out.keys()]

        # Serialize parameters:
        par = copy.deepcopy(self.database.par)

        # Construct the dictionary:
        data = {
            "attr": copy.deepcopy(self.attr),
            "database": {"inp": inp, "out": out, "par": par},
            "cpos": {"x": self.scenePos().x(), "y": self.scenePos().y()},
        }

        return data

    # Create a new handle at the specified position:
    def create_handle(self, role: HandleRole | str, cpos: QtCore.QPointF) -> HandleItem:
        """
        Returns a new handle of the specified role (INP or OUT) at the given position relative to the vertex.
        Can be used with LLM function-calling frameworks (`role` must be a string in that case).
        :param role: HandleRole or str indicating the handle's role (INP or OUT).
        :param cpos: QtCore.QPointF indicating the handle's position relative to the vertex.
        :return:
        """

        if isinstance(role, str):
            role = (
                HandleRole.INP if role.upper() == "INP" else HandleRole.OUT
            )  # Convert the string-role to a `HandleRole`

        # Create the handle:
        handle = HandleItem(
            role,  # Handle's role (INP or OUT).
            cpos,  # Handle's position relative to the vertex.
            self,
            callback=self.sig_handle_clicked,  # Callback function when the handle is clicked.
        )

        # Add the handle to the database:
        if role == HandleRole.INP:
            self.database.inp[handle] = True
        else:
            self.database.out[handle] = True

        # Return the new handle:
        return handle

    # Method to create a new parameter:
    def create_parameter(self, name: str = "Parameter", /):

        self.database.par[name] = True
        self.sig_item_updated.emit(self)

    # Delete this vertex:
    def delete(self):
        self.sig_item_updated.emit(self)
        self.scene().removeItem(self)

    # Clone this vertex:
    def clone(self) -> "VertexItem":

        # Create a new vertex with the same properties:
        vertex = VertexItem(
            cpos=self.scenePos() + QtCore.QPointF(25, 25),
            icon=self.property("icon"),
            limit=self.attr["limit"],
            frame=self.attr["frame"],
            style=self.attr["style"],
            name=self.attr["name"],
        )

        # Return the new vertex:
        return vertex

    # Toggle focus on the vertex's label:
    def toggle_focus(self, focus=True):

        if focus:
            self._label.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)

        else:
            self._label.clearFocus()

    # Open a configuration widget for this vertex:
    def configure(self):
        self.sig_item_focused.emit(self)
        self._config.exec()

    # Highlight this vertex:
    def highlight(self):

        # Center the viewport on this object:
        if canvas := self.scene():
            canvas.clearSelection()
            viewer = canvas.views()[0]
            viewer.centerOn(self)
            self.setSelected(True)

    # Get the vertex's icon:
    def icon(self):
        return self._image.to_icon()
