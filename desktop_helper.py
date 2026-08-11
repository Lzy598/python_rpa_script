"""
桌面自动化辅助工具
影刀无法定位桌面元素时，用此工具兜底
依赖：pip install pyautogui pillow
"""

import pyautogui
import time
import random
import os


class DesktopHelper:
    """桌面自动化辅助"""
    
    def __init__(self):
        # 失败截图目录
        self.screenshot_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'rpa_debug')
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def click_image(self, image_path, confidence=0.8, timeout=10):
        """通过图像识别点击"""
        start = time.time()
        while time.time() - start < timeout:
            pos = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if pos:
                center = pyautogui.center(pos)
                # 模拟真实点击：先移动到再点击
                pyautogui.moveTo(center.x + random.randint(-3, 3), 
                                center.y + random.randint(-3, 3),
                                duration=random.uniform(0.1, 0.3))
                time.sleep(0.1)
                pyautogui.click()
                return True
            time.sleep(0.3)
        return False
    
    def find_and_click_all(self, image_path, confidence=0.8):
        """查找所有匹配的元素并点击"""
        positions = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
        clicked = 0
        for pos in positions:
            center = pyautogui.center(pos)
            pyautogui.click(center)
            clicked += 1
            time.sleep(0.5)
        return clicked
    
    def wait_and_get_screenshot(self, region=None, timeout=10, output_name='debug'):
        """等待并截图"""
        time.sleep(timeout)
        path = os.path.join(self.screenshot_dir, f"{output_name}_{int(time.time())}.png")
        if region:
            pyautogui.screenshot(path, region=region)
        else:
            pyautogui.screenshot(path)
        return path
    
    def type_text(self, text, interval=0.05):
        """模拟真人打字（带随机间隔）"""
        for char in text:
            pyautogui.write(char)
            time.sleep(interval * random.uniform(0.5, 2.0))
    
    def human_like_click(self, x, y):
        """模拟真人点击（带随机偏移和移动曲线）"""
        # 移动到目标附近
        start_x, start_y = pyautogui.position()
        end_x = x + random.randint(-2, 2)
        end_y = y + random.randint(-2, 2)
        
        # 模拟曲线移动（3个控制点）
        steps = random.randint(8, 12)
        for i in range(steps):
            progress = (i + 1) / steps
            cx = start_x + (end_x - start_x) * progress + random.randint(-5, 5)
            cy = start_y + (end_y - start_y) * progress + random.randint(-5, 5)
            pyautogui.moveTo(cx, cy, duration=0.01)
        
        time.sleep(random.uniform(0.05, 0.15))
        pyautogui.click()
    
    def drag_slider(self, start_x, start_y, distance):
        """模拟滑块拖动"""
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        
        # 分段拖动（模拟人类）
        segments = 20
        for i in range(segments + 1):
            x = start_x + distance * (i / segments)
            y = start_y + random.randint(-2, 2)  # 轻微抖动
            pyautogui.moveTo(x, y, duration=0.01)
            time.sleep(random.uniform(0.005, 0.015))
        
        pyautogui.mouseUp()
        time.sleep(0.5)
    
    def paste_from_clipboard(self, text):
        """设置剪贴板并粘贴"""
        import subprocess
        # 使用PowerShell设置剪贴板
        encoded = text.replace('"', '\\"')
        ps_script = f'Set-Clipboard -Value "{encoded}"'
        subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
    
    def press_multiple_tabs(self, times):
        """按多次Tab（在表单间切换）"""
        for _ in range(times):
            pyautogui.press('tab')
            time.sleep(0.1)


# ===== 影刀入口 =====
if __name__ == '__main__':
    dt = DesktopHelper()
    
    action = "{{操作类型}}"  # click / type / drag / paste
    
    if action == 'click':
        image = "{{按钮图片路径}}"
        result = dt.click_image(image)
    elif action == 'type':
        text = "{{输入文本}}"
        dt.type_text(text)
        result = "输入完成"
    elif action == 'paste':
        text = "{{剪贴板内容}}"
        dt.paste_from_clipboard(text)
        result = "粘贴完成"
    
    # 输出到影刀变量
    desktop_result = result
