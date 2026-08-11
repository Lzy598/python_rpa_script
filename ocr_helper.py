"""
OCR验证码识别工具
影刀用法：传入图片路径，返回识别结果
依赖：pip install pytesseract pillow
需要安装Tesseract-OCR引擎
"""

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import re
import os


class OCRHelper:
    """OCR识别助手"""
    
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def preprocess(self, image_path):
        """图像预处理提高识别率"""
        img = Image.open(image_path)
        
        # 放大（提高低分辨率图片识别率）
        img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
        
        # 转灰度
        img = img.convert('L')
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # 二值化
        threshold = 140
        img = img.point(lambda x: 0 if x < threshold else 255)
        
        # 降噪
        img = img.filter(ImageFilter.MedianFilter(3))
        
        return img
    
    def recognize_captcha(self, image_path):
        """识别验证码（数字+字母）"""
        img = self.preprocess(image_path)
        code = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        code = re.sub(r'[^a-zA-Z0-9]', '', code).strip()
        return code
    
    def recognize_numbers(self, image_path):
        """识别纯数字"""
        img = self.preprocess(image_path)
        code = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789')
        code = re.sub(r'[^0-9]', '', code).strip()
        return code
    
    def recognize_chinese(self, image_path):
        """识别中文（如发票、工单）"""
        img = Image.open(image_path)
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        return text.strip()
    
    def batch_recognize(self, folder_path):
        """批量识别文件夹中的图片"""
        results = []
        for f in sorted(os.listdir(folder_path)):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                path = os.path.join(folder_path, f)
                code = self.recognize_captcha(path)
                results.append({'file': f, 'code': code})
                print(f"{f} → {code}")
        return results


# ===== 影刀入口 =====
if __name__ == '__main__':
    ocr = OCRHelper()
    
    # 识别验证码（传入图片路径）
    captcha_image = "{{验证码图片路径}}"
    captcha_type = "{{验证码类型}}"  # captcha / number / chinese
    
    if captcha_type == 'number':
        code = ocr.recognize_numbers(captcha_image)
    elif captcha_type == 'chinese':
        code = ocr.recognize_chinese(captcha_image)
    else:
        code = ocr.recognize_captcha(captcha_image)
    
    # 输出到影刀
    captcha_code = code
    
    # 批量处理
    batch_folder = "{{批量图片文件夹}}"
    batch_results = ocr.batch_recognize(batch_folder)
