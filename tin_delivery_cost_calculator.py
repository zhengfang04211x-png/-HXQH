#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
锡（Sn）期现交割成本测算模型
基于多晶硅套利表的逻辑，适配锡的交割规则
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# 导入参数配置
try:
    from tin_params_config import (
        STORAGE_FEE_PER_TON_PER_DAY,
        DELIVERY_UNIT_TON,
        TRADING_UNIT_TON,
        INBOUND_FEE_PER_TON,
        OUTBOUND_FEE_PER_TON,
        PACKING_FEE_PER_TON,
        TRANSFER_FEE_PER_TON,
        DELIVERY_FEE_PER_TON,
        VAT_RATE,
        DEFAULT_INTEREST_RATE,
        FUTURES_MARGIN_RATE
    )
except ImportError:
    # 如果配置文件不存在，使用默认值
    STORAGE_FEE_PER_TON_PER_DAY = 1.50
    DELIVERY_UNIT_TON = 2.0
    TRADING_UNIT_TON = 1.0
    INBOUND_FEE_PER_TON = 30.0
    OUTBOUND_FEE_PER_TON = 30.0
    PACKING_FEE_PER_TON = 40.0
    TRANSFER_FEE_PER_TON = 2.0
    DELIVERY_FEE_PER_TON = 1.0
    VAT_RATE = 0.13
    DEFAULT_INTEREST_RATE = 0.05
    FUTURES_MARGIN_RATE = 0.10


class TinDeliveryCostCalculator:
    """锡期现交割成本计算器"""
    
    def __init__(self):
        """初始化锡的交割参数"""
        # ========== 锡的固定交割参数 ==========
        # 从配置文件加载参数
        self.storage_fee_per_ton_per_day = STORAGE_FEE_PER_TON_PER_DAY
        self.delivery_unit_ton = DELIVERY_UNIT_TON
        self.trading_unit_ton = TRADING_UNIT_TON
        self.inbound_fee_per_ton = INBOUND_FEE_PER_TON
        self.outbound_fee_per_ton = OUTBOUND_FEE_PER_TON
        self.packing_fee_per_ton = PACKING_FEE_PER_TON
        self.transfer_fee_per_ton = TRANSFER_FEE_PER_TON
        self.delivery_fee_per_ton = DELIVERY_FEE_PER_TON
        self.vat_rate = VAT_RATE
        self.default_interest_rate = DEFAULT_INTEREST_RATE
        self.futures_margin_rate = FUTURES_MARGIN_RATE
    
    def calculate_margin_rate(
        self,
        start_date: datetime,
        delivery_date: datetime,
        last_trading_date: Optional[datetime] = None,
        enterprise_margin_addon: float = 0.0,
        listing_date: Optional[datetime] = None,
        month_before_delivery_date: Optional[datetime] = None,
        delivery_month_start_date: Optional[datetime] = None,
        two_days_before_last_date: Optional[datetime] = None,
        rate_5_percent: float = 0.05,
        rate_10_percent: float = 0.10,
        rate_15_percent: float = 0.15,
        rate_20_percent: float = 0.20
    ) -> Tuple[float, Dict[str, any]]:
        """
        计算动态保证金比例
        
        参数:
            start_date: 开始日期（买入现货日期）
            delivery_date: 交割日期
            last_trading_date: 最后交易日（可选，如果为None则基于交割日期计算）
            enterprise_margin_addon: 企业保证金加收比例（如0.05表示5%）
            listing_date: 合约挂牌日期（如果为None，则使用start_date）
            month_before_delivery_date: 交割月前第一月的第一个交易日（如果为None，则自动计算）
            delivery_month_start_date: 交割月份第一个交易日（如果为None，则自动计算）
            two_days_before_last_date: 最后交易日前二个交易日（如果为None，则自动计算）
            rate_5_percent: 第一阶段保证金比例（默认5%）
            rate_10_percent: 第二阶段保证金比例（默认10%）
            rate_15_percent: 第三阶段保证金比例（默认15%）
            rate_20_percent: 第四阶段保证金比例（默认20%）
        
        返回:
            (平均保证金比例, 详细信息字典)
        """
        # 计算关键时间点（如果未提供则自动计算）
        if listing_date is None:
            listing_date = start_date
        
        if month_before_delivery_date is None:
            # 交割月前第一月的第一个交易日（简化处理，假设为交割月前一个月的1号）
            month_before_delivery_date = delivery_date.replace(day=1) - timedelta(days=1)
            month_before_delivery_date = month_before_delivery_date.replace(day=1)
        
        if delivery_month_start_date is None:
            # 交割月份第一个交易日（交割月1号）
            delivery_month_start_date = delivery_date.replace(day=1)
        
        if two_days_before_last_date is None:
            # 最后交易日前二个交易日（如果未提供last_trading_date，则基于交割日期计算）
            if last_trading_date is None:
                two_days_before_last_date = delivery_date - timedelta(days=2)
            else:
                two_days_before_last_date = last_trading_date - timedelta(days=2)
        
        # 确定每个时间段
        periods = []
        current_date = start_date
        
        # 1. 合约挂牌之日起（使用rate_5_percent）
        if current_date < month_before_delivery_date:
            periods.append({
                'start': current_date,
                'end': min(month_before_delivery_date, delivery_date),
                'rate': rate_5_percent,
                'description': '合约挂牌之日起'
            })
            current_date = month_before_delivery_date
        
        # 2. 交割月前第一月的第一个交易日起（使用rate_10_percent）
        if current_date < delivery_month_start_date:
            periods.append({
                'start': current_date,
                'end': min(delivery_month_start_date, delivery_date),
                'rate': rate_10_percent,
                'description': '交割月前第一月的第一个交易日起'
            })
            current_date = delivery_month_start_date
        
        # 3. 交割月份第一个交易日起（使用rate_15_percent）
        if current_date < two_days_before_last_date:
            periods.append({
                'start': current_date,
                'end': min(two_days_before_last_date, delivery_date),
                'rate': rate_15_percent,
                'description': '交割月份第一个交易日起'
            })
            current_date = two_days_before_last_date
        
        # 4. 最后交易日前二个交易日起（使用rate_20_percent）
        if current_date < delivery_date:
            periods.append({
                'start': current_date,
                'end': delivery_date,
                'rate': rate_20_percent,
                'description': '最后交易日前二个交易日起'
            })
        
        # 计算加权平均保证金比例
        total_days = (delivery_date - start_date).days
        if total_days == 0:
            avg_rate = 0.20
        else:
            weighted_sum = 0
            for period in periods:
                period_days = (period['end'] - period['start']).days
                weighted_sum += period['rate'] * period_days
            avg_rate = weighted_sum / total_days
        
        # 加上企业保证金加收比例
        final_rate = avg_rate + enterprise_margin_addon
        
        return final_rate, {
            'periods': periods,
            'average_rate': avg_rate,
            'enterprise_addon': enterprise_margin_addon,
            'final_rate': final_rate,
            'total_days': total_days,
            'listing_date': listing_date,
            'month_before_delivery_date': month_before_delivery_date,
            'delivery_month_start_date': delivery_month_start_date,
            'two_days_before_last_date': two_days_before_last_date
        }
    
    def calculate_capital_cost(
        self, 
        spot_price: float, 
        quantity_ton: float,
        start_date: datetime,
        end_date: datetime,
        interest_rate: Optional[float] = None,
        margin_rate: Optional[float] = None
    ) -> Dict[str, float]:
        """
        计算资金占用成本（同时计算现货和期货保证金）
        
        参数:
            spot_price: 现货价格（元/吨）
            quantity_ton: 数量（吨）
            start_date: 开始日期
            end_date: 结束日期
            interest_rate: 资金利率（年化），默认使用self.default_interest_rate
            margin_rate: 期货保证金比例（如果提供了margin_rate，则使用此值，否则使用默认值）
        
        返回:
            包含资金成本明细的字典
        """
        if interest_rate is None:
            interest_rate = self.default_interest_rate
        
        holding_days = (end_date - start_date).days
        # 确保持有天数不为负数
        if holding_days < 0:
            holding_days = 0
        
        # 计算现货资金占用（全额现货款，含增值税）
        spot_capital_amount = spot_price * quantity_ton * (1 + self.vat_rate)
        
        # 计算期货保证金占用
        if margin_rate is not None:
            used_margin_rate = max(0, margin_rate)  # 确保保证金比例不为负数
        else:
            used_margin_rate = self.futures_margin_rate
        
        futures_capital_amount = spot_price * quantity_ton * used_margin_rate
        
        # 总资金占用
        total_capital_amount = spot_capital_amount + futures_capital_amount
        
        # 计算资金利息（按天计算）
        daily_rate = interest_rate / 365
        spot_interest_cost = spot_capital_amount * daily_rate * holding_days
        futures_interest_cost = futures_capital_amount * daily_rate * holding_days
        total_interest_cost = spot_interest_cost + futures_interest_cost
        
        # 确保所有成本都是正数
        spot_interest_cost = max(0, spot_interest_cost)
        futures_interest_cost = max(0, futures_interest_cost)
        total_interest_cost = spot_interest_cost + futures_interest_cost
        
        return {
            "spot_capital_amount": spot_capital_amount,
            "futures_capital_amount": futures_capital_amount,
            "total_capital_amount": total_capital_amount,
            "spot_interest_cost": spot_interest_cost,
            "futures_interest_cost": futures_interest_cost,
            "total_interest_cost": total_interest_cost,
            "interest_rate": interest_rate,
            "holding_days": holding_days,
            "margin_rate": used_margin_rate
        }
    
    def calculate_storage_cost(
        self,
        quantity_ton: float,
        holding_days: int
    ) -> Dict[str, float]:
        """
        计算仓储成本
        
        参数:
            quantity_ton: 数量（吨）
            holding_days: 持有天数
        
        返回:
            包含仓储成本明细的字典
        """
        storage_cost = self.storage_fee_per_ton_per_day * quantity_ton * holding_days
        
        return {
            "storage_fee_per_ton_per_day": self.storage_fee_per_ton_per_day,
            "quantity_ton": quantity_ton,
            "holding_days": holding_days,
            "storage_cost": storage_cost
        }
    
    def calculate_delivery_fees(
        self,
        quantity_ton: float,
        inbound_fee_per_ton: Optional[float] = None,
        outbound_fee_per_ton: Optional[float] = None,
        packing_fee_per_ton: Optional[float] = None,
        transfer_fee_per_ton: Optional[float] = None,
        delivery_fee_per_ton: Optional[float] = None,
        train_application_fee_per_ton: float = 0.0,
        transport_fee_per_ton: float = 0.0
    ) -> Dict[str, float]:
        """
        计算交割杂费（入库费、出库费、打包费、过户费等）
        
        参数:
            quantity_ton: 数量（吨）
            inbound_fee_per_ton: 入库费（元/吨），如果为None则使用默认值
            outbound_fee_per_ton: 出库费（元/吨），如果为None则使用默认值
            packing_fee_per_ton: 打包费（元/吨），如果为None则使用默认值
            transfer_fee_per_ton: 过户费（元/吨），如果为None则使用默认值
            delivery_fee_per_ton: 交割手续费（元/吨），如果为None则使用默认值
            train_application_fee_per_ton: 代办车皮申请费（元/吨）
            transport_fee_per_ton: 代办提运费（元/吨）
        
        返回:
            包含各项交割杂费的字典
        """
        inbound_cost = (inbound_fee_per_ton or self.inbound_fee_per_ton) * quantity_ton
        outbound_cost = (outbound_fee_per_ton or self.outbound_fee_per_ton) * quantity_ton
        packing_cost = (packing_fee_per_ton or self.packing_fee_per_ton) * quantity_ton
        transfer_cost = (transfer_fee_per_ton or self.transfer_fee_per_ton) * quantity_ton
        delivery_fee_cost = (delivery_fee_per_ton or self.delivery_fee_per_ton) * quantity_ton
        train_app_cost = train_application_fee_per_ton * quantity_ton
        transport_cost = transport_fee_per_ton * quantity_ton
        
        total_misc_fees = (
            inbound_cost + 
            outbound_cost + 
            packing_cost + 
            transfer_cost + 
            delivery_fee_cost +
            train_app_cost +
            transport_cost
        )
        
        return {
            "inbound_fee": inbound_cost,
            "outbound_fee": outbound_cost,
            "packing_fee": packing_cost,
            "transfer_fee": transfer_cost,
            "delivery_fee": delivery_fee_cost,
            "train_application_fee": train_app_cost,
            "transport_fee": transport_cost,
            "total_misc_fees": total_misc_fees
        }
    
    def calculate_total_cost(
        self,
        spot_price: float,
        quantity_ton: float,
        start_date: datetime,
        end_date: datetime,
        interest_rate: Optional[float] = None,
        margin_rate: Optional[float] = None,
        inbound_fee_per_ton: Optional[float] = None,
        outbound_fee_per_ton: Optional[float] = None,
        packing_fee_per_ton: Optional[float] = None,
        transfer_fee_per_ton: Optional[float] = None,
        delivery_fee_per_ton: Optional[float] = None,
        train_application_fee_per_ton: float = 0.0,
        transport_fee_per_ton: float = 0.0
    ) -> Dict[str, any]:
        """
        计算期现套利总成本
        
        核心公式：
        期现套利总成本 = 现货买入价 + 入库杂费 + (仓储费 × 天数) + 资金利息（现货+期货） + 交割手续费
        
        参数:
            spot_price: 现货价格（元/吨）
            quantity_ton: 数量（吨）
            start_date: 开始日期（买入现货日期）
            end_date: 结束日期（交割日期）
            interest_rate: 资金利率（年化），默认使用self.default_interest_rate
            margin_rate: 期货保证金比例（如果提供了margin_rate，则使用此值）
            其他费用参数：入库费、出库费等，如果为None则使用默认值
        
        返回:
            包含所有成本明细的字典
        """
        holding_days = (end_date - start_date).days
        
        # 1. 现货买入成本（含增值税）
        spot_cost = spot_price * quantity_ton * (1 + self.vat_rate)
        
        # 2. 交割杂费
        misc_fees = self.calculate_delivery_fees(
            quantity_ton,
            inbound_fee_per_ton,
            outbound_fee_per_ton,
            packing_fee_per_ton,
            transfer_fee_per_ton,
            delivery_fee_per_ton,
            train_application_fee_per_ton,
            transport_fee_per_ton
        )
        
        # 3. 仓储成本
        storage = self.calculate_storage_cost(quantity_ton, holding_days)
        
        # 4. 资金利息（同时计算现货和期货保证金）
        capital = self.calculate_capital_cost(
            spot_price, quantity_ton, start_date, end_date,
            interest_rate, margin_rate
        )
        
        # 5. 总成本
        total_cost = (
            spot_cost +
            misc_fees["total_misc_fees"] +
            storage["storage_cost"] +
            capital["total_interest_cost"]
        )
        
        # 6. 单位成本（元/吨）
        cost_per_ton = total_cost / quantity_ton
        
        # 7. 盈亏平衡点（期货价格需要达到这个水平才能保本）
        break_even_price = spot_price + (total_cost - spot_cost) / quantity_ton
        
        return {
            "input": {
                "spot_price": spot_price,
                "quantity_ton": quantity_ton,
                "start_date": start_date,
                "end_date": end_date,
                "holding_days": holding_days,
                "interest_rate": capital["interest_rate"],
                "margin_rate": capital["margin_rate"]
            },
            "cost_breakdown": {
                "spot_cost_with_vat": spot_cost,
                "spot_cost_base": spot_price * quantity_ton,
                "vat_amount": spot_price * quantity_ton * self.vat_rate,
                "misc_fees": misc_fees,
                "storage_cost": storage["storage_cost"],
                "capital_cost": capital["total_interest_cost"],
                "spot_capital_cost": capital["spot_interest_cost"],
                "futures_capital_cost": capital["futures_interest_cost"]
            },
            "summary": {
                "total_cost": total_cost,
                "cost_per_ton": cost_per_ton,
                "break_even_price": break_even_price,
                "premium_needed": break_even_price - spot_price
            }
        }
    
    def check_arbitrage(
        self,
        spot_price: float,
        futures_price: float,
        quantity_ton: float,
        start_date: datetime,
        end_date: datetime,
        interest_rate: Optional[float] = None,
        margin_rate: Optional[float] = None,
        **fee_kwargs
    ) -> Dict[str, any]:
        """
        检查是否能套利
        
        参数:
            spot_price: 现货价格（元/吨）
            futures_price: 期货价格（元/吨）
            quantity_ton: 数量（吨）
            start_date: 开始日期
            end_date: 结束日期
            interest_rate: 资金利率（年化）
            margin_rate: 期货保证金比例
            其他费用参数：**fee_kwargs
        
        返回:
            包含套利分析结果的字典
        """
        # 计算总成本
        cost_result = self.calculate_total_cost(
            spot_price=spot_price,
            quantity_ton=quantity_ton,
            start_date=start_date,
            end_date=end_date,
            interest_rate=interest_rate,
            margin_rate=margin_rate,
            **fee_kwargs
        )
        
        # 计算期货收入（不含增值税）
        futures_revenue = futures_price * quantity_ton
        
        # 计算总成本（不含增值税的现货成本）
        total_cost_excl_vat = cost_result['summary']['total_cost'] - cost_result['cost_breakdown']['vat_amount']
        
        # 计算利润
        profit = futures_revenue - total_cost_excl_vat
        profit_per_ton = profit / quantity_ton
        
        # 判断是否能套利
        can_arbitrage = profit > 0
        profit_rate = (profit / (spot_price * quantity_ton)) * 100 if spot_price > 0 else 0
        
        return {
            **cost_result,
            "arbitrage": {
                "futures_price": futures_price,
                "futures_revenue": futures_revenue,
                "total_cost_excl_vat": total_cost_excl_vat,
                "profit": profit,
                "profit_per_ton": profit_per_ton,
                "profit_rate": profit_rate,
                "can_arbitrage": can_arbitrage,
                "break_even_futures_price": cost_result['summary']['break_even_price']
            }
        }
    
    def print_cost_report(self, result: Dict[str, any]):
        """打印成本报告"""
        print("=" * 80)
        print("锡（Sn）期现交割成本测算报告")
        print("=" * 80)
        
        # 输入参数
        print("\n【输入参数】")
        input_params = result["input"]
        print(f"  现货价格: {input_params['spot_price']:,.2f} 元/吨")
        print(f"  数量: {input_params['quantity_ton']:,.2f} 吨")
        print(f"  持有天数: {input_params['holding_days']} 天")
        print(f"  资金利率: {input_params['interest_rate']*100:.2f}% (年化)")
        
        # 成本明细
        print("\n【成本明细】")
        breakdown = result["cost_breakdown"]
        
        print(f"\n1. 现货买入成本:")
        print(f"   现货基价: {breakdown['spot_cost_base']:,.2f} 元")
        print(f"   增值税 (13%): {breakdown['vat_amount']:,.2f} 元")
        print(f"   小计: {breakdown['spot_cost_with_vat']:,.2f} 元")
        
        print(f"\n2. 交割杂费:")
        misc = breakdown["misc_fees"]
        print(f"   入库费: {misc['inbound_fee']:,.2f} 元")
        print(f"   出库费: {misc['outbound_fee']:,.2f} 元")
        print(f"   打包费: {misc['packing_fee']:,.2f} 元")
        print(f"   过户费: {misc['transfer_fee']:,.2f} 元")
        print(f"   交割手续费: {misc['delivery_fee']:,.2f} 元")
        print(f"   小计: {misc['total_misc_fees']:,.2f} 元")
        
        print(f"\n3. 仓储成本:")
        print(f"   仓储费: {breakdown['storage_cost']:,.2f} 元")
        print(f"   (费率: {self.storage_fee_per_ton_per_day} 元/吨·天)")
        
        print(f"\n4. 资金成本:")
        print(f"   资金利息: {breakdown['capital_cost']:,.2f} 元")
        
        # 汇总
        print("\n【成本汇总】")
        summary = result["summary"]
        print(f"  总成本: {summary['total_cost']:,.2f} 元")
        print(f"  单位成本: {summary['cost_per_ton']:,.2f} 元/吨")
        
        # 盈亏平衡点
        print("\n【盈亏平衡分析】")
        print(f"  盈亏平衡点（期货价格）: {summary['break_even_price']:,.2f} 元/吨")
        print(f"  需要升水: {summary['premium_needed']:,.2f} 元/吨")
        print(f"  升水率: {summary['premium_needed']/result['input']['spot_price']*100:.2f}%")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    calculator = TinDeliveryCostCalculator()
    print("锡期现交割成本计算器已初始化")
