#!/usr/bin/env python3
"""
Bulling - Bowling & Dartboard Scoring App (Python/Qt6 Version)
Personal Use Only - Not for Distribution

Features:
- Traditional 10-pin bowling with proper scoring
- Interactive dartboard with dartboard-to-bowling transposition
- Both interfaces for backwards compatibility
- Bull head logo with dartboard eyes and bowling pin horns
"""

import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout, QLineEdit,
    QMessageBox, QScrollArea, QInputDialog, QGraphicsDropShadowEffect,
    QSplashScreen, QProgressBar, QTabWidget, QGroupBox, QRadioButton,
    QButtonGroup, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, Property, QSize, QPointF, QRectF
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QRadialGradient, QLinearGradient, QPixmap, QPainterPath


# =============================================================================
# DARTBOARD TO BOWLING PIN MAPPING
# =============================================================================
# Dartboard segments map to bowling pin knockdown patterns
# This creates a transposition between dartboard scores and bowling pins

DARTBOARD_TO_PINS = {
    # Single segments (1-20) - knock down specific pins
    1: [1],           # Single 1 -> Pin 1
    2: [2],           # Single 2 -> Pin 2
    3: [3],           # Single 3 -> Pin 3
    4: [4],           # Single 4 -> Pin 4
    5: [5],           # Single 5 -> Pin 5
    6: [6],           # Single 6 -> Pin 6
    7: [7],           # Single 7 -> Pin 7
    8: [8],           # Single 8 -> Pin 8
    9: [9],           # Single 9 -> Pin 9
    10: [10],         # Single 10 -> Pin 10
    11: [1, 2],       # Single 11 -> Pins 1, 2
    12: [1, 3],       # Single 12 -> Pins 1, 3
    13: [2, 3],       # Single 13 -> Pins 2, 3
    14: [4, 5],       # Single 14 -> Pins 4, 5
    15: [5, 6],       # Single 15 -> Pins 5, 6
    16: [7, 8],       # Single 16 -> Pins 7, 8
    17: [8, 9],       # Single 17 -> Pins 8, 9
    18: [9, 10],      # Single 18 -> Pins 9, 10
    19: [1, 2, 3],    # Single 19 -> Front row pins
    20: [4, 5, 6],    # Single 20 -> Second row pins
    # Special zones
    'D': [1, 2, 3, 4, 5, 6],      # Double ring -> 6 pins (spare potential)
    'T': [7, 8, 9, 10],           # Triple ring -> Back row
    'OB': [1, 2, 3, 5],           # Outer bullseye -> 4 pins
    'IB': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Inner bullseye -> STRIKE!
}


class BullHeadLogo(QWidget):
    """Custom widget that draws the bull head logo with dartboard eyes"""

    def __init__(self, size=200, parent=None):
        super().__init__(parent)
        self._size = size
        self._pulse = 0.0
        self.setFixedSize(size, size)

        self._animation = QPropertyAnimation(self, b"pulse")
        self._animation.setDuration(1500)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setLoopCount(-1)
        self._animation.setEasingCurve(QEasingCurve.InOutSine)

    def start_animation(self):
        self._animation.start()

    def stop_animation(self):
        self._animation.stop()

    def get_pulse(self):
        return self._pulse

    def set_pulse(self, value):
        self._pulse = value
        self.update()

    pulse = Property(float, get_pulse, set_pulse)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = self._size
        pulse_scale = 1.0 + (0.02 * abs(self._pulse - 0.5) * 2)

        # Background circle (brown bull head)
        gradient = QRadialGradient(size/2, size/2, size/2)
        gradient.setColorAt(0, QColor("#8B4513"))
        gradient.setColorAt(0.7, QColor("#6B3410"))
        gradient.setColorAt(1, QColor("#4D2E0C"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#3D1E0C"), max(2, size//100)))

        margin = size * 0.05
        painter.drawEllipse(int(margin), int(margin), int(size - margin*2), int(size - margin*2))

        # Bowling pin horns (left)
        horn_width = size * 0.12
        horn_height = size * 0.22
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#E5E5E5"), max(1, size//150)))
        painter.drawEllipse(int(size * 0.08), int(size * 0.05), int(horn_width), int(horn_height))
        painter.setBrush(QBrush(QColor("#FF3B30")))
        painter.drawRect(int(size * 0.095), int(size * 0.18), int(horn_width * 0.75), int(size * 0.035))

        # Bowling pin horns (right)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#E5E5E5"), max(1, size//150)))
        painter.drawEllipse(int(size * 0.80), int(size * 0.05), int(horn_width), int(horn_height))
        painter.setBrush(QBrush(QColor("#FF3B30")))
        painter.drawRect(int(size * 0.815), int(size * 0.18), int(horn_width * 0.75), int(size * 0.035))

        # Snout
        snout_gradient = QRadialGradient(size/2, size * 0.65, size * 0.25)
        snout_gradient.setColorAt(0, QColor("#E8C9A8"))
        snout_gradient.setColorAt(1, QColor("#D4A574"))
        painter.setBrush(QBrush(snout_gradient))
        painter.setPen(QPen(QColor("#B8956A"), max(1, size//150)))
        painter.drawEllipse(int(size * 0.30), int(size * 0.52), int(size * 0.40), int(size * 0.32))

        # Nostrils
        painter.setBrush(QBrush(QColor("#2C1810")))
        painter.setPen(Qt.NoPen)
        nostril_size = size * 0.06
        painter.drawEllipse(int(size * 0.37), int(size * 0.66), int(nostril_size), int(nostril_size * 1.3))
        painter.drawEllipse(int(size * 0.57), int(size * 0.66), int(nostril_size), int(nostril_size * 1.3))

        # Dartboard eyes - with pulse effect
        eye_size = size * 0.18 * pulse_scale
        eye_offset = (size * 0.18 - eye_size) / 2

        left_x = size * 0.22 + eye_offset
        left_y = size * 0.32 + eye_offset
        self._draw_dartboard_eye(painter, left_x, left_y, eye_size)

        right_x = size * 0.60 + eye_offset
        right_y = size * 0.32 + eye_offset
        self._draw_dartboard_eye(painter, right_x, right_y, eye_size)

    def _draw_dartboard_eye(self, painter, x, y, size):
        painter.setBrush(QBrush(QColor("#1D1D1F")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(x), int(y), int(size), int(size))

        ring1 = size * 0.12
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawEllipse(int(x + ring1), int(y + ring1), int(size - ring1*2), int(size - ring1*2))

        ring2 = size * 0.24
        painter.setBrush(QBrush(QColor("#34C759")))
        painter.drawEllipse(int(x + ring2), int(y + ring2), int(size - ring2*2), int(size - ring2*2))

        ring3 = size * 0.36
        painter.setBrush(QBrush(QColor("#FF3B30")))
        painter.drawEllipse(int(x + ring3), int(y + ring3), int(size - ring3*2), int(size - ring3*2))

        ring4 = size * 0.44
        painter.setBrush(QBrush(QColor("#1D1D1F")))
        painter.drawEllipse(int(x + ring4), int(y + ring4), int(size - ring4*2), int(size - ring4*2))


class InteractiveDartboard(QWidget):
    """Interactive dartboard widget with clickable segments"""

    segment_clicked = Signal(int, str)  # segment number, zone type (S/D/T/OB/IB)

    # Standard dartboard segment order (clockwise from top)
    SEGMENT_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

    def __init__(self, size=350, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setMouseTracking(True)
        self._hover_segment = None
        self._hover_zone = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self._size / 2

        # Draw wire frame / outer ring
        painter.setBrush(QBrush(QColor("#1a1a1a")))
        painter.setPen(QPen(QColor("#333333"), 3))
        painter.drawEllipse(2, 2, self._size - 4, self._size - 4)

        # Draw segments
        segment_angle = 360 / 20
        start_angle = 90 - segment_angle / 2  # Start at top

        for i, segment_num in enumerate(self.SEGMENT_ORDER):
            angle = start_angle - i * segment_angle

            # Determine colors (alternating black/cream, red/green for doubles/triples)
            is_dark = i % 2 == 0

            # Draw segment zones from outside to inside
            self._draw_segment(painter, center, angle, segment_angle, segment_num, is_dark)

        # Draw bullseye rings
        # Outer bull (green)
        ob_radius = self._size * 0.08
        is_hover = self._hover_zone == 'OB'
        painter.setBrush(QBrush(QColor("#5ce65c") if is_hover else QColor("#34C759")))
        painter.setPen(QPen(QColor("#2a9d4a"), 2))
        painter.drawEllipse(QPointF(center, center), ob_radius, ob_radius)

        # Inner bull (red)
        ib_radius = self._size * 0.035
        is_hover = self._hover_zone == 'IB'
        painter.setBrush(QBrush(QColor("#ff6b6b") if is_hover else QColor("#FF3B30")))
        painter.setPen(QPen(QColor("#cc2f27"), 2))
        painter.drawEllipse(QPointF(center, center), ib_radius, ib_radius)

        # Draw segment numbers
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Helvetica Neue", 12, QFont.Bold))

        number_radius = self._size * 0.44
        for i, segment_num in enumerate(self.SEGMENT_ORDER):
            angle_rad = math.radians(start_angle - i * segment_angle)
            x = center + number_radius * math.cos(angle_rad) - 8
            y = center - number_radius * math.sin(angle_rad) + 6
            painter.drawText(int(x), int(y), str(segment_num))

    def _draw_segment(self, painter, center, angle, sweep, segment_num, is_dark):
        """Draw a single segment with all its zones"""

        # Radii for different zones (as fraction of total radius)
        outer_double = self._size * 0.47
        inner_double = self._size * 0.43
        outer_triple = self._size * 0.28
        inner_triple = self._size * 0.25
        inner_single = self._size * 0.10

        # Colors
        dark_color = QColor("#1D1D1F")
        light_color = QColor("#F5E6C8")
        red_color = QColor("#FF3B30")
        green_color = QColor("#34C759")

        hover_light = QColor("#FFFACD")
        hover_dark = QColor("#404040")
        hover_red = QColor("#FF6B6B")
        hover_green = QColor("#5CE65C")

        # Check hover states
        is_hover_d = self._hover_segment == segment_num and self._hover_zone == 'D'
        is_hover_t = self._hover_segment == segment_num and self._hover_zone == 'T'
        is_hover_s = self._hover_segment == segment_num and self._hover_zone == 'S'

        # Outer single zone
        base_color = dark_color if is_dark else light_color
        hover_color = hover_dark if is_dark else hover_light
        self._draw_arc_segment(painter, center, inner_double, outer_triple, angle, sweep,
                               hover_color if is_hover_s else base_color)

        # Double zone (outer ring)
        base_color = red_color if is_dark else green_color
        hover_color = hover_red if is_dark else hover_green
        self._draw_arc_segment(painter, center, outer_double, inner_double, angle, sweep,
                               hover_color if is_hover_d else base_color)

        # Triple zone
        base_color = red_color if is_dark else green_color
        hover_color = hover_red if is_dark else hover_green
        self._draw_arc_segment(painter, center, outer_triple, inner_triple, angle, sweep,
                               hover_color if is_hover_t else base_color)

        # Inner single zone
        base_color = dark_color if is_dark else light_color
        hover_color = hover_dark if is_dark else hover_light
        self._draw_arc_segment(painter, center, inner_triple, inner_single, angle, sweep,
                               hover_color if is_hover_s else base_color)

    def _draw_arc_segment(self, painter, center, outer_r, inner_r, angle, sweep, color):
        """Draw an arc segment between two radii"""
        path = QPainterPath()

        # Create arc segment
        outer_rect = QRectF(center - outer_r, center - outer_r, outer_r * 2, outer_r * 2)
        inner_rect = QRectF(center - inner_r, center - inner_r, inner_r * 2, inner_r * 2)

        # Move to start of outer arc
        start_rad = math.radians(angle + sweep/2)
        path.moveTo(center + outer_r * math.cos(start_rad), center - outer_r * math.sin(start_rad))

        # Draw outer arc
        path.arcTo(outer_rect, angle + sweep/2, -sweep)

        # Line to inner arc
        end_rad = math.radians(angle - sweep/2)
        path.lineTo(center + inner_r * math.cos(end_rad), center - inner_r * math.sin(end_rad))

        # Draw inner arc back
        path.arcTo(inner_rect, angle - sweep/2, sweep)

        path.closeSubpath()

        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        segment, zone = self._get_segment_at(event.pos())
        if segment is not None:
            self.segment_clicked.emit(segment, zone)

    def mouseMoveEvent(self, event):
        segment, zone = self._get_segment_at(event.pos())
        if segment != self._hover_segment or zone != self._hover_zone:
            self._hover_segment = segment
            self._hover_zone = zone
            self.update()

    def leaveEvent(self, event):
        self._hover_segment = None
        self._hover_zone = None
        self.update()

    def _get_segment_at(self, pos):
        """Determine which segment and zone was clicked"""
        center = self._size / 2
        dx = pos.x() - center
        dy = center - pos.y()

        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle += 360

        # Check bullseyes first
        if distance < self._size * 0.035:
            return None, 'IB'
        elif distance < self._size * 0.08:
            return None, 'OB'

        # Determine segment
        segment_angle = 18
        adjusted_angle = (angle - 81) % 360  # Adjust for segment layout
        segment_index = int(adjusted_angle / segment_angle)
        segment_num = self.SEGMENT_ORDER[segment_index % 20]

        # Determine zone
        if distance < self._size * 0.10:
            return segment_num, 'S'
        elif distance < self._size * 0.25:
            return segment_num, 'S'
        elif distance < self._size * 0.28:
            return segment_num, 'T'
        elif distance < self._size * 0.43:
            return segment_num, 'S'
        elif distance < self._size * 0.47:
            return segment_num, 'D'

        return None, None


class SplashScreen(QWidget):
    """Animated splash screen with bull head logo"""

    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 500)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.logo = BullHeadLogo(200)
        layout.addWidget(self.logo, alignment=Qt.AlignCenter)

        title = QLabel("BULLING")
        title.setFont(QFont("Helvetica Neue", 36, QFont.Bold))
        title.setStyleSheet("color: #1D1D1F;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Bowling & Dartboard Scorer")
        subtitle.setFont(QFont("Helvetica Neue", 14))
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        personal = QLabel("Personal Use Only")
        personal.setFont(QFont("Helvetica Neue", 10))
        personal.setStyleSheet("color: #999999;")
        personal.setAlignment(Qt.AlignCenter)
        layout.addWidget(personal)

        layout.addSpacing(20)

        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #E5E5E5;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        self.center_on_screen()
        self.logo.start_animation()

        self._progress_value = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(30)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _update_progress(self):
        self._progress_value += 2
        self.progress.setValue(self._progress_value)

        if self._progress_value >= 100:
            self._timer.stop()
            self.logo.stop_animation()
            QTimer.singleShot(300, self._finish)

    def _finish(self):
        self.finished.emit()
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255, 250)))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRoundedRect(self.rect(), 20, 20)


class Pin(QPushButton):
    """Interactive bowling pin button"""

    def __init__(self, pin_id, parent=None):
        super().__init__(parent)
        self.pin_id = pin_id
        self.standing = True
        self.setFixedSize(50, 50)
        self.update_style()
        self.clicked.connect(self.toggle)

    def toggle(self):
        self.standing = not self.standing
        self.update_style()

    def knock_down(self):
        if self.standing:
            self.standing = False
            self.update_style()

    def update_style(self):
        if self.standing:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 3px solid #1D1D1F;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: bold;
                    color: #1D1D1F;
                }
                QPushButton:hover {
                    background-color: #F5F5F7;
                    border-color: #007AFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF3B30;
                    border: 3px solid #CC2F27;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #FF6961;
                }
            """)
        self.setText(str(self.pin_id))

    def reset(self):
        self.standing = True
        self.update_style()


class Player:
    """Player with 10 frames of bowling data"""

    def __init__(self, name):
        self.name = name
        self.frames = [[None, None, None] for _ in range(10)]
        self.scores = [None] * 10
        self.current_frame = 0
        self.current_throw = 0

    def is_complete(self):
        return self.current_frame >= 10


class BullingApp(QMainWindow):
    """Main Bulling Application with Bowling Pins and Dartboard"""

    def __init__(self):
        super().__init__()
        self.players = []
        self.current_player_index = 0
        self.pins = []
        self.game_started = False
        self.input_mode = 'pins'  # 'pins' or 'dartboard'

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Bulling - Bowling & Dartboard Scorer")
        self.setGeometry(100, 100, 1000, 750)
        self.setStyleSheet("background-color: #F5F5F7;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title with logo
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignCenter)

        title_logo = BullHeadLogo(50)
        title_layout.addWidget(title_logo)

        title = QLabel("BULLING")
        title.setFont(QFont("Helvetica Neue", 32, QFont.Bold))
        title.setStyleSheet("color: #1D1D1F; padding: 10px;")
        title_layout.addWidget(title)

        layout.addWidget(title_container)

        # Status bar
        self.status_label = QLabel("Add players to start a new game")
        self.status_label.setFont(QFont("Helvetica Neue", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #007AFF;
            color: white;
            padding: 10px;
            border-radius: 8px;
        """)
        layout.addWidget(self.status_label)

        # Main content area
        content = QHBoxLayout()

        # Left side - Input modes (Pins / Dartboard)
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #D4A574;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)

        # Mode selector
        mode_group = QGroupBox("Input Mode")
        mode_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #1D1D1F;
                background: transparent;
                border: none;
            }
        """)
        mode_layout = QHBoxLayout(mode_group)

        self.pins_radio = QRadioButton("Bowling Pins")
        self.pins_radio.setChecked(True)
        self.pins_radio.toggled.connect(self.switch_mode)
        self.pins_radio.setStyleSheet("color: #1D1D1F; background: transparent;")

        self.dart_radio = QRadioButton("Dartboard")
        self.dart_radio.setStyleSheet("color: #1D1D1F; background: transparent;")

        mode_layout.addWidget(self.pins_radio)
        mode_layout.addWidget(self.dart_radio)
        input_layout.addWidget(mode_group)

        # Stacked widget for pins/dartboard
        self.input_stack = QStackedWidget()

        # Pins widget
        pins_widget = QWidget()
        pins_widget.setStyleSheet("background: transparent;")
        pins_layout = QVBoxLayout(pins_widget)

        pin_title = QLabel("Click pins to knock down")
        pin_title.setFont(QFont("Helvetica Neue", 12))
        pin_title.setAlignment(Qt.AlignCenter)
        pin_title.setStyleSheet("color: #1D1D1F; background: transparent;")
        pins_layout.addWidget(pin_title)

        self.create_pin_layout(pins_layout)
        self.input_stack.addWidget(pins_widget)

        # Dartboard widget
        dart_widget = QWidget()
        dart_widget.setStyleSheet("background: transparent;")
        dart_layout = QVBoxLayout(dart_widget)

        dart_title = QLabel("Click dartboard segment")
        dart_title.setFont(QFont("Helvetica Neue", 12))
        dart_title.setAlignment(Qt.AlignCenter)
        dart_title.setStyleSheet("color: #1D1D1F; background: transparent;")
        dart_layout.addWidget(dart_title)

        self.dartboard = InteractiveDartboard(300)
        self.dartboard.segment_clicked.connect(self.on_dartboard_hit)
        dart_layout.addWidget(self.dartboard, alignment=Qt.AlignCenter)

        dart_info = QLabel("Segments map to bowling pins!\nBullseye = STRIKE!")
        dart_info.setFont(QFont("Helvetica Neue", 10))
        dart_info.setAlignment(Qt.AlignCenter)
        dart_info.setStyleSheet("color: #666666; background: transparent;")
        dart_layout.addWidget(dart_info)

        self.input_stack.addWidget(dart_widget)
        input_layout.addWidget(self.input_stack)

        # Submit throw button
        self.submit_btn = QPushButton("Submit Throw")
        self.submit_btn.setFont(QFont("Helvetica Neue", 14, QFont.Bold))
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #2DB550;
            }
            QPushButton:disabled {
                background-color: #86868B;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_throw)
        self.submit_btn.setEnabled(False)
        input_layout.addWidget(self.submit_btn)

        # Reset pins button
        reset_pins_btn = QPushButton("Reset Pins")
        reset_pins_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9500;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #CC7700;
            }
        """)
        reset_pins_btn.clicked.connect(self.reset_pins)
        input_layout.addWidget(reset_pins_btn)

        content.addWidget(input_frame, 1)

        # Right side - Scorecard
        score_frame = QFrame()
        score_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        score_layout = QVBoxLayout(score_frame)

        score_title = QLabel("Bowling Scorecard")
        score_title.setFont(QFont("Helvetica Neue", 16, QFont.Bold))
        score_title.setStyleSheet("color: #1D1D1F;")
        score_layout.addWidget(score_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.scorecard_widget = QWidget()
        self.scorecard_layout = QVBoxLayout(self.scorecard_widget)
        scroll.setWidget(self.scorecard_widget)
        score_layout.addWidget(scroll)

        content.addWidget(score_frame, 2)

        layout.addLayout(content)

        # Control buttons
        controls = QHBoxLayout()

        add_player_btn = QPushButton("Add Player")
        add_player_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
        """)
        add_player_btn.clicked.connect(self.add_player)
        controls.addWidget(add_player_btn)

        start_btn = QPushButton("Start Game")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2DB550;
            }
        """)
        start_btn.clicked.connect(self.start_game)
        controls.addWidget(start_btn)

        reset_btn = QPushButton("New Game")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9500;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #CC7700;
            }
        """)
        reset_btn.clicked.connect(self.reset_game)
        controls.addWidget(reset_btn)

        controls.addStretch()

        self.pins_down_label = QLabel("Pins Down: 0")
        self.pins_down_label.setFont(QFont("Helvetica Neue", 14, QFont.Bold))
        self.pins_down_label.setStyleSheet("color: #FF3B30;")
        controls.addWidget(self.pins_down_label)

        layout.addLayout(controls)

    def switch_mode(self, checked):
        """Switch between pins and dartboard input"""
        if checked:
            self.input_stack.setCurrentIndex(0)
            self.input_mode = 'pins'
        else:
            self.input_stack.setCurrentIndex(1)
            self.input_mode = 'dartboard'

    def on_dartboard_hit(self, segment, zone):
        """Handle dartboard segment click - transpose to bowling pins"""
        if not self.game_started:
            QMessageBox.information(self, "Start Game", "Start a game first!")
            return

        # Get pins to knock down based on segment/zone
        pins_to_knock = []

        if zone == 'IB':
            # Inner bullseye = STRIKE (all pins)
            pins_to_knock = list(range(1, 11))
            self.status_label.setText("BULLSEYE! STRIKE!")
        elif zone == 'OB':
            # Outer bullseye
            pins_to_knock = DARTBOARD_TO_PINS.get('OB', [])
            self.status_label.setText(f"Outer Bull! Pins: {pins_to_knock}")
        elif zone == 'D' and segment:
            # Double ring
            pins_to_knock = DARTBOARD_TO_PINS.get('D', [])
            self.status_label.setText(f"Double {segment}! Pins: {pins_to_knock}")
        elif zone == 'T' and segment:
            # Triple ring
            pins_to_knock = DARTBOARD_TO_PINS.get('T', [])
            self.status_label.setText(f"Triple {segment}! Pins: {pins_to_knock}")
        elif zone == 'S' and segment:
            # Single segment
            pins_to_knock = DARTBOARD_TO_PINS.get(segment, [segment % 10 + 1])
            self.status_label.setText(f"Single {segment}! Pins: {pins_to_knock}")

        # Knock down the corresponding pins
        for pin in self.pins:
            if pin.pin_id in pins_to_knock:
                pin.knock_down()

        self.update_pins_count()

    def create_pin_layout(self, parent_layout):
        """Create 10-pin bowling layout"""
        pin_container = QWidget()
        pin_container.setStyleSheet("background: transparent;")
        grid = QGridLayout(pin_container)
        grid.setSpacing(10)

        positions = [
            (3, 1.5, 1),
            (2, 1, 2),
            (2, 2, 3),
            (1, 0.5, 4),
            (1, 1.5, 5),
            (1, 2.5, 6),
            (0, 0, 7),
            (0, 1, 8),
            (0, 2, 9),
            (0, 3, 10),
        ]

        self.pins = []
        for row, col, pin_id in positions:
            pin = Pin(pin_id)
            pin.clicked.connect(self.update_pins_count)
            self.pins.append(pin)
            grid.addWidget(pin, row, int(col * 2), 1, 2)

        parent_layout.addWidget(pin_container)

    def update_pins_count(self):
        """Update the pins knocked down counter"""
        count = sum(1 for pin in self.pins if not pin.standing)
        self.pins_down_label.setText(f"Pins Down: {count}")

    def add_player(self):
        """Add a new player"""
        name, ok = QInputDialog.getText(self, "Add Player", "Enter player name:")
        if ok and name.strip():
            self.players.append(Player(name.strip()))
            self.update_scorecard()
            self.status_label.setText(f"Added {name}. {len(self.players)} player(s) ready.")

    def start_game(self):
        """Start the game"""
        if not self.players:
            QMessageBox.warning(self, "No Players", "Add at least one player first!")
            return

        self.game_started = True
        self.current_player_index = 0
        self.submit_btn.setEnabled(True)
        self.reset_pins()
        self.update_status()
        self.update_scorecard()

    def reset_game(self):
        """Reset for a new game"""
        self.players = []
        self.current_player_index = 0
        self.game_started = False
        self.submit_btn.setEnabled(False)
        self.reset_pins()
        self.status_label.setText("Add players to start a new game")
        self.update_scorecard()

    def reset_pins(self):
        """Reset all pins to standing"""
        for pin in self.pins:
            pin.reset()
        self.update_pins_count()

    def get_pins_knocked(self):
        """Get count of knocked pins"""
        return sum(1 for pin in self.pins if not pin.standing)

    def submit_throw(self):
        """Submit the current throw"""
        if not self.game_started:
            return

        player = self.players[self.current_player_index]
        if player.is_complete():
            self.next_player()
            return

        pins_down = self.get_pins_knocked()
        frame_idx = player.current_frame

        if frame_idx == 9:
            self.handle_10th_frame(player, pins_down)
        else:
            self.handle_regular_frame(player, pins_down)

        self.calculate_all_scores()
        self.update_scorecard()
        self.update_status()

    def handle_regular_frame(self, player, pins_down):
        """Handle throws in frames 1-9"""
        frame_idx = player.current_frame

        if player.current_throw == 0:
            player.frames[frame_idx][0] = pins_down

            if pins_down == 10:
                player.current_frame += 1
                player.current_throw = 0
                self.next_player()
            else:
                player.current_throw = 1
        else:
            player.frames[frame_idx][1] = pins_down
            player.current_frame += 1
            player.current_throw = 0
            self.next_player()

        self.reset_pins()

    def handle_10th_frame(self, player, pins_down):
        """Handle 10th frame with bonus throws"""
        frame = player.frames[9]

        if player.current_throw == 0:
            frame[0] = pins_down
            player.current_throw = 1
            if pins_down == 10:
                self.reset_pins()

        elif player.current_throw == 1:
            frame[1] = pins_down
            first = frame[0]

            if first == 10 or (first + pins_down == 10):
                player.current_throw = 2
                self.reset_pins()
            else:
                player.current_frame = 10
                player.current_throw = 0
                self.next_player()

        elif player.current_throw == 2:
            frame[2] = pins_down
            player.current_frame = 10
            player.current_throw = 0
            self.next_player()

        if player.current_throw != 0 or player.current_frame < 10:
            pass
        else:
            self.reset_pins()

    def next_player(self):
        """Move to next player"""
        self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            self.current_player_index = 0

        attempts = 0
        while self.players[self.current_player_index].is_complete() and attempts < len(self.players):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            attempts += 1

        if all(p.is_complete() for p in self.players):
            self.game_over()
        else:
            self.reset_pins()

    def game_over(self):
        """Handle game completion"""
        self.game_started = False
        self.submit_btn.setEnabled(False)

        winner = max(self.players, key=lambda p: p.scores[9] or 0)
        self.status_label.setText(f"Game Over! Winner: {winner.name} with {winner.scores[9]} points!")
        self.status_label.setStyleSheet("""
            background-color: #34C759;
            color: white;
            padding: 10px;
            border-radius: 8px;
        """)

    def calculate_all_scores(self):
        """Calculate scores for all players using standard bowling rules"""
        for player in self.players:
            cumulative = 0

            for i in range(10):
                frame = player.frames[i]
                first = frame[0]

                if first is None:
                    player.scores[i] = None
                    continue

                if i == 9:
                    score = (first or 0) + (frame[1] or 0) + (frame[2] or 0)
                    cumulative += score
                    player.scores[i] = cumulative
                else:
                    score = self.calculate_frame_score(player, i)
                    if score is not None:
                        cumulative += score
                        player.scores[i] = cumulative
                    else:
                        player.scores[i] = None

    def calculate_frame_score(self, player, frame_idx):
        """Calculate score for a single frame using bowling rules"""
        frame = player.frames[frame_idx]
        first = frame[0]
        second = frame[1]

        if first is None:
            return None

        # Strike
        if first == 10:
            next_frame = player.frames[frame_idx + 1]
            next_first = next_frame[0]

            if next_first is None:
                return None

            if next_first == 10 and frame_idx < 8:
                next_next = player.frames[frame_idx + 2]
                if next_next[0] is None:
                    return None
                return 10 + 10 + next_next[0]
            elif next_first == 10 and frame_idx == 8:
                if next_frame[1] is None:
                    return None
                return 10 + next_first + next_frame[1]
            else:
                if next_frame[1] is None:
                    return None
                return 10 + next_first + next_frame[1]

        if second is None:
            return None

        # Spare
        if first + second == 10:
            next_frame = player.frames[frame_idx + 1]
            if next_frame[0] is None:
                return None
            return 10 + next_frame[0]

        # Open frame
        return first + second

    def update_status(self):
        """Update the status display"""
        if not self.game_started:
            return

        player = self.players[self.current_player_index]
        frame_num = player.current_frame + 1
        throw_num = player.current_throw + 1

        self.status_label.setText(f"{player.name} - Frame {frame_num}, Throw {throw_num}")
        self.status_label.setStyleSheet("""
            background-color: #007AFF;
            color: white;
            padding: 10px;
            border-radius: 8px;
        """)

    def update_scorecard(self):
        """Update the scorecard display"""
        for i in reversed(range(self.scorecard_layout.count())):
            widget = self.scorecard_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.players:
            no_players = QLabel("No players yet")
            no_players.setFont(QFont("Helvetica Neue", 12))
            no_players.setStyleSheet("color: #86868B;")
            self.scorecard_layout.addWidget(no_players)
            return

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setSpacing(2)

        name_label = QLabel("Player")
        name_label.setFixedWidth(80)
        name_label.setFont(QFont("Helvetica Neue", 10, QFont.Bold))
        header_layout.addWidget(name_label)

        for i in range(1, 11):
            frame_label = QLabel(str(i))
            frame_label.setFixedWidth(45)
            frame_label.setAlignment(Qt.AlignCenter)
            frame_label.setFont(QFont("Helvetica Neue", 10, QFont.Bold))
            header_layout.addWidget(frame_label)

        total_label = QLabel("Total")
        total_label.setFixedWidth(50)
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setFont(QFont("Helvetica Neue", 10, QFont.Bold))
        header_layout.addWidget(total_label)

        self.scorecard_layout.addWidget(header)

        for idx, player in enumerate(self.players):
            is_current = idx == self.current_player_index and self.game_started

            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setSpacing(2)

            if is_current:
                row.setStyleSheet("background-color: #E3F2FD; border-radius: 4px;")

            name = QLabel(player.name[:8])
            name.setFixedWidth(80)
            name.setFont(QFont("Helvetica Neue", 10, QFont.Bold if is_current else QFont.Normal))
            row_layout.addWidget(name)

            for i in range(10):
                frame_widget = self.create_frame_widget(player, i)
                row_layout.addWidget(frame_widget)

            total = player.scores[9] if player.scores[9] else "-"
            total_lbl = QLabel(str(total))
            total_lbl.setFixedWidth(50)
            total_lbl.setAlignment(Qt.AlignCenter)
            total_lbl.setFont(QFont("Helvetica Neue", 12, QFont.Bold))
            total_lbl.setStyleSheet("color: #007AFF;")
            row_layout.addWidget(total_lbl)

            self.scorecard_layout.addWidget(row)

        self.scorecard_layout.addStretch()

    def create_frame_widget(self, player, frame_idx):
        """Create a widget for a single frame"""
        frame = player.frames[frame_idx]
        score = player.scores[frame_idx]

        widget = QFrame()
        widget.setFixedWidth(45)
        widget.setStyleSheet("""
            QFrame {
                background-color: #F5F5F7;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(2, 2, 2, 2)

        throws_widget = QWidget()
        throws_layout = QHBoxLayout(throws_widget)
        throws_layout.setSpacing(1)
        throws_layout.setContentsMargins(0, 0, 0, 0)

        if frame_idx < 9:
            t1 = self.format_throw(frame[0], is_strike=True)
            t2 = self.format_throw(frame[1], prev=frame[0])

            for t in [t1, t2]:
                lbl = QLabel(t)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Helvetica Neue", 9))
                if t == 'X':
                    lbl.setStyleSheet("color: #FF3B30; font-weight: bold;")
                elif t == '/':
                    lbl.setStyleSheet("color: #34C759; font-weight: bold;")
                throws_layout.addWidget(lbl)
        else:
            t1 = self.format_throw(frame[0], is_strike=True)
            t2 = self.format_throw_10th(frame[1], frame[0])
            t3 = self.format_throw_10th(frame[2], frame[1] if frame[0] != 10 else None)

            for t in [t1, t2, t3]:
                lbl = QLabel(t)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Helvetica Neue", 8))
                if t == 'X':
                    lbl.setStyleSheet("color: #FF3B30; font-weight: bold;")
                elif t == '/':
                    lbl.setStyleSheet("color: #34C759; font-weight: bold;")
                throws_layout.addWidget(lbl)

        layout.addWidget(throws_widget)

        score_lbl = QLabel(str(score) if score is not None else "")
        score_lbl.setAlignment(Qt.AlignCenter)
        score_lbl.setFont(QFont("Helvetica Neue", 10, QFont.Bold))
        layout.addWidget(score_lbl)

        return widget

    def format_throw(self, throw, is_strike=False, prev=None):
        """Format a throw for display"""
        if throw is None:
            return ""
        if is_strike and throw == 10:
            return "X"
        if prev is not None and prev + throw == 10:
            return "/"
        if throw == 0:
            return "-"
        return str(throw)

    def format_throw_10th(self, throw, prev):
        """Format 10th frame throws"""
        if throw is None:
            return ""
        if throw == 10:
            return "X"
        if prev is not None and prev + throw == 10:
            return "/"
        if throw == 0:
            return "-"
        return str(throw)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Bulling")
    app.setOrganizationName("Personal Use")

    splash = SplashScreen()
    splash.show()

    window = BullingApp()

    def show_main_window():
        window.show()
        screen = app.primaryScreen().geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        window.move(x, y)

    splash.finished.connect(show_main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
