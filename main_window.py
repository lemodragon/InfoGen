#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoGen-信息生成器 - PyQt5主界面
现代化GUI设计，提供直观的用户体验
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QCheckBox, QSpinBox, QGroupBox, 
                             QFrame, QSplitter, QMenuBar, QStatusBar,
                             QMessageBox, QFileDialog, QGridLayout, 
                             QTabWidget, QComboBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor

from name_generator import NameGenerator, PhoneGenerator
from vcf_generator import VCFGenerator


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和打包环境"""
    try:
        # PyInstaller打包后的临时目录
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path is None:
            raise AttributeError
    except AttributeError:
        # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class NameGeneratorThread(QThread):
    """姓名生成工作线程，避免界面卡顿"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, generator, count, gender):
        super().__init__()
        self.generator = generator
        self.count = count
        self.gender = gender
    
    def run(self):
        try:
            names = self.generator.generate_names(self.count, self.gender)
            self.finished.emit(names)
        except Exception as e:
            self.error.emit(str(e))


class PhoneGeneratorThread(QThread):
    """手机号生成工作线程"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, generator, count, carrier, prefix):
        super().__init__()
        self.generator = generator
        self.count = count
        self.carrier = carrier
        self.prefix = prefix
    
    def run(self):
        try:
            phones = self.generator.generate_phone_numbers(
                self.count, 
                prefix=self.prefix if self.prefix != "随机" else None,
                carrier=self.carrier if self.carrier != "全部" else None
            )
            self.finished.emit(phones)
        except Exception as e:
            self.error.emit(str(e))


class VCFGeneratorThread(QThread):
    """VCF文件生成工作线程"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, generator, file_count, contacts_per_file, 
                 output_dir, filename_prefix, gender, carrier,
                 naming_mode="timestamp", start_number=1, number_format="{:03d}"):
        super().__init__()
        self.generator = generator
        self.file_count = file_count
        self.contacts_per_file = contacts_per_file
        self.output_dir = output_dir
        self.filename_prefix = filename_prefix
        self.gender = gender
        self.carrier = carrier
        self.naming_mode = naming_mode
        self.start_number = start_number
        self.number_format = number_format
    
    def run(self):
        try:
            result = self.generator.generate_vcf_files(
                file_count=self.file_count,
                contacts_per_file=self.contacts_per_file,
                output_dir=self.output_dir,
                filename_prefix=self.filename_prefix,
                gender=self.gender,
                carrier=self.carrier if self.carrier != "全部" else None,
                progress_callback=self.progress.emit,
                naming_mode=self.naming_mode,
                start_number=self.start_number,
                number_format=self.number_format
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.name_generator = NameGenerator()
        self.phone_generator = PhoneGenerator()
        self.vcf_generator = VCFGenerator()
        
        # 存储生成的数据
        self.generated_names = []
        self.generated_phones = []
        
        # 设置配置
        self.settings = QSettings("InfoGen", "InfoGen")
        
        self.init_ui()
        self.restore_window_state()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("InfoGen v3.0 - 多功能信息生成器")
        
        # 动态计算最小窗口尺寸，确保界面可用性的同时允许用户灵活调整
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        dpi_ratio = screen.logicalDotsPerInch() / 96.0
        
        # 调整为更合理的最小尺寸，确保用户可以缩小窗口
        base_min_width = 580  # 基础最小宽度，足够显示标签栏和控件
        base_min_height = 650  # 基础最小高度，足够显示主要功能区域
        
        min_width = max(base_min_width, int(base_min_width * dpi_ratio))
        min_height = max(base_min_height, int(base_min_height * dpi_ratio))
        self.setMinimumSize(min_width, min_height)
        
        # 调试信息：显示当前的最小尺寸设置
        print(f"窗口最小尺寸设置: {min_width}x{min_height} (DPI比例: {dpi_ratio:.2f})")
        
        # 仅在没有保存的窗口状态时设置默认几何尺寸
        saved_geometry = self.settings.value("geometry")
        if not saved_geometry:
            self.setGeometry(100, 100, 1000, 850)
        
        # 设置窗口图标
        icon_path = get_resource_path('app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        self.create_title_section(main_layout)
        
        # 创建标签页
        self.create_tab_widget(main_layout)
        
        # 创建状态栏
        self.create_status_bar()
        
        # 应用样式
        self.apply_styles()
        
    def create_title_section(self, layout):
        """创建标题区域"""
        title_frame = QFrame()
        title_frame.setFrameStyle(QFrame.StyledPanel)
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        # 主标题
        main_title = QLabel("📱 InfoGen 多功能信息生成器")
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # 副标题
        subtitle = QLabel("姓名生成 | 手机号生成 | VCF通讯录批量生成")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                font-size: 14px;
                background: transparent;
                margin-top: 5px;
            }
        """)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        layout.addWidget(title_frame)
    

    def create_tab_widget(self, layout):
        """创建标签页界面"""
        self.tab_widget = QTabWidget()
        
        # 获取DPI缩放因子，确保在不同显示环境下的适配
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        dpi_ratio = screen.logicalDotsPerInch() / 96.0  # 96 DPI为标准
        
        # 根据DPI调整尺寸
        base_padding_h = max(10, int(10 * dpi_ratio))
        base_padding_v = max(20, int(20 * dpi_ratio))
        min_tab_width = max(100, int(100 * dpi_ratio))
        max_tab_width = max(180, int(180 * dpi_ratio))
        
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }}

            QTabBar::tab {{
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: {base_padding_h}px {base_padding_v}px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: {min_tab_width}px;
                max-width: {max_tab_width}px;
                text-align: center;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 2px solid white;
                color: #667eea;
            }}
            QTabBar::tab:hover {{
                background-color: #e8e8e8;
            }}
        """)
        
        # 设置标签栏的其他属性以确保显示正常
        self.tab_widget.tabBar().setExpanding(False)  # 禁止标签自动扩展填满空间
        self.tab_widget.tabBar().setUsesScrollButtons(True)  # 启用滚动按钮防止标签过多时溢出
        
        # 创建各个标签页
        self.create_name_tab()
        self.create_phone_tab()
        self.create_vcf_tab()
        self.create_about_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_name_tab(self):
        """创建姓名生成标签页"""
        name_tab = QWidget()
        layout = QVBoxLayout(name_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 控制面板
        self.create_name_control_panel(layout)
        
        # 结果显示区域
        self.create_name_result_section(layout)
        
        self.tab_widget.addTab(name_tab, "👤 姓名生成")
    
    def create_phone_tab(self):
        """创建手机号生成标签页"""
        phone_tab = QWidget()
        layout = QVBoxLayout(phone_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 控制面板
        self.create_phone_control_panel(layout)
        
        # 结果显示区域
        self.create_phone_result_section(layout)
        
        self.tab_widget.addTab(phone_tab, "📱 手机号生成")
    
    def create_vcf_tab(self):
        """创建VCF生成标签页"""
        vcf_tab = QWidget()
        layout = QVBoxLayout(vcf_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 控制面板
        self.create_vcf_control_panel(layout)
        
        # 结果显示区域
        self.create_vcf_result_section(layout)
        
        self.tab_widget.addTab(vcf_tab, "📁 VCF通讯录")

    def create_about_tab(self):
        """创建关于标签页"""
        about_tab = QWidget()
        layout = QVBoxLayout(about_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 创建滚动区域
        from PyQt5.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 主标题和图标
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 图标 (如果存在)
        icon_path = get_resource_path('app_icon.ico')
        if os.path.exists(icon_path):
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(64, 64))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(icon_label)
        
        # 标题文本
        title_text_layout = QVBoxLayout()
        main_title = QLabel("InfoGen v3.0")
        main_title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                margin: 0px;
            }
        """)
        
        subtitle = QLabel("信息生成器")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #666;
                margin: 5px 0px;
            }
        """)
        
        title_text_layout.addWidget(main_title)
        title_text_layout.addWidget(subtitle)
        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()
        
        content_layout.addWidget(title_container)
        
        # 功能介绍
        feature_title = QLabel("🚀 功能特色")
        feature_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin-top: 10px;
                margin-bottom: 10px;
            }
        """)
        content_layout.addWidget(feature_title)
        
        features_text = QLabel("""
• 👤 智能姓名生成：基于真实姓氏库，支持男性/女性/混合模式，可生成1-1000个姓名
• 📱 手机号码生成：支持中国大陆四大运营商，包含62个真实号段，可生成1-10000个号码
• 📁 VCF通讯录生成：批量生成标准VCF格式通讯录文件，支持iPhone/Android/Windows等设备
• 🎯 数据完整性：301个真实姓氏 + 1000+个常用名字 + 62个运营商号段
• 💾 多格式导出：支持TXT、CSV等多种格式导出，方便数据使用
        """)
        features_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555;
                line-height: 1.8;
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                border-left: 4px solid #667eea;
            }
        """)
        features_text.setWordWrap(True)
        content_layout.addWidget(features_text)
        
        # 项目声明
        declaration_title = QLabel("📋 项目声明")
        declaration_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        content_layout.addWidget(declaration_title)
        
        declaration_text = QLabel("""
本工具完全免费开源，不收取任何费用，可安全使用。

• 🔒 隐私安全：所有数据本地生成，不上传任何信息
• 📖 开源透明：代码完全开源，可查看所有实现细节
• ⚖️ 合法使用：仅供学习交流和合法用途，请遵守相关法律法规
• 🚫 禁止滥用：严禁用于诈骗、骚扰等非法活动
        """)
        declaration_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555;
                line-height: 1.8;
                background-color: #fff8e1;
                border-radius: 8px;
                padding: 20px;
                border-left: 4px solid #ffc107;
            }
        """)
        declaration_text.setWordWrap(True)
        content_layout.addWidget(declaration_text)
        
        # 联系信息
        contact_title = QLabel("📞 联系信息")
        contact_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        content_layout.addWidget(contact_title)
        
        # 创建联系信息的垂直布局
        contact_container = QWidget()
        contact_layout = QVBoxLayout(contact_container)
        contact_layout.setSpacing(15)
        contact_layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置容器样式
        contact_container.setStyleSheet("""
            QWidget {
                background-color: #e3f2fd;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
            }
        """)
        
        # 开源地址
        github_label = QLabel('🌟 开源地址：<a href="https://github.com/lemodragon/InfoGen" style="color: #2196f3; text-decoration: none;">https://github.com/lemodragon/InfoGen</a>')
        github_label.setStyleSheet("font-size: 14px; color: #555; background: transparent;")
        github_label.setOpenExternalLinks(True)
        github_label.setTextFormat(Qt.TextFormat.RichText)
        
        # 联系作者
        contact_author_label = QLabel('📧 联系作者：<a href="https://demo.lvdpub.com" style="color: #2196f3; text-decoration: none;">https://demo.lvdpub.com</a>')
        contact_author_label.setStyleSheet("font-size: 14px; color: #555; background: transparent;")
        contact_author_label.setOpenExternalLinks(True)
        contact_author_label.setTextFormat(Qt.TextFormat.RichText)
        
        # 问题反馈
        feedback_label = QLabel("💡 问题反馈：欢迎提交Issue或Pull Request")
        feedback_label.setStyleSheet("font-size: 14px; color: #555; background: transparent;")
        
        # 技术栈
        tech_label = QLabel("🔧 技术栈：Python + PyQt5 + 现代化UI设计")
        tech_label.setStyleSheet("font-size: 14px; color: #555; background: transparent;")
        
        # 添加到布局
        contact_layout.addWidget(github_label)
        contact_layout.addWidget(contact_author_label)
        contact_layout.addWidget(feedback_label)
        contact_layout.addWidget(tech_label)
        
        content_layout.addWidget(contact_container)
        
        # 版权信息
        copyright_text = QLabel("© 2025 InfoGen | 基于 PyQt5 开发 | 完全免费开源")
        copyright_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #adb5bd;
                text-align: center;
                margin-top: 30px;
                padding: 15px;
                border-top: 1px solid #dee2e6;
            }
        """)
        copyright_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(copyright_text)
        
        content_layout.addStretch()
        
        # 设置滚动区域
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(about_tab, "ℹ️ 关于")

    def create_name_control_panel(self, layout):
        """创建控制面板"""
        control_group = QGroupBox("生成设置")
        control_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        control_layout = QGridLayout(control_group)
        control_layout.setSpacing(15)
        
        # 性别选择
        gender_label = QLabel("性别选择:")
        gender_label.setStyleSheet("font-weight: bold; color: #555;")
        
        gender_layout = QHBoxLayout()
        self.boy_checkbox = QCheckBox("男性")
        self.girl_checkbox = QCheckBox("女性")
        self.boy_checkbox.setChecked(True)
        self.girl_checkbox.setChecked(True)
        
        # 样式设置
        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                color: #555;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #bbb;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #667eea;
                border-radius: 3px;
                background-color: #667eea;
            }
        """
        self.boy_checkbox.setStyleSheet(checkbox_style)
        self.girl_checkbox.setStyleSheet(checkbox_style)
        
        gender_layout.addWidget(self.boy_checkbox)
        gender_layout.addWidget(self.girl_checkbox)
        gender_layout.addStretch()
        
        # 生成数量
        count_label = QLabel("生成数量:")
        count_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 1000)
        self.count_spinbox.setValue(20)
        self.count_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #667eea;
            }
        """)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("🎲 生成姓名")
        self.clear_btn = QPushButton("🗑️ 清空结果")
        self.export_btn = QPushButton("💾 导出文件")
        
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                color: white;
            }
        """
        
        self.generate_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4c51bf, stop:1 #553c9a);
            }
        """)
        
        self.clear_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f093fb, stop:1 #f5576c);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e879f9, stop:1 #ef4444);
            }
        """)
        
        self.export_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #06b6d4);
            }
        """)
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        
        # 布局设置
        control_layout.addWidget(gender_label, 0, 0)
        control_layout.addLayout(gender_layout, 0, 1)
        control_layout.addWidget(count_label, 1, 0)
        control_layout.addWidget(self.count_spinbox, 1, 1)
        control_layout.addLayout(button_layout, 2, 0, 1, 2)
        
        # 连接信号
        self.generate_btn.clicked.connect(self.generate_names)
        self.clear_btn.clicked.connect(self.clear_results)
        self.export_btn.clicked.connect(self.export_results)
        
        layout.addWidget(control_group)

    def create_phone_control_panel(self, layout):
        """创建手机号控制面板"""
        control_group = QGroupBox("手机号生成设置")
        control_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        control_layout = QGridLayout(control_group)
        control_layout.setSpacing(15)
        
        # 运营商选择
        carrier_label = QLabel("运营商选择:")
        carrier_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.carrier_combo = QComboBox()
        self.carrier_combo.addItems(["全部", "中国移动", "中国联通", "中国电信", "虚拟运营商"])
        self.carrier_combo.setCurrentText("全部")
        
        # 前缀选择
        prefix_label = QLabel("号段前缀:")
        prefix_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.prefix_combo = QComboBox()
        self.prefix_combo.addItem("随机")
        # 添加所有前缀
        for prefix in self.phone_generator.prefixes:
            self.prefix_combo.addItem(prefix)
        
        combo_style = """
            QComboBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-style: solid;
                border-width: 4px;
                border-color: transparent transparent #555 transparent;
            }
        """
        self.carrier_combo.setStyleSheet(combo_style)
        self.prefix_combo.setStyleSheet(combo_style)
        
        # 生成数量
        phone_count_label = QLabel("生成数量:")
        phone_count_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.phone_count_spinbox = QSpinBox()
        self.phone_count_spinbox.setRange(1, 10000)
        self.phone_count_spinbox.setValue(50)
        self.phone_count_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #667eea;
            }
        """)
        
        # 显示选项
        display_label = QLabel("显示选项:")
        display_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.show_carrier_checkbox = QCheckBox("显示运营商标识")
        self.show_carrier_checkbox.setChecked(True)  # 默认显示
        self.show_carrier_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #555;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #bbb;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #667eea;
                border-radius: 3px;
                background-color: #667eea;
            }
        """)
        
        # 按钮区域
        phone_button_layout = QHBoxLayout()
        
        self.generate_phone_btn = QPushButton("📱 生成手机号")
        self.clear_phone_btn = QPushButton("🗑️ 清空结果")
        self.export_phone_btn = QPushButton("💾 导出文件")
        
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                color: white;
            }
        """
        
        self.generate_phone_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        
        self.clear_phone_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f093fb, stop:1 #f5576c);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e879f9, stop:1 #ef4444);
            }
        """)
        
        self.export_phone_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #06b6d4);
            }
        """)
        
        phone_button_layout.addWidget(self.generate_phone_btn)
        phone_button_layout.addWidget(self.clear_phone_btn)
        phone_button_layout.addWidget(self.export_phone_btn)
        phone_button_layout.addStretch()
        
        # 布局设置
        control_layout.addWidget(carrier_label, 0, 0)
        control_layout.addWidget(self.carrier_combo, 0, 1)
        control_layout.addWidget(prefix_label, 1, 0)
        control_layout.addWidget(self.prefix_combo, 1, 1)
        control_layout.addWidget(phone_count_label, 2, 0)
        control_layout.addWidget(self.phone_count_spinbox, 2, 1)
        control_layout.addWidget(display_label, 3, 0)
        control_layout.addWidget(self.show_carrier_checkbox, 3, 1)
        control_layout.addLayout(phone_button_layout, 4, 0, 1, 2)
        
        # 连接信号
        self.generate_phone_btn.clicked.connect(self.generate_phones)
        self.clear_phone_btn.clicked.connect(self.clear_phone_results)
        self.export_phone_btn.clicked.connect(self.export_phone_results)
        
        layout.addWidget(control_group)

    def create_vcf_control_panel(self, layout):
        """创建VCF控制面板"""
        control_group = QGroupBox("VCF通讯录批量生成设置")
        control_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        control_layout = QGridLayout(control_group)
        control_layout.setSpacing(15)
        
        # VCF文件数量
        file_count_label = QLabel("VCF文件数量:")
        file_count_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.vcf_file_count_spinbox = QSpinBox()
        self.vcf_file_count_spinbox.setRange(1, 100)
        self.vcf_file_count_spinbox.setValue(5)
        
        # 每文件联系人数量
        contacts_per_file_label = QLabel("每文件联系人数:")
        contacts_per_file_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.contacts_per_file_spinbox = QSpinBox()
        self.contacts_per_file_spinbox.setRange(1, 10000)
        self.contacts_per_file_spinbox.setValue(1000)
        
        # 文件名前缀
        filename_prefix_label = QLabel("文件名前缀:")
        filename_prefix_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.filename_prefix_edit = QLineEdit("通讯录")
        
        # 命名模式选择
        naming_mode_label = QLabel("文件命名模式:")
        naming_mode_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.naming_mode_combo = QComboBox()
        self.naming_mode_combo.addItems(["时间戳模式", "自定义序号"])
        self.naming_mode_combo.setCurrentIndex(0)  # 默认时间戳模式
        
        # 起始数字（仅在自定义序号模式下显示）
        self.start_number_label = QLabel("起始数字:")
        self.start_number_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.start_number_spinbox = QSpinBox()
        self.start_number_spinbox.setRange(1, 99999)
        self.start_number_spinbox.setValue(1)
        
        # 数字格式选择（仅在自定义序号模式下显示）
        self.number_format_label = QLabel("数字格式:")
        self.number_format_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.number_format_combo = QComboBox()
        self.number_format_combo.addItems(["固定3位数 (001,002...)", "自动位数 (1,2,3...)"])
        self.number_format_combo.setCurrentIndex(0)  # 默认固定3位数
        
        # 默认隐藏自定义序号相关控件
        self.start_number_label.setVisible(False)
        self.start_number_spinbox.setVisible(False)
        self.number_format_label.setVisible(False)
        self.number_format_combo.setVisible(False)
        
        # 联系人性别选择
        vcf_gender_label = QLabel("联系人性别:")
        vcf_gender_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.vcf_gender_combo = QComboBox()
        self.vcf_gender_combo.addItems(["混合", "男性", "女性"])
        
        # 手机号运营商
        vcf_carrier_label = QLabel("手机号运营商:")
        vcf_carrier_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.vcf_carrier_combo = QComboBox()
        self.vcf_carrier_combo.addItems(["全部", "中国移动", "中国联通", "中国电信", "虚拟运营商"])
        
        # 样式设置
        spinbox_style = """
            QSpinBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #667eea;
            }
        """
        
        lineedit_style = """
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """
        
        combo_style = """
            QComboBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-style: solid;
                border-width: 4px;
                border-color: transparent transparent #555 transparent;
            }
        """
        
        self.vcf_file_count_spinbox.setStyleSheet(spinbox_style)
        self.contacts_per_file_spinbox.setStyleSheet(spinbox_style)
        self.filename_prefix_edit.setStyleSheet(lineedit_style)
        self.vcf_gender_combo.setStyleSheet(combo_style)
        self.vcf_carrier_combo.setStyleSheet(combo_style)
        self.naming_mode_combo.setStyleSheet(combo_style)
        self.start_number_spinbox.setStyleSheet(spinbox_style)
        self.number_format_combo.setStyleSheet(combo_style)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 3px;
            }
        """)
        
        # 按钮区域
        vcf_button_layout = QHBoxLayout()
        
        self.generate_vcf_btn = QPushButton("📁 批量生成VCF")
        self.preview_vcf_btn = QPushButton("👁️ 预览内容")
        
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                color: white;
            }
        """
        
        self.generate_vcf_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        
        self.preview_vcf_btn.setStyleSheet(button_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #06b6d4);
            }
        """)
        
        vcf_button_layout.addWidget(self.generate_vcf_btn)
        vcf_button_layout.addWidget(self.preview_vcf_btn)
        vcf_button_layout.addStretch()
        
        # 布局设置
        control_layout.addWidget(file_count_label, 0, 0)
        control_layout.addWidget(self.vcf_file_count_spinbox, 0, 1)
        control_layout.addWidget(contacts_per_file_label, 1, 0)
        control_layout.addWidget(self.contacts_per_file_spinbox, 1, 1)
        control_layout.addWidget(filename_prefix_label, 2, 0)
        control_layout.addWidget(self.filename_prefix_edit, 2, 1)
        control_layout.addWidget(naming_mode_label, 3, 0)
        control_layout.addWidget(self.naming_mode_combo, 3, 1)
        control_layout.addWidget(self.start_number_label, 4, 0)
        control_layout.addWidget(self.start_number_spinbox, 4, 1)
        control_layout.addWidget(self.number_format_label, 5, 0)
        control_layout.addWidget(self.number_format_combo, 5, 1)
        control_layout.addWidget(vcf_gender_label, 6, 0)
        control_layout.addWidget(self.vcf_gender_combo, 6, 1)
        control_layout.addWidget(vcf_carrier_label, 7, 0)
        control_layout.addWidget(self.vcf_carrier_combo, 7, 1)
        control_layout.addWidget(self.progress_bar, 8, 0, 1, 2)
        control_layout.addLayout(vcf_button_layout, 9, 0, 1, 2)
        
        # 连接信号
        self.generate_vcf_btn.clicked.connect(self.generate_vcf_files)
        self.preview_vcf_btn.clicked.connect(self.preview_vcf_content)
        self.naming_mode_combo.currentTextChanged.connect(self.on_naming_mode_changed)
        
        layout.addWidget(control_group)

    def create_name_result_section(self, layout):
        """创建姓名结果显示区域"""
        result_group = QGroupBox("生成结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        result_layout = QVBoxLayout(result_group)
        
        # 结果显示文本框
        self.name_result_text = QTextEdit()
        self.name_result_text.setPlaceholderText("点击'生成姓名'按钮开始生成...")
        self.name_result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                background-color: #f8fafc;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        
        # 统计信息标签
        self.name_stats_label = QLabel("准备就绪")
        self.name_stats_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                padding: 5px;
            }
        """)
        
        result_layout.addWidget(self.name_result_text)
        result_layout.addWidget(self.name_stats_label)
        
        layout.addWidget(result_group)

    def create_phone_result_section(self, layout):
        """创建手机号结果显示区域"""
        result_group = QGroupBox("生成结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        result_layout = QVBoxLayout(result_group)
        
        # 结果显示文本框
        self.phone_result_text = QTextEdit()
        self.phone_result_text.setPlaceholderText("点击'生成手机号'按钮开始生成...")
        self.phone_result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Microsoft YaHei', monospace;
                font-size: 14px;
                line-height: 1.5;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                background-color: #f8fafc;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        
        # 统计信息标签
        self.phone_stats_label = QLabel("准备就绪")
        self.phone_stats_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                padding: 5px;
            }
        """)
        
        result_layout.addWidget(self.phone_result_text)
        result_layout.addWidget(self.phone_stats_label)
        
        layout.addWidget(result_group)

    def create_vcf_result_section(self, layout):
        """创建VCF结果显示区域"""
        result_group = QGroupBox("生成结果与预览")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        result_layout = QVBoxLayout(result_group)
        
        # 结果显示文本框
        self.vcf_result_text = QTextEdit()
        self.vcf_result_text.setPlaceholderText("点击'预览内容'查看VCF格式，或点击'批量生成VCF'开始生成文件...")
        self.vcf_result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Microsoft YaHei', monospace;
                font-size: 12px;
                line-height: 1.4;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                background-color: #f8fafc;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        
        # 统计信息标签
        self.vcf_stats_label = QLabel("准备就绪")
        self.vcf_stats_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                padding: 5px;
            }
        """)
        
        result_layout.addWidget(self.vcf_result_text)
        result_layout.addWidget(self.vcf_stats_label)
        
        layout.addWidget(result_group)
        
    def create_result_section(self, layout):
        """创建结果显示区域"""
        result_group = QGroupBox("生成结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        result_layout = QVBoxLayout(result_group)
        
        # 结果显示文本框
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("点击'生成姓名'按钮开始生成...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                background-color: #f8fafc;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        
        # 统计信息标签
        self.stats_label = QLabel("准备就绪")
        self.stats_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                padding: 5px;
            }
        """)
        
        result_layout.addWidget(self.result_text)
        result_layout.addWidget(self.stats_label)
        
        layout.addWidget(result_group)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        
        # 设置状态栏样式
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f1f5f9;
                border: none;
                padding: 2px 8px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # 创建版权信息标签
        copyright_label = QLabel("© 2025 InfoGen | 基于 PyQt5 开发 | 完全免费开源")
        copyright_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                margin-right: 20px;
            }
        """)
        
        # 添加数据库统计信息
        name_stats = self.name_generator.get_statistics()
        phone_stats = self.phone_generator.get_statistics()
        stats_text = f"📊 姓名库：{name_stats['姓氏数量']}个姓氏，{name_stats['男性双字名']+name_stats['男性单字名']}个男性名，{name_stats['女性双字名']+name_stats['女性单字名']}个女性名 | 号段库：{phone_stats['总号段数']}个号段"
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 11px;
                font-weight: 400;
                padding: 4px 8px;
            }
        """)
        
        # 添加到状态栏
        self.status_bar.addWidget(copyright_label)
        self.status_bar.addPermanentWidget(stats_label)
        
        # 保存版权标签引用，用于临时消息显示
        self.copyright_label = copyright_label
        
        self.setStatusBar(self.status_bar)
    
    def show_temp_message(self, message, duration=3000):
        """显示临时消息"""
        original_text = self.copyright_label.text()
        self.copyright_label.setText(message)
        self.copyright_label.setStyleSheet("""
            QLabel {
                color: #059669;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                margin-right: 20px;
            }
        """)
        
        # 设置定时器恢复原始文本和样式
        QTimer.singleShot(duration, lambda: self.restore_copyright_label(original_text))
    
    def restore_copyright_label(self, original_text):
        """恢复版权标签的原始样式"""
        self.copyright_label.setText(original_text)
        self.copyright_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                margin-right: 20px;
            }
        """)
        
    def apply_styles(self):
        """应用全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f1f5f9;
            }
            QWidget {
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
        """)
        
    def generate_names(self):
        """生成姓名"""
        # 检查性别选择
        if not self.boy_checkbox.isChecked() and not self.girl_checkbox.isChecked():
            QMessageBox.warning(self, "警告", "请至少选择一种性别！")
            return
            
        # 确定性别参数
        if self.boy_checkbox.isChecked() and self.girl_checkbox.isChecked():
            gender = "all"
        elif self.boy_checkbox.isChecked():
            gender = "boy"
        else:
            gender = "girl"
            
        count = self.count_spinbox.value()
        
        # 禁用生成按钮，防止重复点击
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("⏳ 生成中...")
        self.show_temp_message("正在生成姓名...")
        
        # 创建并启动工作线程
        self.name_worker_thread = NameGeneratorThread(self.name_generator, count, gender)
        self.name_worker_thread.finished.connect(self.on_names_generated)
        self.name_worker_thread.error.connect(self.on_generation_error)
        self.name_worker_thread.start()
        
    def on_names_generated(self, names):
        """姓名生成完成回调"""
        self.generated_names = names
        
        # 显示结果
        result_text = "\n".join(names)
        self.name_result_text.setText(result_text)
        
        # 更新统计信息
        boy_count = sum(1 for name in names if self.is_likely_boy_name(name))
        girl_count = len(names) - boy_count
        
        stats_text = f"已生成 {len(names)} 个姓名 | 男性: {boy_count} 个 | 女性: {girl_count} 个"
        self.name_stats_label.setText(stats_text)
        
        # 恢复生成按钮
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🎲 生成姓名")
        self.show_temp_message(f"✅ 成功生成 {len(names)} 个姓名")
        
    def on_generation_error(self, error_msg):
        """生成错误回调"""
        QMessageBox.critical(self, "错误", f"生成姓名时发生错误：\n{error_msg}")
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🎲 生成姓名")
        self.show_temp_message("❌ 生成失败")
        
    def is_likely_boy_name(self, name):
        """简单判断是否为男性姓名（基于名字部分）"""
        if len(name) <= 1:
            return True
            
        name_part = name[1:]  # 去掉姓氏
        
        # 检查是否在男性名字数据中
        for boy_name in self.name_generator.boy2 + self.name_generator.boy1:
            if name_part == boy_name:
                return True
        return False
        
    def clear_results(self):
        """清空姓名结果"""
        self.name_result_text.clear()
        self.generated_names = []
        self.name_stats_label.setText("准备就绪")
        self.show_temp_message("🗑️ 已清空姓名结果", 2000)
        
    def export_results(self):
        """导出结果到文件"""
        if not self.generated_names:
            QMessageBox.information(self, "提示", "没有可导出的姓名，请先生成姓名！")
            return
            
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存姓名列表", "姓名列表.txt", "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("InfoGen-信息生成器 - 生成结果\n")
                    f.write("=" * 30 + "\n\n")
                    for i, name in enumerate(self.generated_names, 1):
                        f.write(f"{i:3d}. {name}\n")
                    f.write(f"\n总计: {len(self.generated_names)} 个姓名")
                    
                QMessageBox.information(self, "导出成功", f"姓名列表已保存到：\n{file_path}")
                self.show_temp_message("💾 导出成功")
                
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"保存文件时发生错误：\n{str(e)}")
                self.show_temp_message("❌ 导出失败")

    # 手机号相关方法
    def generate_phones(self):
        """生成手机号"""
        count = self.phone_count_spinbox.value()
        carrier_text = self.carrier_combo.currentText()
        prefix_text = self.prefix_combo.currentText()
        
        # 映射运营商选择
        carrier_map = {
            "全部": None,
            "中国移动": "mobile",
            "中国联通": "unicom", 
            "中国电信": "telecom",
            "虚拟运营商": "virtual"
        }
        carrier = carrier_map.get(carrier_text)
        
        # 禁用生成按钮
        self.generate_phone_btn.setEnabled(False)
        self.generate_phone_btn.setText("⏳ 生成中...")
        self.show_temp_message("正在生成手机号...")
        
        # 创建并启动工作线程
        self.phone_worker_thread = PhoneGeneratorThread(
            self.phone_generator, count, carrier, prefix_text
        )
        self.phone_worker_thread.finished.connect(self.on_phones_generated)
        self.phone_worker_thread.error.connect(self.on_phone_generation_error)
        self.phone_worker_thread.start()
    
    def on_phones_generated(self, phones):
        """手机号生成完成回调"""
        self.generated_phones = phones
        
        # 格式化显示结果
        formatted_phones = []
        carrier_stats = {}
        
        for phone in phones:
            # 格式化为 xxx xxxx xxxx
            formatted = f"{phone[:3]} {phone[3:7]} {phone[7:]}"
            carrier = self.phone_generator.get_carrier_name(phone)
            
            # 根据复选框状态决定是否显示运营商标识
            if self.show_carrier_checkbox.isChecked():
                formatted_phones.append(f"{formatted} ({carrier})")
            else:
                formatted_phones.append(formatted)
                
            carrier_stats[carrier] = carrier_stats.get(carrier, 0) + 1
        
        # 显示结果
        result_text = "\n".join(formatted_phones)
        self.phone_result_text.setText(result_text)
        
        # 统计信息
        stats_parts = [f"已生成 {len(phones)} 个手机号"]
        for carrier, count in carrier_stats.items():
            stats_parts.append(f"{carrier}: {count}个")
        
        stats_text = " | ".join(stats_parts)
        self.phone_stats_label.setText(stats_text)
        
        # 恢复生成按钮
        self.generate_phone_btn.setEnabled(True)
        self.generate_phone_btn.setText("📱 生成手机号")
        self.show_temp_message(f"✅ 成功生成 {len(phones)} 个手机号")
    
    def on_phone_generation_error(self, error_msg):
        """手机号生成错误回调"""
        QMessageBox.critical(self, "错误", f"生成手机号时发生错误：\n{error_msg}")
        self.generate_phone_btn.setEnabled(True)
        self.generate_phone_btn.setText("📱 生成手机号")
        self.show_temp_message("❌ 生成失败")
    
    def clear_phone_results(self):
        """清空手机号结果"""
        self.phone_result_text.clear()
        self.generated_phones = []
        self.phone_stats_label.setText("准备就绪")
        self.show_temp_message("🗑️ 已清空手机号结果", 2000)
    
    def export_phone_results(self):
        """导出手机号结果"""
        if not self.generated_phones:
            QMessageBox.information(self, "提示", "没有可导出的手机号，请先生成手机号！")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存手机号列表", "手机号列表.txt", "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("手机号生成器 - 生成结果\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for phone in self.generated_phones:
                        formatted = f"{phone[:3]} {phone[3:7]} {phone[7:]}"
                        carrier = self.phone_generator.get_carrier_name(phone)
                        # 根据复选框状态决定是否包含运营商标识
                        if self.show_carrier_checkbox.isChecked():
                            f.write(f"{formatted} ({carrier})\n")
                        else:
                            f.write(f"{formatted}\n")
                    
                    f.write(f"\n总计: {len(self.generated_phones)} 个手机号")
                
                QMessageBox.information(self, "成功", f"文件已保存至：{file_path}")
                self.show_temp_message("💾 手机号导出成功")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件时发生错误：\n{str(e)}")

    # VCF相关方法
    def on_naming_mode_changed(self, mode_text):
        """命名模式改变时的处理"""
        is_custom_mode = (mode_text == "自定义序号")
        
        # 显示/隐藏自定义序号相关控件
        self.start_number_label.setVisible(is_custom_mode)
        self.start_number_spinbox.setVisible(is_custom_mode)
        self.number_format_label.setVisible(is_custom_mode)
        self.number_format_combo.setVisible(is_custom_mode)
        
        # 更新界面提示
        if is_custom_mode:
            self.show_temp_message("🔢 已切换到自定义序号模式", 2000)
        else:
            self.show_temp_message("🕐 已切换到时间戳模式", 2000)
    
    def generate_vcf_files(self):
        """生成VCF文件"""
        file_count = self.vcf_file_count_spinbox.value()
        contacts_per_file = self.contacts_per_file_spinbox.value()
        filename_prefix = self.filename_prefix_edit.text().strip() or "通讯录"
        
        gender_text = self.vcf_gender_combo.currentText()
        carrier_text = self.vcf_carrier_combo.currentText()
        
        # 映射性别选择
        gender_map = {"混合": "all", "男性": "boy", "女性": "girl"}
        gender = gender_map.get(gender_text, "all")
        
        # 映射运营商选择
        carrier_map = {
            "全部": None,
            "中国移动": "mobile", 
            "中国联通": "unicom",
            "中国电信": "telecom",
            "虚拟运营商": "virtual"
        }
        carrier = carrier_map.get(carrier_text)
        
        # 获取命名模式相关参数
        naming_mode_text = self.naming_mode_combo.currentText()
        naming_mode = "custom_number" if naming_mode_text == "自定义序号" else "timestamp"
        start_number = self.start_number_spinbox.value()
        
        # 获取数字格式
        format_text = self.number_format_combo.currentText()
        number_format = "{:03d}" if "固定3位数" in format_text else "{:d}"
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择VCF文件保存目录")
        if not output_dir:
            return
        
        # 显示进度条并禁用按钮
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_vcf_btn.setEnabled(False)
        self.generate_vcf_btn.setText("⏳ 生成中...")
        self.show_temp_message("正在批量生成VCF文件...")
        
        # 创建并启动工作线程
        self.vcf_worker_thread = VCFGeneratorThread(
            self.vcf_generator, file_count, contacts_per_file,
            output_dir, filename_prefix, gender, carrier,
            naming_mode, start_number, number_format
        )
        self.vcf_worker_thread.finished.connect(self.on_vcf_generated)
        self.vcf_worker_thread.progress.connect(self.on_vcf_progress)
        self.vcf_worker_thread.error.connect(self.on_vcf_generation_error)
        self.vcf_worker_thread.start()
    
    def on_vcf_generated(self, result):
        """VCF生成完成回调"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 显示结果
        if result["success"]:
            result_text = f"""✅ VCF文件批量生成完成！

📊 生成统计：
• 成功创建文件：{result['files_created']} 个
• 总联系人数：{result['total_contacts']} 个
• 输出目录：{result['output_directory']}

📁 生成的文件：
"""
            for file_path in result["created_files"]:
                file_name = file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
                result_text += f"• {file_name}\n"
                
        else:
            result_text = f"❌ 生成失败：{result.get('error', '未知错误')}"
        
        self.vcf_result_text.setText(result_text)
        
        # 更新统计
        if result["success"]:
            stats_text = f"成功生成 {result['files_created']} 个VCF文件，共 {result['total_contacts']} 个联系人"
            self.vcf_stats_label.setText(stats_text)
            self.show_temp_message("✅ VCF文件生成完成")
            QMessageBox.information(self, "成功", f"已成功生成 {result['files_created']} 个VCF文件！")
        else:
            self.vcf_stats_label.setText("生成失败")
            self.show_temp_message("❌ VCF文件生成失败")
        
        # 恢复按钮
        self.generate_vcf_btn.setEnabled(True)
        self.generate_vcf_btn.setText("📁 批量生成VCF")
    
    def on_vcf_progress(self, progress):
        """VCF生成进度回调"""
        self.progress_bar.setValue(progress)
    
    def on_vcf_generation_error(self, error_msg):
        """VCF生成错误回调"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", f"生成VCF文件时发生错误：\n{error_msg}")
        
        self.generate_vcf_btn.setEnabled(True)
        self.generate_vcf_btn.setText("📁 批量生成VCF")
        self.show_temp_message("❌ 生成失败")
    
    def preview_vcf_content(self):
        """预览VCF内容"""
        gender_text = self.vcf_gender_combo.currentText()
        carrier_text = self.vcf_carrier_combo.currentText()
        
        # 映射选择
        gender_map = {"混合": "all", "男性": "boy", "女性": "girl"}
        gender = gender_map.get(gender_text, "all")
        
        carrier_map = {
            "全部": None,
            "中国移动": "mobile",
            "中国联通": "unicom", 
            "中国电信": "telecom",
            "虚拟运营商": "virtual"
        }
        carrier = carrier_map.get(carrier_text)
        
        # 生成预览内容
        try:
            preview_content = self.vcf_generator.preview_vcf_content(
                count=3, gender=gender, carrier=carrier
            )
            
            # 添加说明文字
            header = """📋 VCF格式预览（示例联系人）
================================================================

"""
            footer = f"""
================================================================
💡 说明：以上为VCF标准格式示例
📱 实际生成时会根据您的设置批量创建
🎯 当前设置：{gender_text}性别，{carrier_text}运营商"""
            
            full_content = header + preview_content + footer
            self.vcf_result_text.setText(full_content)
            
            self.vcf_stats_label.setText("VCF格式预览已生成")
            self.show_temp_message("📋 VCF预览完成", 2000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成VCF预览时发生错误：\n{str(e)}")

    def restore_window_state(self):
        """恢复窗口状态"""
        try:
            # 恢复窗口几何（位置和大小）
            geometry = self.settings.value("geometry")
            if geometry:
                success = self.restoreGeometry(geometry)
                if success:
                    print("成功恢复窗口尺寸和位置")
                else:
                    print("窗口几何数据无效，使用默认设置")
                    # 如果恢复失败，设置默认几何
                    self.setGeometry(100, 100, 1200, 850)
            
            # 恢复窗口状态（最大化、最小化等）
            window_state = self.settings.value("windowState")
            if window_state:
                success = self.restoreState(window_state)
                if success:
                    print("成功恢复窗口状态")
                else:
                    print("窗口状态数据无效")
        except Exception as e:
            print(f"恢复窗口状态失败: {e}")
            # 发生异常时确保有默认窗口大小
            self.setGeometry(100, 100, 1200, 850)
    
    def save_window_state(self):
        """保存窗口状态"""
        try:
            # 保存窗口几何（位置和大小）
            geometry = self.saveGeometry()
            self.settings.setValue("geometry", geometry)
            
            # 保存窗口状态（最大化、最小化等）
            window_state = self.saveState()
            self.settings.setValue("windowState", window_state)
            
            # 强制同步设置到磁盘
            self.settings.sync()
            print("窗口状态已保存")
            
        except Exception as e:
            print(f"保存窗口状态失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.save_window_state()
        event.accept()


def main():
    """主程序入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("InfoGen-信息生成器")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("Name Generator Studio")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main()) 