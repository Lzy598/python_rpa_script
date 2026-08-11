"""
Excel批量处理工具
用于：合并多文件、筛选分组、生成报表
影刀用法：传入文件路径列表，返回处理结果
"""

import pandas as pd
import os
from datetime import datetime


def merge_excel_files(file_list, output_path, sheet_name=None):
    """合并多个Excel文件"""
    all_data = []
    
    for f in file_list:
        try:
            if sheet_name:
                df = pd.read_excel(f, sheet_name=sheet_name)
            else:
                df = pd.read_excel(f)
            df['来源文件'] = os.path.basename(f)
            all_data.append(df)
        except Exception as e:
            print(f"读取失败 {f}: {e}")
    
    if not all_data:
        return {'status': 'error', 'message': '没有成功读取任何文件'}
    
    result = pd.concat(all_data, ignore_index=True)
    result.to_excel(output_path, index=False)
    
    return {
        'status': 'success',
        'file_count': len(all_data),
        'total_rows': len(result),
        'output_path': output_path
    }


def filter_and_group(input_path, output_path, 
                     filter_col=None, filter_val=None,
                     group_col=None, agg_col=None, agg_func='sum'):
    """筛选+分组汇总"""
    df = pd.read_excel(input_path)
    
    # 筛选
    if filter_col and filter_val is not None:
        df = df[df[filter_col] == filter_val]
    
    # 分组
    if group_col:
        if agg_col:
            grouped = df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
        else:
            grouped = df.groupby(group_col).size().reset_index(name='数量')
        grouped.to_excel(output_path, index=False)
        return {
            'status': 'success',
            'total_rows': len(df),
            'group_count': len(grouped),
            'output_path': output_path
        }
    
    # 不分组直接输出筛选结果
    df.to_excel(output_path, index=False)
    return {
        'status': 'success',
        'total_rows': len(df),
        'output_path': output_path
    }


def split_excel(input_path, output_dir, rows_per_file=1000):
    """把大Excel拆分成多个小文件"""
    df = pd.read_excel(input_path)
    total_rows = len(df)
    file_count = 0
    
    os.makedirs(output_dir, exist_ok=True)
    
    for start in range(0, total_rows, rows_per_file):
        end = min(start + rows_per_file, total_rows)
        chunk = df.iloc[start:end]
        
        output_name = os.path.join(
            output_dir, 
            f"拆分_{start+1}-{end}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        chunk.to_excel(output_name, index=False)
        file_count += 1
    
    return {
        'status': 'success',
        'original_rows': total_rows,
        'file_count': file_count,
        'output_dir': output_dir
    }


def generate_daily_report(detail_file, output_path):
    """从明细生成日报汇总"""
    df = pd.read_excel(detail_file)
    
    # 确保日期列是日期格式
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet1: 汇总
        summary = df.describe(include='all').round(2)
        summary.to_excel(writer, sheet_name='汇总')
        
        # Sheet2: 按日统计（如果有日期列）
        if '日期' in df.columns:
            daily = df.groupby(df['日期'].dt.date).agg(
                数量=('金额', 'count'),
                总金额=('金额', 'sum'),
                平均金额=('金额', 'mean')
            ).round(2)
            daily.to_excel(writer, sheet_name='按日统计')
        
        # Sheet3: 明细
        df.to_excel(writer, sheet_name='明细', index=False)
    
    return {'status': 'success', 'output_path': output_path}


# ===== 影刀入口 =====
if __name__ == '__main__':
    # 影刀传参示例
    input_files = ["{{文件路径1}}", "{{文件路径2}}"]
    out_path = "{{输出路径}}"
    
    result = merge_excel_files(input_files, out_path)
    # 输出到影刀变量：merge_result
    merge_result = result
