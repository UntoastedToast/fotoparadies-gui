import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox,
                           QScrollArea, QFrame, QSizePolicy, QStyle, QStyleFactory,
                           QComboBox, QInputDialog, QDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import QTimer, Qt, QRect, QRectF, QSize, QUrl
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPainterPath, QIcon, QLinearGradient
from PyQt6.QtGui import QDesktopServices
from platformdirs import user_data_dir
from fotoparadies.main import get_orders_list, save_orders_list
from fotoparadies.fotoparadies import FotoparadiesStatus

class FluentCard(QFrame):
    def __init__(self, status=None):
        super().__init__()
        self.setObjectName("fluentCard")
        self.status = status

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Basis-Rechteck
        path = QPainterPath()
        rect = QRectF(2, 2, self.width()-4, self.height()-4)
        path.addRoundedRect(rect, 8, 8)  # Größerer Radius für Fluent Design
        
        # Status-spezifische Farben (Windows 11 Fluent Farben)
        if self.status == "ERROR":
            status_color = QColor("#FD8183")  # Fluent Error Red
        elif self.status == "DELIVERED":
            status_color = QColor("#60CDAE")  # Fluent Success Green
        elif self.status == "READY":
            status_color = QColor("#60A5FA")  # Fluent Info Blue
        else:
            status_color = QColor("#FDB022")  # Fluent Warning Orange
        
        # Hintergrund und Effekte basierend auf System-Theme
        if QApplication.palette().window().color().lightness() > 128:
            # Light Mode
            bg_color = QColor(255, 255, 255)
            if self.status:
                # Mica-Effekt (Layer 1)
                painter.fillPath(path, QColor(255, 255, 255, 240))
                
                # Status-Akzent (Layer 2)
                accent_path = QPainterPath()
                accent_rect = QRectF(2, 2, 4, self.height()-4)
                accent_path.addRoundedRect(accent_rect, 2, 2)
                painter.fillPath(accent_path, status_color)
                
                # Subtle Glow (Layer 3)
                glow = QLinearGradient(0, 0, 8, 0)
                glow_color = status_color
                glow_color.setAlpha(15)
                glow.setColorAt(0, glow_color)
                glow.setColorAt(1, QColor(255, 255, 255, 0))
                painter.fillRect(6, 2, 8, self.height()-4, glow)
            else:
                painter.fillPath(path, QColor(255, 255, 255, 240))
            
            # Border
            painter.setPen(QColor(0, 0, 0, 15))
        else:
            # Dark Mode
            bg_color = QColor(45, 45, 45)
            if self.status:
                # Mica-Effekt (Layer 1)
                painter.fillPath(path, QColor(45, 45, 45, 240))
                
                # Status-Akzent (Layer 2)
                accent_path = QPainterPath()
                accent_rect = QRectF(2, 2, 4, self.height()-4)
                accent_path.addRoundedRect(accent_rect, 2, 2)
                painter.fillPath(accent_path, status_color)
                
                # Subtle Glow (Layer 3)
                glow = QLinearGradient(0, 0, 8, 0)
                glow_color = status_color
                glow_color.setAlpha(20)
                glow.setColorAt(0, glow_color)
                glow.setColorAt(1, QColor(45, 45, 45, 0))
                painter.fillRect(6, 2, 8, self.height()-4, glow)
            else:
                painter.fillPath(path, QColor(45, 45, 45, 240))
            
            # Border
            painter.setPen(QColor(255, 255, 255, 15))
        
        painter.drawPath(path)

class OrderCard(FluentCard):
    def __init__(self, order, main_window=None):
        super().__init__(status=order.currentstatus)
        self.order = order
        self.main_window = main_window
        self.setup_ui()
        
        # Mache die Karte klickbar
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """Öffnet die Fotoparadies-Website mit den korrekten Parametern"""
        if event.button() == Qt.MouseButton.LeftButton:
            url = f"https://www.fotoparadies.de/service/auftragsstatus.html#/?orderid={self.order._order}&locationid={self.order._shop}"
            QDesktopServices.openUrl(QUrl(url))
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Status Icon (Emoji)
        icon_label = QLabel()
        if self.order.currentstatus == "READY":
            icon_label.setText("✅")  # Grüner Haken
            status_color = "#107C10"  # Grün
        elif self.order.currentstatus == "DELIVERED":
            icon_label.setText("📦")  # Paket
            status_color = "#0078D4"  # Blau
        else:
            icon_label.setText("⏳")  # Sanduhr
            status_color = "#797775"  # Grau
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        layout.addWidget(icon_label)
        
        # Info Container
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        
        # Erste Zeile: Shop und Bestellnummer
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        shop_label = QLabel(f"Shop {self.order._shop}")
        shop_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        header_layout.addWidget(shop_label)
        
        order_label = QLabel(f"#{self.order._order}")
        order_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(order_label)
        
        header_layout.addStretch()
        info_layout.addWidget(header_widget)
        
        # Zweite Zeile: Status
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(5)
        
        status_label = QLabel(self.order.currentstatus)
        status_label.setFont(QFont("Segoe UI", 11))
        status_label.setStyleSheet(f"color: {status_color};")
        status_layout.addWidget(status_label)
        
        # Browser Emoji zum Öffnen der Website
        browser_button = QPushButton("🌐")
        browser_button.setFont(QFont("Segoe UI", 11))
        browser_button.setCursor(Qt.CursorShape.PointingHandCursor)
        browser_button.setToolTip("Website öffnen")
        browser_button.setStyleSheet("QPushButton { border: none; background: transparent; padding: 0px; }")
        browser_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://www.fotoparadies.de/service/auftragsstatus.html#/?orderid={self.order._order}&locationid={self.order._shop}")))
        status_layout.addWidget(browser_button)
        
        status_layout.addStretch()
        info_layout.addWidget(status_container)
        
        layout.addWidget(info_container)
        layout.addStretch()
        
        # Löschen Button
        delete_button = QPushButton("Löschen")
        delete_button.setFont(QFont("Segoe UI", 11))
        delete_button.setObjectName("deleteButton")  # Spezielles Styling für Löschen-Button
        delete_button.clicked.connect(lambda: self.main_window.remove_order(self.order))
        layout.addWidget(delete_button)

class ManageFavoritesDialog(QDialog):
    def __init__(self, parent=None, favorites=None):
        super().__init__(parent)
        self.favorites = favorites or []
        self.setWindowTitle("Favoriten verwalten")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Liste der Favoriten
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Segoe UI", 11))
        for shop in self.favorites:
            item = QListWidgetItem(shop)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        delete_button = QPushButton("Löschen")
        delete_button.setFont(QFont("Segoe UI", 11))
        delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_button)
        
        close_button = QPushButton("Schließen")
        close_button.setFont(QFont("Segoe UI", 11))
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
    
    def delete_selected(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            shop = item.text()
            if shop in self.favorites:
                self.favorites.remove(shop)
            self.list_widget.takeItem(self.list_widget.row(item))

class FotoparadiesGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Windows Fluent Design Style aktivieren
        QApplication.setStyle(QStyleFactory.create("Windows"))
        
        # Favoriten laden
        self.favorites_file = Path(user_data_dir("fotoparadies", "Janik Rapp")) / "favorites.json"
        self.favorites_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_favorites()
        
        # System-Theme erkennen und anwenden
        self.update_theme()
        
        self.setWindowTitle("Fotoparadies Status Tracker")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
    
    def load_favorites(self):
        """Lade gespeicherte Favoriten"""
        self.favorites = []
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, 'r') as f:
                    self.favorites = json.load(f)
            except:
                self.favorites = []
    
    def save_favorites(self):
        """Speichere Favoriten"""
        try:
            with open(self.favorites_file, 'w') as f:
                json.dump(self.favorites, f)
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Favoriten konnten nicht gespeichert werden: {str(e)}")
    
    def add_new_shop(self):
        """Füge neue Shopnummer hinzu"""
        shop, ok = QInputDialog.getText(self, "Neue Shopnummer", 
                                      "Geben Sie die neue Shopnummer ein:",
                                      QLineEdit.EchoMode.Normal)
        if ok and shop:
            shop = shop.strip()
            if shop and shop not in self.favorites:
                self.favorites.append(shop)
                self.save_favorites()
                # Aktualisiere ComboBox
                self.shop_combo.clear()
                self.shop_combo.addItems(self.favorites)
                self.shop_combo.addItem("+ Neue Shopnummer")
                self.shop_combo.addItem("Favoriten verwalten...")
                # Wähle neue Nummer aus
                self.shop_combo.setCurrentText(shop)
    
    def on_shop_selected(self, index):
        """Handler für Shop-Auswahl"""
        current_text = self.shop_combo.currentText()
        if current_text == "+ Neue Shopnummer":
            self.add_new_shop()
        elif current_text == "Favoriten verwalten...":
            self.manage_favorites()
    
    def manage_favorites(self):
        """Öffne Dialog zum Verwalten der Favoriten"""
        dialog = ManageFavoritesDialog(self, self.favorites)
        if dialog.exec():
            # Übernehme die geänderte Favoritenliste
            self.favorites = dialog.favorites
            self.save_favorites()
            
            # Aktualisiere ComboBox
            current_text = self.shop_combo.currentText()
            self.shop_combo.clear()
            self.shop_combo.addItems(self.favorites)
            self.shop_combo.addItem("+ Neue Shopnummer")
            self.shop_combo.addItem("Favoriten verwalten...")
            
            # Versuche, die vorherige Auswahl wiederherzustellen
            if current_text in self.favorites:
                self.shop_combo.setCurrentText(current_text)
    
    def setup_ui(self):
        # Hauptwidget und Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Titel
        title = QLabel("Fotoparadies Status Tracker")
        title.setFont(QFont("Segoe UI", 24))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(title)

        # Input Layout für Eingabefelder
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)

        # Shop Layout
        shop_widget = FluentCard()
        shop_layout = QHBoxLayout(shop_widget)
        shop_layout.setContentsMargins(15, 15, 15, 15)
        shop_layout.setSpacing(10)

        shop_label = QLabel("Shop:")
        shop_label.setFont(QFont("Segoe UI", 11))
        shop_layout.addWidget(shop_label)

        # ComboBox für Shops
        self.shop_combo = QComboBox()
        self.shop_combo.setFont(QFont("Segoe UI", 11))
        self.shop_combo.addItems(self.favorites)
        self.shop_combo.addItem("+ Neue Shopnummer")
        self.shop_combo.addItem("Favoriten verwalten...")
        self.shop_combo.currentIndexChanged.connect(self.on_shop_selected)
        shop_layout.addWidget(self.shop_combo)
        
        input_layout.addWidget(shop_widget)

        # Order Layout
        order_widget = FluentCard()
        order_layout = QHBoxLayout(order_widget)
        order_layout.setContentsMargins(15, 15, 15, 15)
        order_layout.setSpacing(10)

        # Order Number Input
        order_label = QLabel("Bestellnummer:")
        order_label.setFont(QFont("Segoe UI", 11))
        order_layout.addWidget(order_label)

        self.order_input = QLineEdit()
        self.order_input.setFont(QFont("Segoe UI", 11))
        self.order_input.setPlaceholderText("z.B. 12345678")
        self.order_input.returnPressed.connect(self.add_order)  # Enter-Taste Handler
        order_layout.addWidget(self.order_input)

        # Add Order Button
        add_button = QPushButton("Hinzufügen")
        add_button.setFont(QFont("Segoe UI", 11))
        add_button.clicked.connect(self.add_order)
        order_layout.addWidget(add_button)

        input_layout.addWidget(order_widget)

        main_layout.addLayout(input_layout)

        # Scroll-Bereich für Karten
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        scroll.setWidget(self.cards_widget)
        main_layout.addWidget(scroll)
        
        # Button-Leiste
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        
        refresh_button = QPushButton("Aktualisieren")
        refresh_button.setFont(QFont("Segoe UI", 11))
        refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_button.clicked.connect(self.refresh_orders)
        button_layout.addWidget(refresh_button)
        
        cleanup_button = QPushButton("Aufräumen")
        cleanup_button.setFont(QFont("Segoe UI", 11))
        cleanup_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cleanup_button.clicked.connect(self.cleanup_orders)
        button_layout.addWidget(cleanup_button)
        
        main_layout.addWidget(button_widget)
        
        # Timer für automatische Aktualisierung (alle 5 Minuten)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_orders)
        self.timer.start(300000)  # 300000 ms = 5 Minuten
        
        # Initial orders laden
        self.refresh_orders()
    
    def update_theme(self):
        """Aktualisiert das Farbschema basierend auf dem System-Theme"""
        is_dark = QApplication.palette().window().color().lightness() <= 128
        accent_color = QApplication.palette().highlight().color().name()
        
        if is_dark:
            self.setStyleSheet(f"""
                QMainWindow, QScrollArea, QWidget {{
                    background-color: #202020;
                    color: #FFFFFF;
                }}
                QLineEdit, QComboBox {{
                    padding: 8px;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    background: #2D2D2D;
                    color: #FFFFFF;
                }}
                QComboBox::drop-down {{
                    border: none;
                    padding-right: 8px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border: none;
                }}
                QLineEdit:focus, QComboBox:focus {{
                    border: 1px solid {accent_color};
                }}
                QPushButton {{
                    padding: 8px 16px;
                    border-radius: 4px;
                    background: rgba(255, 255, 255, 0.06);
                    color: #FFFFFF;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                QPushButton:hover {{
                    background: rgba(255, 255, 255, 0.08);
                }}
                QPushButton:pressed {{
                    background: rgba(255, 255, 255, 0.04);
                }}
                QPushButton#primary {{
                    background: {accent_color};
                    border: 1px solid {accent_color};
                }}
                QPushButton#primary:hover {{
                    opacity: 0.9;
                }}
                QPushButton#primary:pressed {{
                    opacity: 0.8;
                }}
                QLabel {{
                    color: #FFFFFF;
                    background: transparent;
                }}
                #fluentCard {{
                    background: transparent;
                    border: none;
                }}
                OrderCard QWidget {{
                    background: transparent;
                }}
                #deleteButton {{
                    background: rgba(255, 0, 0, 0.1);
                    border: 1px solid rgba(255, 0, 0, 0.2);
                    color: #FF99A4;
                }}
                #deleteButton:hover {{
                    background: rgba(255, 0, 0, 0.15);
                }}
                #deleteButton:pressed {{
                    background: rgba(255, 0, 0, 0.08);
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #FFFFFF;
                }}
                QLineEdit, QComboBox {{
                    padding: 8px;
                    border: 1px solid #E5E5E5;
                    border-radius: 4px;
                    background: #FFFFFF;
                }}
                QComboBox::drop-down {{
                    border: none;
                    padding-right: 8px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border: none;
                }}
                QLineEdit:focus, QComboBox:focus {{
                    border: 1px solid {accent_color};
                }}
                QPushButton {{
                    padding: 8px 16px;
                    border-radius: 4px;
                    background: rgba(0, 0, 0, 0.03);
                    color: #000000;
                    border: 1px solid rgba(0, 0, 0, 0.06);
                }}
                QPushButton:hover {{
                    background: rgba(0, 0, 0, 0.05);
                }}
                QPushButton:pressed {{
                    background: rgba(0, 0, 0, 0.02);
                }}
                QPushButton#primary {{
                    background: {accent_color};
                    border: 1px solid {accent_color};
                    color: white;
                }}
                QPushButton#primary:hover {{
                    opacity: 0.9;
                }}
                QPushButton#primary:pressed {{
                    opacity: 0.8;
                }}
                #fluentCard {{
                    background: transparent;
                    border: none;
                }}
                OrderCard QWidget {{
                    background: transparent;
                }}
                #deleteButton {{
                    background: rgba(255, 0, 0, 0.05);
                    border: 1px solid rgba(255, 0, 0, 0.1);
                    color: #C42B1C;
                }}
                #deleteButton:hover {{
                    background: rgba(255, 0, 0, 0.08);
                }}
                #deleteButton:pressed {{
                    background: rgba(255, 0, 0, 0.03);
                }}
            """)
    
    def on_favorite_selected(self, text):
        """Wenn eine Shopnummer aus den Favoriten ausgewählt wird"""
        if text:
            self.shop_combo.setCurrentText(text)
    
    def add_order(self):
        """Fügt eine neue Bestellung hinzu"""
        shop = self.shop_combo.currentText()
        if shop == "+ Neue Shopnummer" or shop == "Favoriten verwalten...":
            return
            
        order_number = self.order_input.text().strip()
        if not order_number:
            return
            
        try:
            # Konvertiere Eingaben zu Integers
            shop_number = int(shop)
            order_number = int(order_number)
            
            # Erstelle neue Bestellung
            new_order = FotoparadiesStatus(shop_number, order_number)
            
            # Prüfen ob Bestellung bereits existiert
            orders = get_orders_list()
            for existing in orders:
                if existing._shop == shop_number and existing._order == order_number:
                    QMessageBox.warning(
                        self,
                        "Bestellung existiert bereits",
                        "Diese Bestellung wurde bereits hinzugefügt."
                    )
                    return
            
            # Bestellung hinzufügen
            orders.append(new_order)
            save_orders_list(orders)
            
            # UI aktualisieren
            self.order_input.clear()
            self.refresh_orders()
            
        except ValueError:
            QMessageBox.warning(
                self,
                "Ungültige Eingabe",
                "Bitte geben Sie gültige Zahlen für Shop und Bestellnummer ein."
            )
    
    def remove_order(self, order_to_remove):
        orders = get_orders_list()
        orders = [order for order in orders if order.ordername != order_to_remove.ordername]
        save_orders_list(orders)
        self.refresh_orders()
    
    def refresh_orders(self):
        # Bestehende Karten entfernen
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Neue Karten erstellen
        orders = get_orders_list()
        for order in orders:
            order.refresh()  # Status aktualisieren
            card = OrderCard(order, main_window=self)
            self.cards_layout.addWidget(card)
        
        # Platzhalter am Ende hinzufügen
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.cards_layout.addWidget(spacer)
    
    def cleanup_orders(self):
        orders = get_orders_list()
        # Nur Bestellungen behalten, die nicht den Status "DELIVERED" haben
        orders = [order for order in orders if order.currentstatus != "DELIVERED"]
        save_orders_list(orders)
        self.refresh_orders()

def main():
    app = QApplication(sys.argv)
    window = FotoparadiesGUI()
    window.show()
    sys.exit(app.exec())
