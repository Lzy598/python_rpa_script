"""
文本清洗 + 数据校验工具
影刀用法：复制此脚本到Python脚本组件，传入原始文本，获取清洗后结果
"""

import re
import json


def clean_text(raw_text):
    """通用文本清洗"""
    text = raw_text
    
    # 去掉HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去掉特殊符号（保留中文、英文、数字、常见标点）
    text = re.sub(r'[^\u4e00-\u9fff\w\s\.\,\-\:\;\$\¥\￥\%\#\@\（\）\(\)]', '', text)
    
    # 合并多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 全角转半角
    text = text.replace('，', ',').replace('。', '.').replace('；', ';')
    text = text.replace('：', ':').replace（'（', '(').replace('）', ')')
    
    return text


def extract_phone(text):
    """提取手机号"""
    phones = re.findall(r'1[3-9]\d{9}', text)
    return phones[0] if phones else ''


def extract_id_card(text):
    """提取身份证号"""
    ids = re.findall(r'\d{17}[\dXx]', text)
    return ids[0] if ids else ''


def extract_amounts(text):
    """提取金额"""
    amounts = re.findall(r'[¥￥]?\d+\.?\d{0,2}', text)
    return [a for a in amounts if a]


def extract_emails(text):
    """提取邮箱"""
    emails = re.findall(r'\w+@\w+\.\w+', text)
    return emails


def validate_phone(phone):
    """校验手机号"""
    return bool(re.match(r'^1[3-9]\d{9}$', phone))


def validate_email(email):
    """校验邮箱"""
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))


def validate_id_card(id_no):
    """简单校验身份证号"""
    if not re.match(r'^\d{17}[\dXx]$', id_no):
        return False
    # 校验出生日期
    birth = id_no[6:14]
    try:
        import datetime
        datetime.datetime.strptime(birth, '%Y%m%d')
        return True
    except:
        return False


def batch_clean_data(rows, columns_config):
    """
    批量清洗数据
    rows: [['张三', '13800138000'], ['李四', '13900139000']]
    columns_config: {
        'name': {'type': 'text', 'required': True},
        'phone': {'type': 'phone', 'required': True},
        'email': {'type': 'email', 'required': False}
    }
    """
    results = []
    errors = []
    
    for i, row in enumerate(rows):
        cleaned = {}
        for j, (col, config) in enumerate(columns_config.items()):
            val = str(row[j]) if j < len(row) else ''
            val = clean_text(val)
            
            # 校验
            if config.get('required') and not val:
                errors.append(f"第{i+1}行{col}为空")
                continue
            
            if config['type'] == 'phone' and val and not validate_phone(val):
                errors.append(f"第{i+1}行{col}格式错误: {val}")
            
            cleaned[col] = val
        
        if cleaned:
            results.append(cleaned)
    
    return {
        'success_count': len(results),
        'error_count': len(errors),
        'errors': errors,
        'data': results
    }


# ===== 影刀直接调用入口 =====
if __name__ == '__main__':
    # 影刀传入原始文本（替换为影刀变量）
    raw_input = "{{原始文本}}"
    
    result = {
        'cleaned': clean_text(raw_input),
        'phone': extract_phone(raw_input),
        'email': extract_emails(raw_input),
        'amounts': extract_amounts(raw_input)
    }
    
    # 输出到影刀变量
    # 设置输出变量：cleaned_text / extracted_info
    cleaned_text = json.dumps(result, ensure_ascii=False)
    extracted_info = result
