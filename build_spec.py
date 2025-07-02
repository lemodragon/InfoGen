#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoGen打包脚本
使用PyInstaller将应用程序打包为独立的可执行文件
"""

import sys
import os
import PyInstaller.__main__
import argparse

def create_spec_content():
    """创建.spec文件内容"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
sys.setrecursionlimit(5000)

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('app_icon.ico', '.')],  # 包含图标文件
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'name_generator',
        'vcf_generator',
        'main_window'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='InfoGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon='app_icon.ico',
    version_file=None,
)
'''
    return spec_content

def build_executable(spec_only=False):
    """构建可执行文件"""
    
    print("=" * 50)
    print("   InfoGen v3.0 打包工具")  
    print("=" * 50)
    
    # 检查必要文件
    required_files = ['app.py', 'main_window.py', 'name_generator.py', 'vcf_generator.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ 错误：缺少必要文件：")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # 创建spec文件
    spec_filename = 'infogen.spec'
    print(f"📄 创建spec文件：{spec_filename}")
    
    try:
        with open(spec_filename, 'w', encoding='utf-8') as f:
            f.write(create_spec_content())
        print("✅ spec文件创建成功")
    except Exception as e:
        print(f"❌ spec文件创建失败：{e}")
        return False
    
    if spec_only:
        print("🎯 仅生成spec文件模式，跳过打包")
        return True
    
    # 执行打包
    print("🔨 开始打包...")
    print("⏳ 这可能需要几分钟时间，请耐心等待...")
    
    try:
        PyInstaller.__main__.run([
            '--clean',
            '--noconfirm', 
            spec_filename
        ])
        
        # 检查是否成功生成
        exe_path = os.path.join('dist', 'InfoGen.exe')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"✅ 打包成功！")
            print(f"📍 文件位置：{exe_path}")
            print(f"📏 文件大小：{file_size:.1f} MB")
            
            # 显示使用说明
            print("\n" + "=" * 50)
            print("📋 使用说明：")
            print("1. 可执行文件已生成在 dist 目录下")
            print("2. InfoGen.exe 可以独立运行，无需Python环境")
            print("3. 首次运行可能需要较长时间加载")
            print("4. 建议将exe文件复制到独立目录使用")
            print("=" * 50)
            return True
        else:
            print("❌ 打包失败：未找到生成的exe文件")
            return False
            
    except Exception as e:
        print(f"❌ 打包过程中出现错误：{e}")
        return False
    
    finally:
        # 清理临时文件
        try:
            if os.path.exists('build'):
                import shutil
                shutil.rmtree('build')
                print("🧹 已清理临时文件")
        except:
            pass

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='InfoGen打包工具')
    parser.add_argument('--spec-only', action='store_true', 
                       help='仅生成spec文件，不执行打包')
    
    args = parser.parse_args()
    
    success = build_executable(spec_only=args.spec_only)
    
    if success:
        print("\n🎉 操作完成！")
    else:
        print("\n💥 操作失败！")
        sys.exit(1)

if __name__ == '__main__':
    main() 