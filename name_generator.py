#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfoGen-信息生成器 - 核心逻辑模块
基于原JavaScript版本的完整Python实现
"""

import random


class PhoneGenerator:
    """中国大陆手机号码生成器类"""
    
    def __init__(self):
        """初始化手机号码前缀数据库"""
        # 中国大陆手机号码前缀（根据用户提供的最新号段）
        self.prefixes = [
            # 中国移动号段
            "134", "135", "136", "137", "138", "139", 
            "150", "151", "152", "157", "158", "159", 
            "182", "183", "184", "187", "188", 
            "195", "197", "198", 
            "147", "1440",  # 数据卡
            
            # 中国联通号段  
            "130", "131", "132", 
            "145", "155", "156", 
            "166", "175", "176", 
            "185", "186", 
            
            # 中国电信号段
            "133", "149", 
            "153", "173", "174", 
            "177", "180", "181", "189", 
            "190", "191", "193", "199",
            
            # 虚拟运营商号段
            "170", "171", "162"
        ]
        
        # 按运营商分类的号段
        self.mobile_prefixes = [
            "134", "135", "136", "137", "138", "139", 
            "150", "151", "152", "157", "158", "159", 
            "182", "183", "184", "187", "188", 
            "195", "197", "198", "147"
        ]
        
        self.unicom_prefixes = [
            "130", "131", "132", "145", "155", "156", 
            "166", "175", "176", "185", "186"
        ]
        
        self.telecom_prefixes = [
            "133", "149", "153", "173", "174", 
            "177", "180", "181", "189", 
            "190", "191", "193", "199"
        ]
        
        self.virtual_prefixes = [
            "170", "171", "162"
        ]

    def generate_phone_number(self, prefix=None, carrier=None):
        """
        生成一个手机号码
        
        Args:
            prefix (str): 指定前缀，如"138"，为None时随机选择
            carrier (str): 指定运营商，"mobile", "unicom", "telecom", "virtual", "all"
            
        Returns:
            str: 生成的11位手机号码
        """
        # 选择前缀
        if prefix:
            if prefix in self.prefixes:
                chosen_prefix = prefix
            else:
                raise ValueError(f"不支持的号段前缀: {prefix}")
        else:
            # 根据运营商选择前缀
            if carrier == "mobile":
                chosen_prefix = random.choice(self.mobile_prefixes)
            elif carrier == "unicom":
                chosen_prefix = random.choice(self.unicom_prefixes)
            elif carrier == "telecom":
                chosen_prefix = random.choice(self.telecom_prefixes)
            elif carrier == "virtual":
                chosen_prefix = random.choice(self.virtual_prefixes)
            else:
                chosen_prefix = random.choice(self.prefixes)
        
        # 生成后8位随机数字
        remaining_digits = 11 - len(chosen_prefix)
        random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits)])
        
        return chosen_prefix + random_suffix

    def generate_phone_numbers(self, count, prefix=None, carrier=None, unique=True):
        """
        批量生成手机号码
        
        Args:
            count (int): 生成数量
            prefix (str): 指定前缀
            carrier (str): 指定运营商
            unique (bool): 是否确保唯一性
            
        Returns:
            list: 生成的手机号码列表
        """
        if count <= 0:
            return []
            
        phone_numbers = []
        generated_set = set() if unique else None
        
        max_attempts = count * 10  # 防止无限循环
        attempts = 0
        
        while len(phone_numbers) < count and attempts < max_attempts:
            phone = self.generate_phone_number(prefix, carrier)
            
            if unique and generated_set is not None:
                if phone not in generated_set:
                    phone_numbers.append(phone)
                    generated_set.add(phone)
            else:
                phone_numbers.append(phone)
                
            attempts += 1
            
        return phone_numbers

    def get_carrier_name(self, phone_number):
        """
        根据手机号码前缀判断运营商
        
        Args:
            phone_number (str): 手机号码
            
        Returns:
            str: 运营商名称
        """
        if not phone_number or len(phone_number) < 3:
            return "未知"
            
        prefix = phone_number[:3]
        
        if prefix in self.mobile_prefixes:
            return "中国移动"
        elif prefix in self.unicom_prefixes:
            return "中国联通"
        elif prefix in self.telecom_prefixes:
            return "中国电信"
        elif prefix in self.virtual_prefixes:
            return "虚拟运营商"
        else:
            return "未知运营商"

    def get_statistics(self):
        """获取号段统计信息"""
        return {
            "总号段数": len(self.prefixes),
            "中国移动号段": len(self.mobile_prefixes),
            "中国联通号段": len(self.unicom_prefixes),
            "中国电信号段": len(self.telecom_prefixes),
            "虚拟运营商号段": len(self.virtual_prefixes),
            "支持的前缀": self.prefixes
        }


class NameGenerator:
    """中文姓名生成器类"""
    
    def __init__(self):
        """初始化姓名数据库"""
        # 男性双字名数组 (386个)
        self.boy2 = [
            "煜洋", "雨泽", "越泽", "之玉", "锦程", "修杰", "烨伟", "尔曼", "立辉", "致远", "天思", "友绿", "聪健", "修洁", "平灵", "源智", "烨华", "振家", "越彬",
            "子轩", "伟宸", "晋鹏", "觅松", "海亦", "雨珍", "浩宇", "嘉熙", "志泽", "苑博", "念波", "峻熙", "俊驰", "聪展", "南松", "黎昕", "谷波", "凝海", "靖易",
            "渊思", "煜祺", "乐驹", "风华", "睿渊", "博超", "天磊", "夜白", "初晴", "瑾瑜", "鹏飞", "弘文", "伟泽", "迎松", "雨泽", "白易", "远航", "晓啸", "智宸",
            "晓博", "靖琪", "十八", "君浩", "绍辉", "天德", "半山", "一江", "皓轩", "子默", "青寒", "问筠", "旭尧", "冷之", "天宇", "正豪", "文博", "明辉", "子骞", "灵竹",
            "三德", "连虎", "十三", "天川", "一德", "严青", "擎苍", "思远", "嘉懿", "鸿煊", "晟睿", "鸿涛", "孤风", "青文", "浩然", "明杰", "若风", "广山", "若之", "浩阑", "南风", "浩轩",
            "博涛", "烨霖", "天佑", "半雪", "文轩", "明轩", "鹏煊", "沛山", "道天", "千筹", "远望", "乘风", "道之", "乘云", "天抒", "士萧", "文龙", "一鸣", "半仙", "远锋", "元正",
            "断秋", "远山", "飞扬", "一笑", "天问", "浩天", "沧海", "安康", "安平", "安然", "安晏", "安宜", "安志", "波鸿", "博明", "博雅", "博易", "博远", "才哲", "才俊", "成和",
            "承安", "承平", "承宣", "承允", "承泽", "承志", "飞虎", "飞龙", "飞羽", "涵煦", "昊苍", "昊空", "昊然", "昊天", "宏达", "宏恺", "景辉", "景明", "景山", "乐池",
            "天逸", "伟志", "文宣", "文彦", "向晨", "向阳", "星阑", "阳波", "逸仙", "逸明", "正奇", "子瑜", "玮涛", "庭霖", "弘智", "品川", "钰宸", "子尘", "润楚", "元云", "杰弘", "杰棠", "智语", "绍若", "贤权", "禹哲", "纪德", "轩军", "楠佑", "鸿华", "峻莱", "裕韬", "寒淮", "烨若", "畅孝", "雨泰", "绍若", "庆韬", "浩慕", "恩晨", "佑晨", "翰俊", "聪铭", "瑜睿", "应泰", "为城", "炫杰", "竟锋", "亦韵", "若杰", "航苏", "俊建", "玮锋", "晔苏", "桦君", "信煊", "益正", "惠坪", "炳城", "川健", "煊博", "瀚强", "亦健", "卓逸", "仲智", "旭柳", "易扬", "浩淼", "若星", "书润", "文博", "圣霖", "濡温", "生朋", "永润", "温泰", "言佑", "乐凡", "均语", "卓锦", "炜泽", "奕辰", "韵熙", "汇润", "润庭", "伟俊", "立圣", "东子", "轩宏", "哲聪", "庭苍", "亮涛", "松清", "绍校",
            "峻熙", "立诚", "弘文", "熠彤", "鸿煊", "哲瀚", "博涛", "伟泽", "煜城", "鹤轩", "昊天", "思聪", "展鹏", "笑愚", "志强", "炫明", "雪松", "思源", "智渊", "思淼", "晓啸", "天宇", "浩然", "文轩", "鹭洋", "振家", "乐驹", "晓博", "文博", "昊焱", "立果", "金鑫", "锦程", "嘉熙", "鹏飞", "子默", "思远", "浩轩", "语堂", "聪健", "炎彬", "子骞", "君浩", "博超", "昊强", "鑫磊", "晋鹏", "雨泽", "弘文", "瑾瑜",
            "郜坤", "哲羽", "意致", "瑾靖", "易琦", "光济", "玄奕", "骞尧", "清嘉", "冷睿", "永丰", "夭锦", "辰哲", "承颜", "习凛", "堇文", "鹏云", "华茂", "永以", "澎湃", "康伯", "玉韬", "云霆", "雨伯", "友健", "维峰", "沺誉", "安陵", "君皓", "志勇", "茂材", "运杰", "苑博", "佳炎", "鸿月", "加答", "涛卓", "康顺", "凯定", "城可",
            "世砚", "博良", "俊宇", "睿书", "泓佳", "书鸣", "辉鑫", "语智", "艺智", "思涵", "呈岚", "天骐", "翰睿", "哲涛", "凯霆", "君皓", "言陌", "浩志", "勇笠", "玮翔", "志宇", "雄浚", "祖弘", "宏颢", "雨辰", "诗颢"
        ]

        # 中文姓氏数组 (301个)
        self.xing = [
            "赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈", "褚", "卫", "蒋",
            "沈", "韩", "杨", "朱", "秦", "尤", "许", "何", "吕", "施", "张", "孔", "曹", "严", "华", "金", "魏",
            "陶", "姜", "戚", "谢", "邹", "喻", "柏", "水", "窦", "章", "云", "苏", "潘", "葛", "奚", "范", "彭",
            "郎", "鲁", "韦", "昌", "马", "苗", "凤", "花", "方", "任", "袁", "柳", "鲍", "史", "唐", "费", "薛",
            "雷", "贺", "倪", "汤", "滕", "殷", "罗", "毕", "郝", "安", "常", "傅", "卞", "齐", "元", "顾", "孟",
            "平", "黄", "穆", "萧", "尹", "姚", "邵", "湛", "汪", "祁", "毛", "狄", "米", "伏", "成", "戴", "谈",
            "宋", "茅", "庞", "熊", "纪", "舒", "屈", "项", "祝", "董", "梁", "杜", "阮", "蓝", "闵", "季", "贾",
            "路", "娄", "江", "童", "颜", "郭", "梅", "盛", "林", "钟", "徐", "邱", "骆", "高", "夏", "蔡", "田",
            "樊", "胡", "凌", "霍", "虞", "万", "支", "柯", "管", "卢", "莫", "柯", "房", "裘", "缪", "解", "应",
            "宗", "丁", "宣", "邓", "单", "杭", "洪", "包", "诸", "左", "石", "崔", "吉", "龚", "程", "嵇", "邢",
            "裴", "陆", "荣", "翁", "荀", "于", "惠", "甄", "曲", "封", "储", "仲", "伊", "宁", "仇", "甘", "武",
            "符", "刘", "景", "詹", "龙", "叶", "幸", "司", "黎", "溥", "印", "怀", "蒲", "邰", "从", "索", "赖",
            "卓", "屠", "池", "乔", "胥", "闻", "莘", "翟", "谭", "贡", "劳", "逄", "姬", "申", "扶", "堵",
            "冉", "宰", "雍", "桑", "寿", "通", "燕", "浦", "尚", "农", "温", "别", "庄", "晏", "柴", "瞿", "阎",
            "连", "习", "容", "向", "古", "易", "廖", "庾", "终", "步", "都", "耿", "满", "弘", "匡", "国", "文",
            "寇", "广", "禄", "阙", "东", "欧", "利", "师", "巩", "聂", "关", "荆", "红", "游", "竺", "司马", "上官", "欧阳", "夏侯",
            "诸葛", "东方", "赫连", "皇甫", "尉迟", "公羊", "澹台", "公冶", "宗政", "濮阳", "淳于", "单于",
            "太叔", "申屠", "公孙", "仲孙", "轩辕", "令狐", "宇文", "长孙", "慕容", "司徒", "司空", "拓拔"
        ]

        # 女性双字名数组 (580个) 
        self.girl2 = [
            "紫萱", "紫霜", "紫菱", "紫蓝", "紫翠", "紫安", "芷容", "芷巧", "芷卉", "之桃", "元霜", "语雪", "语蓉", "语琴", "语芙", "语蝶", "雨梅", "雨莲", "雨兰", "又菡",
            "映萱", "映安", "忆雪", "雅彤", "雪瑶", "雪卉", "晓夏", "向梦", "香萱", "香岚", "惜雪", "思菱", "水瑶", "诗桃", "山菡", "若菱", "青曼", "千柔", "绮梅", "凝雁", "凝安",
            "妙之", "凌波", "寄琴", "涵易", "涵菱", "含烟", "曼冬", "灵珊", "映菡", "易真", "小萱", "怜南", "书瑶", "慕晴", "半烟", "翠桃", "向真", "晓瑶", "香菱", "凡霜", "晓霜",
            "芷蝶", "之云", "寄翠", "涵菡", "念薇", "灵凡", "冰夏", "绮晴", "碧琴", "以寒",
            "梦绾", "禾霓", "落柔", "恬栖", "以蓝", "星楚", "晚棠", "乐薇", "云毓", "静昀", "洛一", "馨雅", "芊昔", "沐颜", "清墨", "意羡", "禾凝", "黎思", "锦惜", "北茉", "清筱", "青玥", "可星", "芝恬", "昕甜", "禾婉", "慕唯", "唯兮", "歆一", "佳念", "晚柠", "初恩", "乐晗", "佳觅", "初语", "苏郁", "知宛", "意暄", "安诺", "可夏", "予希", "木冉", "优游", "伊依", "倾清", "心歆", "颖恩", "楚瑶", "如一", "沐心",
            "子沛", "婷秀", "芳凝", "洛颜", "思璐", "郡一", "向妙", "想蓉", "待臻", "姝美", "蓉柳", "溪颜", "璞诗", "知韦", "之寒", "蓉珊", "尔毓", "诗睿", "诗钰", "念汐", "恬懿", "和佩", "芒可", "靖柳", "欣碧", "婧媛", "芸霞", "子茗", "梦琳", "琳姿", "寄影", "若嫣", "艺珂", "素琳", "淑云", "茜涵", "莹云", "清媛", "思怡", "待晚", "绮晴", "夏婷", "熙瑾", "玉珍", "语彤", "聪怡", "善蕊", "菀柠", "颖菲", "君雨", "柳如", "欣静", "怡岚", "芳睿", "语淑", "慧偲", "半槐", "娥菲", "余芸", "婉吟", "媚鸿", "听薇", "恬懿", "琳娜", "思妤", "双芸", "梓欣", "乐巧", "宁敏", "逸恬", "婷颜", "羽莹", "曼溪", "思璎", "梦淑", "映嘉", "天亦", "映凝", "曦薇", "泱祺", "艳蕊", "壁煊", "心怡", "茉涵", "熙柔", "玥芙", "倚真", "雅惠", "千羽", "思雅",
            "希柠", "辰柚", "亦橙", "伊桃", "南柚", "蕉礼", "橙美", "宛桔", "皙恬", "锦芊", "栀萌", "亦攸", "皙宁", "舒淳", "以葵", "伊湉", "司纯", "稚京", "奈笙", "西棠", "今安", "晏乔", "舒然", "慕倾", "玖鸢", "思莞", "紫茉", "珑琪", "冉峤", "凝初", "南嫣", "知潼", "奕北", "桑宁", "禾茉", "昕言", "念一", "希雅", "伊诺", "婉柠", "岁穗", "苏酥", "诗施", "声笙", "芊澄", "梨珂", "晞悦", "芮柒", "南星", "苡沫", "鹿绫", "楚奈", "芊凛", "婉宁", "安禾", "舒言", "芮瑶", "艺涵", "恬雨", "清颜", "乔仪", "幼沅", "简心", "宁希", "婧恬", "黎念",
            "灵淼", "含卿", "兮虞", "缘珞", "依莹", "玥冰", "谷梓", "南芊", "筱茵", "甜亦", "佳知", "惜珞", "惜灵", "傲晴", "若琼", "晴岚", "诗淇", "语兰", "傲龄", "知薇", "晓汐", "萌知", "含蓓", "安冉", "梓紫", "璇知", "冰晴", "汐梓", "静若", "诗云", "紫知", "紫丝", "觅甜", "奕芊", "倩知", "笑珞", "万姝", "初瑶", "妍依", "碧希", "晓蓓", "冉娇", "笑龄", "以兮", "兮筱", "雨甯", "妤华", "冰蓉", "沁蓉", "万奕", "虞兰", "静笛", "媱雅", "黛绿", "水静", "水妍", "语蕊", "欣蓉", "妙馨", "龄蓉", "紫莎", "婧琳", "甜晴", "静芙", "恬娣", "晓倩", "熙萱", "冉清", "歆瑜", "黛颖", "婧芷", "姗梵", "夏蓉", "菲悦", "依龄", "寻双"
        ]

        # 男性单字名数组 (59个)
        self.boy1 = [
            "宇", "翔", "飞", "雄", "帅", "涛", "强", "斌", "昊", "伟", "泽", "峰", "博", "德", "荣", "辉", "俊", "志", "勇", "琪", "杰", "洋", "瑞", "奇", "鸿", "浩", "宏", "华", "东", "光", "辰", "丰", "栋", "昌", "朋", "坚", "智", "聪", "亮", "正", "明", "诚", "永", "联", "瑜", "雷", "威", "敏", "乐", "信", "柏", "佳", "晋", "育", "立", "祥", "学", "豪", "仁", "友"
        ]

        # 女性单字名数组 (77个)
        self.girl1 = [
            "美", "娜", "秀", "雯", "蕾", "洁", "思", "慧", "心", "涵", "静", "英", "晓", "琳", "珊", "莉", "佳", "婷", "璐", "晨", "安", "包", "贝", "冰", "蓓", "珂", "柏", "琳", "菲", "怡", "娜", "心", "洁", "梓", "瑶", "珊", "艾", "诗", "璐", "倩", "苏", "雯", "婧", "秀", "慧", "彤", "媛", "美", "晶", "琪", "云", "萍", "蕾", "莉", "莹", "薇", "楠", "楚", "佳", "爽", "卓", "格", "斌", "羽", "茜", "婷", "琦", "绮", "燕", "张", "青", "红", "翠", "帆", "离", "莲", "宜", "园", "冬", "霜"
        ]

    def get_random_from_array(self, array):
        """从数组中随机选择一个元素"""
        return random.choice(array)

    def make_boy_name(self):
        """生成男性姓名"""
        first = self.get_random_from_array(self.xing)
        
        # 70%概率生成双字名，30%概率生成单字名
        choice = 1 if random.random() < 0.7 else 2
        
        if choice == 1:
            second = self.get_random_from_array(self.boy2)
        else:
            second = self.get_random_from_array(self.boy1)
            
        return first + second

    def make_girl_name(self):
        """生成女性姓名"""
        first = self.get_random_from_array(self.xing)
        
        # 70%概率生成双字名，30%概率生成单字名
        choice = 1 if random.random() < 0.7 else 2
        
        if choice == 1:
            second = self.get_random_from_array(self.girl2)
        else:
            second = self.get_random_from_array(self.girl1)
            
        return first + second

    def generate_names(self, num, gender="all"):
        """
        生成指定数量和性别的姓名
        
        Args:
            num (int): 生成数量
            gender (str): 性别选择 - "boy", "girl", "all"
            
        Returns:
            list: 生成的姓名列表
        """
        if num <= 0:
            return []
            
        names = []
        
        for _ in range(num):
            if gender == "boy":
                names.append(self.make_boy_name())
            elif gender == "girl":
                names.append(self.make_girl_name())
            elif gender == "all":
                # 随机选择男性或女性姓名
                choice = random.randint(1, 2)
                if choice == 1:
                    names.append(self.make_boy_name())
                else:
                    names.append(self.make_girl_name())
                    
        return names

    def get_statistics(self):
        """获取姓名数据库统计信息"""
        return {
            "姓氏数量": len(self.xing),
            "男性双字名": len(self.boy2),
            "男性单字名": len(self.boy1),
            "女性双字名": len(self.girl2),
            "女性单字名": len(self.girl1),
            "理论组合数": {
                "男性双字名组合": len(self.xing) * len(self.boy2),
                "男性单字名组合": len(self.xing) * len(self.boy1),
                "女性双字名组合": len(self.xing) * len(self.girl2),
                "女性单字名组合": len(self.xing) * len(self.girl1)
            }
        }


if __name__ == "__main__":
    # 测试代码
    name_generator = NameGenerator()
    phone_generator = PhoneGenerator()
    
    print("=== InfoGen-信息生成器测试 ===")
    print("\n姓名数据库统计信息:")
    name_stats = name_generator.get_statistics()
    for key, value in name_stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v:,}")
        else:
            print(f"{key}: {value}")
    
    print("\n姓名生成测试:")
    print("男性姓名示例:", name_generator.generate_names(5, "boy"))
    print("女性姓名示例:", name_generator.generate_names(5, "girl"))
    print("混合姓名示例:", name_generator.generate_names(5, "all"))
    
    print("\n=== 手机号码生成器测试 ===")
    print("\n号段统计信息:")
    phone_stats = phone_generator.get_statistics()
    for key, value in phone_stats.items():
        if isinstance(value, list):
            print(f"{key}: {len(value)}个 (部分示例: {value[:5]}...)")
        else:
            print(f"{key}: {value}")
    
    print("\n手机号码生成测试:")
    print("随机号码:", phone_generator.generate_phone_numbers(5))
    print("移动号码:", phone_generator.generate_phone_numbers(3, carrier="mobile"))
    print("联通号码:", phone_generator.generate_phone_numbers(3, carrier="unicom"))
    print("电信号码:", phone_generator.generate_phone_numbers(3, carrier="telecom"))
    
    # 运营商识别测试
    test_phones = phone_generator.generate_phone_numbers(3)
    print("\n运营商识别测试:")
    for phone in test_phones:
        carrier = phone_generator.get_carrier_name(phone)
        print(f"{phone} -> {carrier}") 