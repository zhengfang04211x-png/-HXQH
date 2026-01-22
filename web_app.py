#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
锡期现交割成本测算模型 - Web界面
使用Streamlit创建交互式网页应用
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from tin_delivery_cost_calculator import TinDeliveryCostCalculator

# 设置页面配置
st.set_page_config(
    page_title="锡期现交割成本测算",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .arbitrage-yes {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #c3e6cb;
    }
    .arbitrage-no {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #f5c6cb;
    }
    .cost-table {
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化计算器
# 注意：不使用缓存，确保每次都是新的实例，避免参数污染
calculator = TinDeliveryCostCalculator()

# 标题
st.markdown('<h1 class="main-header">📊 锡（Sn）期现交割成本测算模型</h1>', unsafe_allow_html=True)

# 侧边栏 - 参数设置
st.sidebar.header("⚙️ 参数设置")

# 基础参数
st.sidebar.subheader("基础参数")
spot_price = st.sidebar.number_input(
    "现货价格（元/吨）",
    min_value=0.0,
    value=403250.0,
    step=1000.0,
    format="%.2f",
    help="当前现货市场价格"
)

futures_price = st.sidebar.number_input(
    "期货价格（元/吨）",
    min_value=0.0,
    value=408290.0,
    step=1000.0,
    format="%.2f",
    help="期货合约价格"
)

delivery_price = st.sidebar.number_input(
    "交割价格（元/吨）",
    min_value=0.0,
    value=408290.0,
    step=1000.0,
    format="%.2f",
    help="实际交割价格（默认等于期货价格，可手动修改）"
)

quantity_ton = st.sidebar.number_input(
    "数量（吨）",
    min_value=0.1,
    value=10.0,
    step=0.5,
    format="%.2f",
    help="交割数量"
)

# 合约和日期选择
st.sidebar.subheader("合约和时间设置")

# 合约代码输入
contract_code = st.sidebar.text_input(
    "合约代码",
    value="sn2603",
    help="输入合约代码，如sn2603（会自动识别交割日为2026年3月15日）",
    placeholder="sn2603"
)

# 解析合约代码并计算相关日期
def calculate_contract_dates(contract_code):
    """根据合约代码计算相关日期"""
    if not contract_code:
        return None, None, None, None, None
    
    import re
    match = re.match(r'sn(\d{2})(\d{2})', contract_code.lower())
    if not match:
        return None, None, None, None, None
    
    year_str, month_str = match.groups()
    year = 2000 + int(year_str)
    month = int(month_str)
    
    if not (1 <= month <= 12):
        return None, None, None, None, None
    
    # 交割日期：合约月15日
    delivery_date = datetime(year, month, 15).date()
    
    # 合约挂牌日期：通常为交割月前一年左右，简化处理为交割月前11个月
    # 例如：sn2612 (2026年12月) -> 2026年1月22日左右
    # 这里简化为交割月前11个月的22日
    listing_year = year
    listing_month = month - 11
    if listing_month <= 0:
        listing_month += 12
        listing_year -= 1
    listing_date = datetime(listing_year, listing_month, 22).date()
    
    # 交割月前第一月的第一个交易日：交割月前一个月的1号
    month_before_year = year
    month_before_month = month - 1
    if month_before_month <= 0:
        month_before_month = 12
        month_before_year -= 1
    month_before_delivery_date = datetime(month_before_year, month_before_month, 1).date()
    
    # 交割月份第一个交易日：交割月的1号
    delivery_month_start_date = datetime(year, month, 1).date()
    
    # 最后交易日前二个交易日：交割日前2个工作日
    # 简化处理：交割日前2天（实际应该考虑工作日）
    two_days_before_last_date = delivery_date - timedelta(days=2)
    
    return delivery_date, listing_date, month_before_delivery_date, delivery_month_start_date, two_days_before_last_date

# 初始化session_state
if 'last_contract_code' not in st.session_state:
    st.session_state.last_contract_code = None

# 解析合约代码
delivery_date_default = None
listing_date_default = None
month_before_delivery_default = None
delivery_month_start_default = None
two_days_before_last_default = None

if contract_code:
    dates = calculate_contract_dates(contract_code)
    if dates[0]:
        delivery_date_default, listing_date_default, month_before_delivery_default, delivery_month_start_default, two_days_before_last_default = dates
        
        # 如果合约代码改变了，清除相关日期的session_state
        if st.session_state.last_contract_code != contract_code:
            # 清除日期相关的session_state
            if 'listing_date_value' in st.session_state:
                del st.session_state.listing_date_value
            if 'month_before_delivery_value' in st.session_state:
                del st.session_state.month_before_delivery_value
            if 'delivery_month_start_value' in st.session_state:
                del st.session_state.delivery_month_start_value
            if 'two_days_before_last_value' in st.session_state:
                del st.session_state.two_days_before_last_value
            
            st.session_state.last_contract_code = contract_code

# 日期选择
start_date = st.sidebar.date_input(
    "开始日期（买入现货日期）",
    value=datetime.now().date(),
    help="买入现货的日期"
)

delivery_date = st.sidebar.date_input(
    "交割日期",
    value=delivery_date_default if delivery_date_default else (datetime.now() + timedelta(days=30)).date(),
    help="合约交割日（一般为合约月15日，法定假日顺延，可手动修改）"
)

# 资金参数
st.sidebar.subheader("资金参数")
interest_rate_percent = st.sidebar.slider(
    "资金利率（年化）",
    min_value=0.0,
    max_value=20.0,
    value=5.0,
    step=0.1,
    format="%.1f%%",
    help="年化资金成本利率（同时用于现货和期货保证金）",
    key="interest_rate_slider"
)
# 转换为小数形式用于计算
interest_rate = interest_rate_percent / 100.0

enterprise_margin_addon = st.sidebar.number_input(
    "企业保证金加收比例",
    min_value=0.0,
    max_value=0.50,
    value=0.0,
    step=0.01,
    format="%.2f",
    help="企业保证金加收比例（如0.05表示5%）"
)

# 保证金比例时间点设置
st.sidebar.subheader("保证金比例时间点（可修改）")
with st.sidebar.expander("保证金比例设置"):
    # 保证金比例值
    rate_5_percent = st.number_input(
        "第一阶段保证金比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.1,
        format="%.1f",
        help="合约挂牌之日起的保证金比例",
        key="rate_5"
    ) / 100
    
    rate_10_percent = st.number_input(
        "第二阶段保证金比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        format="%.1f",
        help="交割月前第一月的第一个交易日起的保证金比例",
        key="rate_10"
    ) / 100
    
    rate_15_percent = st.number_input(
        "第三阶段保证金比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=0.1,
        format="%.1f",
        help="交割月份第一个交易日起的保证金比例",
        key="rate_15"
    ) / 100
    
    rate_20_percent = st.number_input(
        "第四阶段保证金比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=0.1,
        format="%.1f",
        help="最后交易日前二个交易日起的保证金比例",
        key="rate_20"
    ) / 100
    
    # 时间点设置（根据合约代码自动生成）
    # 使用动态key，当合约代码改变时，key也会改变，从而重置日期值
    listing_date_key = f"listing_date_{contract_code}"
    month_before_delivery_key = f"month_before_delivery_{contract_code}"
    delivery_month_start_key = f"delivery_month_start_{contract_code}"
    two_days_before_last_key = f"two_days_before_last_{contract_code}"
    
    listing_date = st.date_input(
        "合约挂牌日期",
        value=listing_date_default if listing_date_default else start_date,
        help="合约挂牌日期（根据合约代码自动生成，可手动修改）",
        key=listing_date_key
    )
    
    month_before_delivery_date = st.date_input(
        "交割月前第一月的第一个交易日",
        value=month_before_delivery_default if month_before_delivery_default else (delivery_date.replace(day=1) - timedelta(days=1)).replace(day=1),
        help="交割月前第一月的第一个交易日（根据合约代码自动生成，可手动修改）",
        key=month_before_delivery_key
    )
    
    delivery_month_start_date = st.date_input(
        "交割月份第一个交易日",
        value=delivery_month_start_default if delivery_month_start_default else delivery_date.replace(day=1),
        help="交割月份第一个交易日（根据合约代码自动生成，可手动修改）",
        key=delivery_month_start_key
    )
    
    two_days_before_last_date = st.date_input(
        "最后交易日前二个交易日",
        value=two_days_before_last_default if two_days_before_last_default else (delivery_date - timedelta(days=2)),
        help="最后交易日前二个交易日（根据合约代码自动生成，可手动修改）",
        key=two_days_before_last_key
    )

# 入库/出库方式选择
st.sidebar.subheader("入库/出库方式")

inbound_method = st.sidebar.selectbox(
    "入库方式",
    ["专用线", "非箱式车辆自送", "箱式车自送（包括集装箱车辆）"],
    help="选择入库方式"
)

outbound_method = st.sidebar.selectbox(
    "出库方式",
    ["专用线", "非箱式车辆自提", "箱式车辆自提（包括集装箱车辆）"],
    help="选择出库方式"
)

# 入库费用映射
inbound_fee_map = {
    "专用线": 35.0,
    "非箱式车辆自送": 30.0,
    "箱式车自送（包括集装箱车辆）": 40.0
}

# 出库费用映射
outbound_fee_map = {
    "专用线": 35.0,
    "非箱式车辆自提": 25.0,
    "箱式车辆自提（包括集装箱车辆）": 35.0
}

inbound_fee_per_ton = inbound_fee_map[inbound_method]
outbound_fee_per_ton = outbound_fee_map[outbound_method]

# 代办费用
st.sidebar.subheader("代办费用（可选）")
use_train_application = st.sidebar.checkbox("代办车皮申请", value=False, help="5元/吨")
use_transport = st.sidebar.checkbox("代办提运", value=False, help="2元/吨")

train_application_fee_per_ton = 5.0 if use_train_application else 0.0
transport_fee_per_ton = 2.0 if use_transport else 0.0

# 其他交割参数
st.sidebar.subheader("其他交割参数")
with st.sidebar.expander("查看/修改其他交割参数"):
    packing_fee = st.number_input(
        "打包费（元/吨）",
        min_value=0.0,
        value=calculator.packing_fee_per_ton,
        step=1.0,
        format="%.2f",
        key="packing_fee_input"
    )
    
    transfer_fee = st.number_input(
        "过户费（元/吨）",
        min_value=0.0,
        value=calculator.transfer_fee_per_ton,
        step=0.1,
        format="%.2f",
        key="transfer_fee_input"
    )
    
    delivery_fee = st.number_input(
        "交割手续费（元/吨）",
        min_value=0.0,
        value=calculator.delivery_fee_per_ton,
        step=0.1,
        format="%.2f",
        key="delivery_fee_input"
    )
    
    vat_rate = st.number_input(
        "增值税率",
        min_value=0.0,
        max_value=1.0,
        value=calculator.vat_rate,
        step=0.01,
        format="%.2f",
        help="增值税率（如0.13表示13%）",
        key="vat_rate_input"
    )
    
    storage_fee = st.number_input(
        "仓储费（元/吨·天）",
        min_value=0.0,
        value=calculator.storage_fee_per_ton_per_day,
        step=0.1,
        format="%.2f",
        key="storage_fee_input"
    )
    
    # 临时更新计算器参数
    calculator.packing_fee_per_ton = packing_fee
    calculator.transfer_fee_per_ton = transfer_fee
    calculator.delivery_fee_per_ton = delivery_fee
    calculator.vat_rate = vat_rate
    calculator.storage_fee_per_ton_per_day = storage_fee

# 计算动态保证金比例
margin_rate, margin_info = calculator.calculate_margin_rate(
    datetime.combine(start_date, datetime.min.time()),
    datetime.combine(delivery_date, datetime.min.time()),
    None,  # last_trading_date不再需要
    enterprise_margin_addon,
    datetime.combine(listing_date, datetime.min.time()),
    datetime.combine(month_before_delivery_date, datetime.min.time()),
    datetime.combine(delivery_month_start_date, datetime.min.time()),
    datetime.combine(two_days_before_last_date, datetime.min.time()),
    rate_5_percent,
    rate_10_percent,
    rate_15_percent,
    rate_20_percent
)

# 计算套利
try:
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(delivery_date, datetime.min.time())
    
    result = calculator.check_arbitrage(
        spot_price=spot_price,
        futures_price=futures_price,
        delivery_price=delivery_price,
        quantity_ton=quantity_ton,
        start_date=start_dt,
        end_date=end_dt,
        interest_rate=interest_rate,
        margin_rate=margin_rate,
        inbound_fee_per_ton=inbound_fee_per_ton,
        outbound_fee_per_ton=outbound_fee_per_ton,
        packing_fee_per_ton=packing_fee,
        transfer_fee_per_ton=transfer_fee,
        delivery_fee_per_ton=delivery_fee,
        train_application_fee_per_ton=train_application_fee_per_ton,
        transport_fee_per_ton=transport_fee_per_ton
    )
    
    holding_days = result['input']['holding_days']
    breakdown = result['cost_breakdown']
    misc = breakdown['misc_fees']
    
    # ========== 第一部分：每吨各项成本 ==========
    st.header("📊 第一部分：每吨各项成本")
    
    # 计算每吨成本
    spot_cost_base_per_ton = spot_price  # 现货基价
    # 增值税 = (交割价格 - 现货成本) × 增值税率
    vat_per_ton = (delivery_price - spot_price) * vat_rate if delivery_price > spot_price else 0
    spot_cost_per_ton = spot_price + vat_per_ton  # 现货成本（含增值税）
    
    # 交割杂费（每吨）
    inbound_fee_per_ton_calc = inbound_fee_per_ton
    outbound_fee_per_ton_calc = outbound_fee_per_ton
    packing_fee_per_ton_calc = packing_fee
    transfer_fee_per_ton_calc = transfer_fee
    delivery_fee_per_ton_calc = delivery_fee
    train_app_per_ton = train_application_fee_per_ton
    transport_per_ton = transport_fee_per_ton
    
    misc_fees_per_ton = (
        inbound_fee_per_ton_calc +
        outbound_fee_per_ton_calc +
        packing_fee_per_ton_calc +
        transfer_fee_per_ton_calc +
        delivery_fee_per_ton_calc +
        train_app_per_ton +
        transport_per_ton
    )
    
    # 仓储费（每吨）
    storage_cost_per_ton = storage_fee * holding_days
    
    # 资金成本（每吨）
    # 现货资金成本（每吨）
    spot_capital_amount_per_ton = spot_price * (1 + vat_rate)
    spot_interest_per_ton = spot_capital_amount_per_ton * (interest_rate / 365) * holding_days
    
    # 期货保证金资金成本（每吨）
    futures_capital_amount_per_ton = spot_price * margin_info['final_rate']
    futures_interest_per_ton = futures_capital_amount_per_ton * (interest_rate / 365) * holding_days
    
    # 总资金成本（每吨）
    total_interest_per_ton = spot_interest_per_ton + futures_interest_per_ton
    
    # 每吨总成本
    total_cost_per_ton = (
        spot_cost_per_ton +
        misc_fees_per_ton +
        storage_cost_per_ton +
        total_interest_per_ton
    )
    
    # 显示每吨成本明细表
    cost_per_ton_data = {
        "成本项": [
            "现货基价",
            "增值税",
            "现货成本小计（含税）",
            "入库费",
            "出库费",
            "打包费",
            "过户费",
            "交割手续费",
            "代办车皮申请" if train_app_per_ton > 0 else None,
            "代办提运" if transport_per_ton > 0 else None,
            "交割杂费小计",
            "仓储费",
            "现货资金成本",
            "期货保证金资金成本",
            "总资金成本",
            "**每吨总成本**"
        ],
        "金额（元/吨）": [
            spot_cost_base_per_ton,
            vat_per_ton,
            spot_cost_per_ton,
            inbound_fee_per_ton_calc,
            outbound_fee_per_ton_calc,
            packing_fee_per_ton_calc,
            transfer_fee_per_ton_calc,
            delivery_fee_per_ton_calc,
            train_app_per_ton if train_app_per_ton > 0 else None,
            transport_per_ton if transport_per_ton > 0 else None,
            misc_fees_per_ton,
            storage_cost_per_ton,
            spot_interest_per_ton,
            futures_interest_per_ton,
            total_interest_per_ton,
            total_cost_per_ton
        ]
    }
    
    # 过滤掉None值
    filtered_data = {
        "成本项": [item for item in cost_per_ton_data["成本项"] if item is not None],
        "金额（元/吨）": [val for val in cost_per_ton_data["金额（元/吨）"] if val is not None]
    }
    
    cost_per_ton_df = pd.DataFrame(filtered_data)
    cost_per_ton_df['金额（元/吨）'] = cost_per_ton_df['金额（元/吨）'].apply(lambda x: f"{x:,.2f}")
    
    st.dataframe(cost_per_ton_df, use_container_width=True, hide_index=True)
    
    # ========== 第二部分：资金需求 ==========
    st.header("💰 第二部分：资金需求")
    
    # 计算资金需求
    # 现货资金占用 = 现货成本 + 增值税
    spot_capital_total = breakdown['spot_cost_with_vat']  # 购买现货需要资金（含增值税）
    futures_margin_total = spot_price * quantity_ton * margin_info['final_rate']  # 购买期货需要资金（保证金）
    total_capital_needed = spot_capital_total + futures_margin_total  # 总资金需求
    
    capital_col1, capital_col2, capital_col3 = st.columns(3)
    
    with capital_col1:
        st.metric(
            "购买现货需要资金",
            f"¥{spot_capital_total:,.2f}",
            help="现货成本 + 增值税"
        )
        st.caption(f"现货基价: ¥{spot_price:,.2f}/吨")
        st.caption(f"数量: {quantity_ton:.2f} 吨")
        st.caption(f"增值税: ¥{breakdown['vat_amount']:,.2f}")
    
    with capital_col2:
        st.metric(
            "购买期货需要资金（保证金）",
            f"¥{futures_margin_total:,.2f}",
            help="现货价格 × 数量 × 保证金比例"
        )
        st.caption(f"保证金比例: {margin_info['final_rate']*100:.2f}%")
        st.caption(f"（平均: {margin_info['average_rate']*100:.2f}% + 企业加收: {enterprise_margin_addon*100:.2f}%）")
    
    with capital_col3:
        st.metric(
            "总资金需求",
            f"¥{total_capital_needed:,.2f}",
            help="现货资金 + 期货保证金"
        )
        st.caption("需要准备的总资金")
    
    # ========== 第三部分：按数量计算总成本 ==========
    st.header("📋 第三部分：按数量计算总成本")
    
    # 套利判断结果
    arbitrage_result = result['arbitrage']
    can_arbitrage = arbitrage_result['can_arbitrage']
    
    # 显示套利结果
    if can_arbitrage:
        st.markdown(f"""
        <div class="arbitrage-yes">
            <h2>✅ 可以套利！</h2>
            <p><strong>预期利润：</strong>¥{arbitrage_result['profit']:,.2f}（{arbitrage_result['profit_per_ton']:,.2f} 元/吨）</p>
            <p><strong>利润率：</strong>{arbitrage_result['profit_rate']:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="arbitrage-no">
            <h2>❌ 无法套利</h2>
            <p><strong>预期亏损：</strong>¥{abs(arbitrage_result['profit']):,.2f}（{abs(arbitrage_result['profit_per_ton']):,.2f} 元/吨）</p>
            <p><strong>需要期货价格达到：</strong>¥{arbitrage_result['break_even_futures_price']:,.2f}/吨 才能保本</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 总成本明细
    total_cost_data = {
        "成本项": [
            "现货成本（含税）",
            "交割杂费",
            "仓储费",
            "现货资金成本",
            "期货保证金资金成本",
            "总资金成本",
            "**总成本**"
        ],
        "金额（元）": [
            breakdown['spot_cost_with_vat'],
            breakdown['misc_fees']['total_misc_fees'],
            breakdown['storage_cost'],
            breakdown['spot_capital_cost'],
            breakdown['futures_capital_cost'],
            breakdown['capital_cost'],
            result['summary']['total_cost']
        ]
    }
    
    total_cost_df = pd.DataFrame(total_cost_data)
    total_cost_df['占比'] = (total_cost_df['金额（元）'] / result['summary']['total_cost'] * 100).round(2)
    total_cost_df['金额（元）'] = total_cost_df['金额（元）'].apply(lambda x: f"{x:,.2f}")
    total_cost_df['占比'] = total_cost_df['占比'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(total_cost_df, use_container_width=True, hide_index=True)
    
    # 交割杂费明细
    st.subheader("交割杂费明细")
    misc_items = []
    misc_values = []
    
    if misc['inbound_fee'] > 0:
        misc_items.append(f"入库费（{inbound_method}）")
        misc_values.append(misc['inbound_fee'])
    if misc['outbound_fee'] > 0:
        misc_items.append(f"出库费（{outbound_method}）")
        misc_values.append(misc['outbound_fee'])
    if misc['packing_fee'] > 0:
        misc_items.append("打包费")
        misc_values.append(misc['packing_fee'])
    if misc['transfer_fee'] > 0:
        misc_items.append("过户费")
        misc_values.append(misc['transfer_fee'])
    if misc['delivery_fee'] > 0:
        misc_items.append("交割手续费")
        misc_values.append(misc['delivery_fee'])
    if misc['train_application_fee'] > 0:
        misc_items.append("代办车皮申请")
        misc_values.append(misc['train_application_fee'])
    if misc['transport_fee'] > 0:
        misc_items.append("代办提运")
        misc_values.append(misc['transport_fee'])
    
    if misc_items:
        misc_df = pd.DataFrame({
            "费用项": misc_items,
            "金额（元）": [f"{v:,.2f}" for v in misc_values]
        })
        st.dataframe(misc_df, use_container_width=True, hide_index=True)
    
    # 关键指标
    st.subheader("关键指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "总成本",
            f"¥{result['summary']['total_cost']:,.2f}",
            help="期现套利总成本"
        )
    
    with col2:
        st.metric(
            "单位成本",
            f"¥{result['summary']['cost_per_ton']:,.2f}/吨",
            help="每吨成本"
        )
    
    with col3:
        st.metric(
            "期货收入",
            f"¥{arbitrage_result['futures_revenue']:,.2f}",
            help="期货交割收入"
        )
    
    with col4:
        delta_label = f"{arbitrage_result['profit_rate']:.2f}%"
        st.metric(
            "预期利润",
            f"¥{arbitrage_result['profit']:,.2f}",
            delta=delta_label if can_arbitrage else None,
            delta_color="normal" if can_arbitrage else "inverse",
            help="预期利润（期货收入 - 总成本）"
        )
    
    # 详细说明
    st.subheader("详细说明")
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown("### 成本构成说明")
        st.markdown(f"""
        - **现货成本（含税）**: ¥{breakdown['spot_cost_with_vat']:,.2f}
          - 现货基价: ¥{breakdown['spot_cost_base']:,.2f}
          - 增值税 ({vat_rate*100:.0f}%): ¥{breakdown['vat_amount']:,.2f}
          - 计算公式: (交割价格 {delivery_price:,.2f} - 现货价格 {spot_price:,.2f}) × {vat_rate*100:.0f}%
        
        - **交割杂费**: ¥{breakdown['misc_fees']['total_misc_fees']:,.2f}
          - 入库费: ¥{misc['inbound_fee']:,.2f}
          - 出库费: ¥{misc['outbound_fee']:,.2f}
          - 打包费: ¥{misc['packing_fee']:,.2f}
          - 过户费: ¥{misc['transfer_fee']:,.2f}
          - 交割手续费: ¥{misc['delivery_fee']:,.2f}
          {f"- 代办车皮申请: ¥{misc['train_application_fee']:,.2f}" if misc['train_application_fee'] > 0 else ""}
          {f"- 代办提运: ¥{misc['transport_fee']:,.2f}" if misc['transport_fee'] > 0 else ""}
        
        - **仓储费**: ¥{breakdown['storage_cost']:,.2f}
          - 费率: ¥{storage_fee:.2f}/吨·天 × {quantity_ton:.2f}吨 × {holding_days}天
        """)
    
    with detail_col2:
        st.markdown("### 资金成本说明")
        st.markdown(f"""
        - **现货资金成本**: ¥{breakdown['spot_capital_cost']:,.2f}
          - 资金占用: ¥{spot_capital_total:,.2f}
          - 利率: {interest_rate*100:.2f}% (年化)
          - 持有天数: {holding_days} 天
        
        - **期货保证金资金成本**: ¥{breakdown['futures_capital_cost']:,.2f}
          - 保证金占用: ¥{futures_margin_total:,.2f}
          - 保证金比例: {margin_info['final_rate']*100:.2f}%
          - 利率: {interest_rate*100:.2f}% (年化)
          - 持有天数: {holding_days} 天
        
        - **总资金成本**: ¥{breakdown['capital_cost']:,.2f}
        """)
        
        st.markdown("### 套利分析")
        st.markdown(f"""
        - **现货价格**: ¥{spot_price:,.2f}/吨
        - **期货价格**: ¥{futures_price:,.2f}/吨
        - **交割价格**: ¥{delivery_price:,.2f}/吨
        - **盈亏平衡点**: ¥{arbitrage_result['break_even_futures_price']:,.2f}/吨
        - **期货收入**: ¥{arbitrage_result['futures_revenue']:,.2f}
        - **总成本（不含税）**: ¥{arbitrage_result['total_cost_excl_vat']:,.2f}
        - **预期利润**: ¥{arbitrage_result['profit']:,.2f}
        - **利润率**: {arbitrage_result['profit_rate']:.2f}%
        """)
    
    # 保证金时间段明细
    if margin_info.get('periods'):
        st.subheader("保证金时间段明细")
        periods_data = []
        for period in margin_info['periods']:
            period_days = (period['end'] - period['start']).days
            periods_data.append({
                '时间段': period['description'],
                '开始日期': period['start'].strftime('%Y-%m-%d'),
                '结束日期': period['end'].strftime('%Y-%m-%d'),
                '天数': period_days,
                '保证金比例': f"{period['rate']*100:.1f}%"
            })
        periods_df = pd.DataFrame(periods_data)
        st.dataframe(periods_df, use_container_width=True, hide_index=True)
    
    # 时间信息
    st.subheader("时间信息")
    time_col1, time_col2, time_col3 = st.columns(3)
    
    with time_col1:
        st.metric("开始日期", start_date.strftime("%Y-%m-%d"))
    
    with time_col2:
        st.metric("交割日期", delivery_date.strftime("%Y-%m-%d"))
    
    with time_col3:
        st.metric("持有天数", f"{holding_days} 天")

except Exception as e:
    st.error(f"计算错误: {str(e)}")
    st.exception(e)

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "锡期现交割成本测算模型 | 基于多晶硅套利表逻辑适配"
    "</div>",
    unsafe_allow_html=True
)
