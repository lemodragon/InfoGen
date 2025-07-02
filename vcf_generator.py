#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VCF通讯录生成器 - 标准VCF格式文件生成
支持批量生成多个VCF文件，每个文件包含指定数量的联系人
"""

import os
import random
from datetime import datetime
from name_generator import NameGenerator, PhoneGenerator


class VCFGenerator:
    """VCF通讯录文件生成器类"""
    
    def __init__(self):
        """初始化生成器"""
        self.name_generator = NameGenerator()
        self.phone_generator = PhoneGenerator()
    
    def create_contact_vcf_entry(self, name, phone):
        """
        创建单个联系人的VCF条目
        
        Args:
            name (str): 联系人姓名
            phone (str): 联系人电话
            
        Returns:
            str: VCF格式的联系人条目
        """
        # 格式化电话号码为 xxx xxxx xxxx 格式
        formatted_phone = f"{phone[:3]} {phone[3:7]} {phone[7:]}" if len(phone) == 11 else phone
        
        vcf_entry = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
N:{name[0]};{name[1:]};;;
TEL;CELL:{phone}
TEL;CELL;TYPE=VOICE:{formatted_phone}
END:VCARD
"""
        return vcf_entry
    
    def generate_contacts(self, count, gender="all", carrier=None, unique_phones=True):
        """
        生成指定数量的联系人（姓名+电话）
        
        Args:
            count (int): 联系人数量
            gender (str): 性别选择 - "boy", "girl", "all"
            carrier (str): 运营商选择 - "mobile", "unicom", "telecom", "virtual", "all"
            unique_phones (bool): 是否确保电话号码唯一
            
        Returns:
            list: 联系人列表，每个元素为(姓名, 电话)元组
        """
        if count <= 0:
            return []
        
        # 生成姓名
        names = self.name_generator.generate_names(count, gender)
        
        # 生成电话号码
        phones = self.phone_generator.generate_phone_numbers(count, carrier=carrier, unique=unique_phones)
        
        # 确保姓名和电话数量匹配
        min_count = min(len(names), len(phones))
        contacts = [(names[i], phones[i]) for i in range(min_count)]
        
        return contacts
    
    def create_vcf_file(self, contacts, filename, encoding='utf-8'):
        """
        创建VCF文件
        
        Args:
            contacts (list): 联系人列表
            filename (str): 文件名
            encoding (str): 文件编码
            
        Returns:
            bool: 是否创建成功
        """
        try:
            with open(filename, 'w', encoding=encoding) as file:
                for name, phone in contacts:
                    vcf_entry = self.create_contact_vcf_entry(name, phone)
                    file.write(vcf_entry)
                    file.write('\n')  # 在联系人之间添加空行
            return True
        except Exception as e:
            print(f"创建VCF文件失败: {e}")
            return False
    
    def generate_vcf_files(self, file_count, contacts_per_file, 
                          output_dir="vcf_output", 
                          filename_prefix="通讯录",
                          gender="all", 
                          carrier=None, 
                          unique_phones=True,
                          progress_callback=None,
                          naming_mode="timestamp",
                          start_number=1,
                          number_format="{:03d}"):
        """
        批量生成VCF文件
        
        Args:
            file_count (int): 生成文件数量
            contacts_per_file (int): 每个文件的联系人数量
            output_dir (str): 输出目录
            filename_prefix (str): 文件名前缀
            gender (str): 性别选择
            carrier (str): 运营商选择
            unique_phones (bool): 是否确保电话号码唯一
            progress_callback (function): 进度回调函数
            naming_mode (str): 命名模式 - "timestamp"(时间戳) 或 "custom_number"(自定义序号)
            start_number (int): 自定义序号模式的起始数字
            number_format (str): 数字格式化字符串，如"{:03d}"表示3位数补零
            
        Returns:
            dict: 生成结果信息
        """
        # 创建输出目录
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"无法创建输出目录: {e}",
                    "files_created": 0
                }
        
        # 根据命名模式生成文件名
        if naming_mode == "timestamp":
            # 时间戳模式（原有逻辑）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        created_files = []
        failed_files = []
        
        for i in range(file_count):
            # 生成联系人
            contacts = self.generate_contacts(
                contacts_per_file, 
                gender=gender, 
                carrier=carrier, 
                unique_phones=unique_phones
            )
            
            # 根据命名模式生成文件名
            if naming_mode == "custom_number":
                # 自定义序号模式
                current_number = start_number + i
                number_str = number_format.format(current_number)
                filename = f"{filename_prefix}_{number_str}.vcf"
            else:
                # 时间戳模式（默认）
                filename = f"{filename_prefix}_{timestamp}_{i+1:03d}.vcf"
            
            filepath = os.path.join(output_dir, filename)
            
            # 创建VCF文件
            if self.create_vcf_file(contacts, filepath):
                created_files.append(filepath)
            else:
                failed_files.append(filepath)
            
            # 调用进度回调
            if progress_callback:
                progress = (i + 1) / file_count * 100
                progress_callback(int(progress))
        
        return {
            "success": len(failed_files) == 0,
            "files_created": len(created_files),
            "files_failed": len(failed_files),
            "created_files": created_files,
            "failed_files": failed_files,
            "output_directory": output_dir,
            "total_contacts": len(created_files) * contacts_per_file
        }
    
    def preview_vcf_content(self, count=3, gender="all", carrier=None):
        """
        生成VCF内容预览
        
        Args:
            count (int): 预览联系人数量
            gender (str): 性别选择
            carrier (str): 运营商选择
            
        Returns:
            str: VCF内容预览
        """
        contacts = self.generate_contacts(count, gender, carrier)
        preview_content = ""
        
        for name, phone in contacts:
            preview_content += self.create_contact_vcf_entry(name, phone)
            preview_content += "\n"
        
        return preview_content
    
    def get_generation_info(self, file_count, contacts_per_file):
        """
        获取生成任务的统计信息
        
        Args:
            file_count (int): 文件数量
            contacts_per_file (int): 每文件联系人数量
            
        Returns:
            dict: 统计信息
        """
        total_contacts = file_count * contacts_per_file
        
        # 估算文件大小（每个联系人约150字节）
        estimated_size_per_file = contacts_per_file * 150  # 字节
        total_estimated_size = file_count * estimated_size_per_file
        
        return {
            "文件数量": file_count,
            "每文件联系人数": contacts_per_file,
            "总联系人数": total_contacts,
            "预计单文件大小": f"{estimated_size_per_file / 1024:.1f} KB",
            "预计总大小": f"{total_estimated_size / 1024:.1f} KB" if total_estimated_size < 1024*1024 else f"{total_estimated_size / (1024*1024):.1f} MB"
        }


if __name__ == "__main__":
    # 测试代码
    vcf_gen = VCFGenerator()
    
    print("=== VCF通讯录生成器测试 ===")
    
    # 预览测试
    print("\nVCF内容预览:")
    preview = vcf_gen.preview_vcf_content(3, "all")
    print(preview)
    
    # 生成信息测试
    print("生成任务信息:")
    info = vcf_gen.get_generation_info(5, 100)
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # 小批量生成测试
    print("\n开始小批量测试...")
    result = vcf_gen.generate_vcf_files(
        file_count=2,
        contacts_per_file=10,
        output_dir="test_vcf",
        filename_prefix="测试通讯录"
    )
    
    print("生成结果:")
    for key, value in result.items():
        print(f"{key}: {value}") 