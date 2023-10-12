# Created by Nemesis
# nemesisuks@protonmail.com

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from urllib.parse import urlsplit

class NWUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, headers):
        super().__init__()
        self.headers = headers

    def set_headers(self, headers):
        self.headers = headers

    def interceptRequest(self, info):
        print(info, self.headers)
        for header, value in self.headers:
            info.setHttpHeader(QByteArray(bytes(header, 'utf-8')), QByteArray(bytes(value, 'utf-8')))

class WebEngineProfile(QWebEngineProfile):
    def cookieFilter(self, url, cookie):
        # Disables third-party cookies
        if url.host() != cookie.domain():
            return False
        return True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Creates a QWebEngineView
        self.browser = QWebEngineView()

        # Creates a custom profile
        self.profile = WebEngineProfile()

        # Sets the custom profile for the browser
        self.browser.setPage(QWebEnginePage(self.profile))

        # Disables JavaScript by default
        settings = self.browser.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)  # Disable WebRTC

        # Disables local storage (caching)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)

        # Disables file access
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)

        # Sets custom User-Agent string
        user_agent = "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0"
        self.browser.page().profile().setHttpUserAgent(user_agent)

        # Sets the central widget
        self.setCentralWidget(self.browser)

        # Shows the window maximized
        self.showMaximized()

        # Creates a navigation toolbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Adds navigation actions (Back, Forward, Reload, Home)
        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # Button for I2P Router Console
        custom_redirect_btn = QAction(QIcon('i2p_icon.png'), 'I2P Router Console', self)
        custom_redirect_btn.triggered.connect(self.custom_redirect)
        navbar.addAction(custom_redirect_btn)

        # Creates a URL input field
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Creates a proxy switch
        self.proxy_switch = QCheckBox('Use I2P Proxy', self)
        self.proxy_switch.stateChanged.connect(self.toggle_proxy)
        navbar.addWidget(self.proxy_switch)

        # Creates a status label for proxy
        self.status_label = QLabel("Proxy Status: Disconnected", self)
        navbar.addWidget(self.status_label)

        # Connects the URL change signal to update the URL bar
        self.browser.urlChanged.connect(self.update_url)

        # Sets up a proxy (Initially enabled)
        self.proxy_enabled = True
        self.proxy = QNetworkProxy()
        self.proxy.setType(QNetworkProxy.HttpProxy)
        self.proxy.setHostName("127.0.0.1")
        self.proxy.setPort(4444)

        # Initialize the NWUrlRequestInterceptor with default headers
        default_headers = [
            ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"),
            ("Accept-Language", "en-US,en;q=0.5"),
            ("Accept-Encoding", "gzip, deflate, br")
        ]
        self.request_interceptor = NWUrlRequestInterceptor(default_headers)
        self.browser.page().profile().setUrlRequestInterceptor(self.request_interceptor)

        # Enables the proxy initially and set the checkbox state
        self.toggle_proxy(Qt.Checked)

        # Sets the initial URL
        self.browser.setUrl(QUrl('http://legwork.i2p/'))

    def toggle_proxy(self, state):
        if state == Qt.Checked:
            QNetworkProxy.setApplicationProxy(self.proxy)
            self.proxy_enabled = True
        else:
            QNetworkProxy.setApplicationProxy(QNetworkProxy())
            self.proxy_enabled = False
        self.update_proxy_status()
        # Sets the checkbox state to match the proxy state
        self.proxy_switch.setChecked(self.proxy_enabled)

    def navigate_home(self):
        use_i2p_proxy = self.proxy_switch.isChecked()
        if use_i2p_proxy:
            # If the checkbox is checked, use the Legwork I2P URL
            self.browser.setUrl(QUrl('http://legwork.i2p/'))
        else:
            # If the checkbox is unchecked, use the clearnet URL
            self.browser.setUrl(QUrl('https://i2pengine.com/'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url  # Adds 'http://' prefix if missing
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        url = q.toString()
        parsed_url = urlsplit(url)
        hostname = parsed_url.hostname

        if url.startswith("https://"):
            self.url_bar.setStyleSheet("color: green;")
        elif hostname == "localhost" or hostname == "127.0.0.1":
            self.url_bar.setStyleSheet("color: black;")
        elif "http://127.0.0.1:7657/" in url:
            self.url_bar.setStyleSheet("color: black;")
        elif parsed_url.netloc.endswith(".i2p"):
            self.url_bar.setStyleSheet("color: green;")
        else:
            self.url_bar.setStyleSheet("color: red")

        self.url_bar.setText(url)


    def update_proxy_status(self):
        if self.proxy_enabled:
            self.status_label.setText("Proxy Status: Connected")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Proxy Status: Disconnected")
            self.status_label.setStyleSheet("color: red;")

    def custom_redirect(self):
        # Redirects to http://127.0.0.1:7657/ (I2P Router Console)
        self.browser.setUrl(QUrl('http://127.0.0.1:7657/'))

    def closeEvent(self, event):
        # Clears browsing data when the application is closed
        self.browser.page().history().clear()
        self.browser.page().profile().clearAllVisitedLinks()
        event.accept()

app = QApplication(["Browser.py", "--qt-flag", "host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1"])
QApplication.setApplicationName('I2P Browser')
window = MainWindow()
# Loads and sets the application icon
app_icon = QIcon("i2p_icon.png")
app.setWindowIcon(app_icon)
app.exec_()
