"""
财务计算工具
影刀用法：传入财务数据，获取计算结果
"""

import json


class FinanceCalculator:
    """财务计算器"""
    
    @staticmethod
    def calc_salary(base, bonus=0, deduction=0, tax_rate=None):
        """计算实发工资"""
        gross = base + bonus
        
        # 个税计算（简化版）
        if tax_rate is None:
            taxable = max(0, gross - 5000)
            if taxable <= 3000:
                tax_rate = 0.03
                quick_deduct = 0
            elif taxable <= 12000:
                tax_rate = 0.1
                quick_deduct = 210
            elif taxable <= 25000:
                tax_rate = 0.2
                quick_deduct = 1410
            else:
                tax_rate = 0.25
                quick_deduct = 2660
            tax = taxable * tax_rate - quick_deduct
        else:
            tax = gross * tax_rate
        
        net = gross - tax - deduction
        
        return {
            '应发': round(gross, 2),
            '个税': round(max(0, tax), 2),
            '扣款': round(deduction, 2),
            '实发': round(net, 2)
        }
    
    @staticmethod
    def calc_invoice_tax(amount, tax_rate=0.13):
        """发票税额计算"""
        tax = round(amount * tax_rate / (1 + tax_rate), 2)
        no_tax = round(amount - tax, 2)
        return {
            '含税金额': amount,
            '不含税金额': no_tax,
            '税额': tax,
            '税率': f"{tax_rate*100}%"
        }
    
    @staticmethod
    def calc_reimbursement(items):
        """费用报销汇总
        items: [{'category':'交通','amount':100}, {'category':'餐饮','amount':200}]
        """
        total = 0
        by_category = {}
        
        for item in items:
            total += item['amount']
            cat = item['category']
            by_category[cat] = by_category.get(cat, 0) + item['amount']
        
        return {
            '总金额': total,
            '按分类': by_category,
            '笔数': len(items)
        }
    
    @staticmethod
    def calc_tax_report(revenue, cost, expense):
        """简易税务计算"""
        profit = revenue - cost - expense
        tax = max(0, profit * 0.25)  # 企业所得税25%
        net_profit = profit - tax
        
        return {
            '营业收入': revenue,
            '营业成本': cost,
            '期间费用': expense,
            '利润总额': profit,
            '所得税': round(tax, 2),
            '净利润': round(net_profit, 2),
            '利润率': f"{round(net_profit/revenue*100, 2)}%" if revenue else "0%"
        }


# ===== 影刀入口 =====
if __name__ == '__main__':
    calc = FinanceCalculator()
    
    calc_type = "{{计算类型}}"  # salary / invoice / tax_report
    
    if calc_type == 'salary':
        result = calc.calc_salary(
            float("{{基本工资}}"),
            float("{{奖金}}"),
            float("{{扣款}}")
        )
    elif calc_type == 'invoice':
        result = calc.calc_invoice_tax(
            float("{{含税金额}}")
        )
    elif calc_type == 'tax_report':
        result = calc.calc_tax_report(
            float("{{营业收入}}"),
            float("{{营业成本}}"),
            float("{{期间费用}}")
        )
    
    # 输出到影刀变量
    finance_result = result
