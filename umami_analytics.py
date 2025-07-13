#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Umami Analytics for Desktop Applications
桌面应用Umami统计模块 - 完整功能实现
"""

import sys
import os
import platform
import hashlib
import time
import threading
import tempfile
import shutil
import json
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("警告: requests库未安装，统计功能将被禁用")

try:
    import geoip2.database
    import geoip2.errors
    HAS_GEOIP = True
except ImportError:
    HAS_GEOIP = False
    print("提示: geoip2库未安装，地理位置功能将被禁用")


class UmamiAnalytics:
    """桌面应用Umami统计分析类"""
    
    def __init__(self, umami_url="https://umami.lvdpub.com/script.js", 
                 website_id="9ecc9e6b-a8c1-4501-9561-20617798f753"):
        """
        初始化Umami统计模块
        
        Args:
            umami_url (str): Umami服务器地址
            website_id (str): 网站ID
        """
        self.umami_url = umami_url
        self.website_id = website_id
        self.enabled = HAS_REQUESTS
        
        if not self.enabled:
            print("统计功能已禁用: 缺少必要依赖")
            return
            
        # API端点配置
        base_url = umami_url.replace('/script.js', '')
        self.possible_endpoints = [
            f"{base_url}/api/send",
            f"{base_url}/api/collect", 
            f"{base_url}/api/track"
        ]
        self.current_endpoint = self.possible_endpoints[0]
        
        # 会话管理
        self.session_id = self._generate_session_id()
        self.user_id = self._generate_user_id()
        self.start_time = time.time()
        self.last_activity = time.time()
        
        # 心跳机制
        self.heartbeat_interval = 30  # 30秒心跳
        self.heartbeat_timer = None
        self.is_active = True
        
        # 系统信息
        self.user_agent = self._get_user_agent()
        self.screen_resolution = self._get_screen_resolution()
        self.location_info = self._get_location_info()
        
        # 检测可用端点
        self._detect_working_endpoint()
        
        print(f"Umami统计模块已初始化 - 会话ID: {self.session_id[:8]}...")
    
    def _generate_session_id(self):
        """生成会话ID（每小时更新）"""
        machine_id = f"{platform.node()}-{platform.system()}"
        current_hour = int(time.time() / 3600)
        session_string = f"{machine_id}-{current_hour}"
        return hashlib.md5(session_string.encode()).hexdigest()
    
    def _generate_user_id(self):
        """生成用户ID（基于机器标识）"""
        machine_id = f"{platform.node()}-{platform.system()}"
        return hashlib.md5(machine_id.encode()).hexdigest()[:16]
    
    def _get_user_agent(self):
        """获取用户代理字符串"""
        system = platform.system()
        if system == "Windows":
            version = platform.version()
            return f"Mozilla/5.0 (Windows NT {version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        elif system == "Darwin":
            version = platform.mac_ver()[0]
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {version.replace('.', '_')}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        else:
            return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def _get_screen_resolution(self):
        """获取屏幕分辨率"""
        try:
            from PyQt5.QtWidgets import QApplication
            if QApplication.instance():
                screen = QApplication.primaryScreen()
                size = screen.size()
                return f"{size.width()}x{size.height()}"
        except:
            pass
        return "1920x1080"  # 默认分辨率
    
    def _get_location_info(self):
        """获取地理位置信息"""
        if not HAS_GEOIP:
            return {"country": "未知", "region": "未知", "city": "未知"}
        
        try:
            # 获取外网IP
            ip = self._get_external_ip()
            if ip:
                return self._get_ip_location(ip)
        except Exception as e:
            print(f"获取地理位置失败: {e}")
        
        return {"country": "未知", "region": "未知", "city": "未知"}
    
    def _get_external_ip(self):
        """获取外网IP地址"""
        try:
            response = requests.get('https://api.ipify.org', timeout=3)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        return None
    
    def _get_ip_location(self, ip):
        """根据IP获取地理位置"""
        try:
            # 查找GeoIP数据库文件
            db_paths = [
                '/usr/share/GeoIP/GeoLite2-City.mmdb',
                '/opt/GeoIP/GeoLite2-City.mmdb',
                './GeoLite2-City.mmdb'
            ]
            
            db_path = None
            for path in db_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            if not db_path:
                return {"country": "未知", "region": "未知", "city": "未知"}
            
            # Windows中文路径处理
            if sys.platform == 'win32':
                temp_fd, temp_path = tempfile.mkstemp(suffix='.mmdb', prefix='geoip_')
                os.close(temp_fd)
                shutil.copy2(db_path, temp_path)
                db_path = temp_path
            
            with geoip2.database.Reader(db_path) as reader:
                response = reader.city(ip)
                result = {
                    "country": response.country.names.get('zh-CN', response.country.name or '未知'),
                    "region": response.subdivisions.most_specific.names.get('zh-CN', response.subdivisions.most_specific.name or '未知'),
                    "city": response.city.names.get('zh-CN', response.city.name or '未知')
                }
                
                # 清理临时文件
                if sys.platform == 'win32' and 'temp_path' in locals():
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                
                return result
                
        except Exception as e:
            print(f"IP地理位置查询失败: {e}")
            return {"country": "未知", "region": "未知", "city": "未知"}
    
    def _detect_working_endpoint(self):
        """检测可用的API端点"""
        if not self.enabled:
            return
            
        for endpoint in self.possible_endpoints:
            try:
                response = requests.options(endpoint, timeout=3)
                if response.status_code in [200, 405]:
                    self.current_endpoint = endpoint
                    print(f"使用API端点: {endpoint}")
                    return
            except:
                continue
        
        print(f"使用默认端点: {self.current_endpoint}")
    
    def _send_event(self, event_type, event_name, event_data=None):
        """
        发送统计事件
        
        Args:
            event_type (str): 事件类型 - "pageview" 或 "event"
            event_name (str): 事件名称
            event_data (dict): 事件数据
        """
        if not self.enabled:
            return
            
        def send_request():
            try:
                if event_type == "pageview":
                    payload = {
                        "type": "event",  # 修正：所有事件都使用"event"类型
                        "payload": {
                            "website": self.website_id,
                            "hostname": "infogen.desktop",
                            "url": f"/app/{event_name}",
                            "title": f"InfoGen - {event_name}",
                            "referrer": "",
                            "screen": self.screen_resolution
                        }
                    }
                    # 添加自定义数据
                    if event_data:
                        payload["payload"]["data"] = {
                            "session_id": self.session_id,
                            "user_id": self.user_id,
                            "platform": platform.system(),
                            "version": "3.0",
                            "location": self.location_info,
                            **event_data
                        }
                else:
                    payload = {
                        "type": "event",  # 保持event类型
                        "payload": {
                            "website": self.website_id,
                            "hostname": "infogen.desktop",
                            "name": event_name
                        }
                    }
                    # 添加自定义数据
                    if event_data:
                        payload["payload"]["data"] = {
                            "session_id": self.session_id,
                            "user_id": self.user_id,
                            "platform": platform.system(),
                            "version": "3.0",
                            "location": self.location_info,
                            **event_data
                        }
                
                headers = {
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/json",
                    "Origin": "https://infogen.desktop"
                }
                
                # 发送请求
                response = requests.post(
                    self.current_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"统计事件发送成功: {event_name}")
                else:
                    print(f"统计事件发送失败: {event_name} - 状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"统计事件发送异常: {event_name} - {e}")
        
        # 异步发送，避免阻塞主线程
        thread = threading.Thread(target=send_request)
        thread.daemon = True
        thread.start()
    
    def _start_heartbeat(self):
        """启动心跳监控（已禁用）"""
        # 不再启动心跳监控，避免产生无用的统计数据
        pass
    
    def _stop_heartbeat(self):
        """停止心跳监控"""
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.is_active = False
    
    def track_app_start(self):
        """追踪应用启动"""
        self._send_event("pageview", "应用启动", {
            "start_time": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform_info": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        })
        
        # 同时发送一个event类型的事件用于测试
        self._send_event("event", "启动测试", {
            "test_type": "app_start_event",
            "start_time": datetime.now().isoformat()
        })
        
        # 启动心跳监控（已禁用）
        self._start_heartbeat()
    
    def track_app_close(self):
        """追踪应用关闭"""
        session_duration = int(time.time() - self.start_time)
        
        self._send_event("event", "应用关闭", {
            "session_duration": session_duration,
            "close_time": datetime.now().isoformat()
        })
        
        # 停止心跳监控
        self._stop_heartbeat()
    
    def track_about_page_view(self):
        """追踪关于页面访问"""
        self.last_activity = time.time()
        self._send_event("pageview", "关于", {
            "view_time": datetime.now().isoformat()
        })
    
    def track_tutorial_page_view(self):
        """追踪教程页面访问"""
        self.last_activity = time.time()
        self._send_event("pageview", "教程", {
            "view_time": datetime.now().isoformat()
        })
    
    def track_external_link_click(self, url, link_text=""):
        """追踪外部链接点击"""
        self.last_activity = time.time()
        self._send_event("event", link_text, {
            "url": url,
            "link_text": link_text,
            "click_time": datetime.now().isoformat()
        })
    
    def track_feature_usage(self, feature_name, feature_data=None):
        """追踪功能使用"""
        self.last_activity = time.time()
        self._send_event("event", f"feature_{feature_name}", {
            "feature": feature_name,
            "usage_time": datetime.now().isoformat(),
            **(feature_data or {})
        })
    
    def track_tab_switch(self, tab_name):
        """追踪标签页切换"""
        self.last_activity = time.time()
        self._send_event("pageview", f"tab_{tab_name}", {
            "tab": tab_name,
            "switch_time": datetime.now().isoformat()
        })
    
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = time.time() 