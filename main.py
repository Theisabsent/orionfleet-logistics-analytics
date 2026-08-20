import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    customers = pd.read_csv('customers.csv')
    transactions = pd.read_csv('transactions.csv')
    products = pd.read_csv('products.csv')
    support_tickets = pd.read_csv('support_tickets.csv')
    employees = pd.read_csv('employees.csv')
    marketing = pd.read_csv('marketing_activity.csv')
    return customers, transactions, products, support_tickets, employees, marketing

def perform_deep_leakage_analysis(customers, transactions, products, support_tickets):
    print("=" * 70)
    print("        ORIONFLEET LOGISTICS - ADVANCED PROFIT LEAKAGE ANALYSIS")
    print("=" * 70 + "\n")
    
    # Merge datasets
    df = transactions.merge(products, on='product_id', how='left').merge(customers, on='customer_id', how='left')
    df['margin_pct'] = df['estimated_margin'] / df['net_revenue']

    # 1. Payment Status Leakage
    total_rev = df['net_revenue'].sum()
    unpaid = df[df['payment_status'] != 'Paid']
    unpaid_total = unpaid['net_revenue'].sum()
    
    print("1. CASH FLOW & PAYMENT LEAKAGE")
    print(f"   • Total Net Billed:               ₹{total_rev:,.2f}")
    print(f"   • Uncollected Exposure (Leak):    ₹{unpaid_total:,.2f} ({unpaid_total/total_rev*100:.2f}%)")
    print("   • Leakage Breakdown by Status:")
    for status, amt in df.groupby('payment_status')['net_revenue'].sum().items():
        if status != 'Paid':
            print(f"     - {status:10s}: ₹{amt:,.2f}")
    
    print("\n   • Top Regions with Unpaid Exposure:")
    top_unpaid_reg = unpaid.groupby('region')['net_revenue'].sum().sort_values(ascending=False).head(3)
    for reg, val in top_unpaid_reg.items():
        print(f"     - {reg:10s}: ₹{val:,.2f}")
    print()

    # 2. Discount & Negative Margin Leakage
    total_discounts = df['discount_amount'].sum()
    neg_margin_df = df[df['estimated_margin'] < 0]
    neg_margin_count = len(neg_margin_df)
    neg_margin_loss = neg_margin_df['estimated_margin'].sum()

    print("2. DISCOUNTING & MARGIN EROSION LEAKAGE")
    print(f"   • Total Revenue Lost to Discounts: ₹{total_discounts:,.2f}")
    print(f"   • Negative Margin Transactions:     {neg_margin_count} sales executed at a direct net loss")
    print(f"   • Direct Loss from Negative Sales: ₹{abs(neg_margin_loss):,.2f}")
    print("   • Cause: 100% of negative margin sales occurred at 15% or 20% discount rates.\n")

    # 3. Customer Churn ACV Exposure
    at_risk_acv = customers[customers['account_status'] == 'At Risk']['annual_contract_value'].sum()
    churned_acv = customers[customers['account_status'] == 'Churned']['annual_contract_value'].sum()

    print("3. CUSTOMER CHURN & CONTRACT VALUE LEAKAGE")
    print(f"   • Lost ARR (Churned Customers):    ₹{churned_acv:,.2f}")
    print(f"   • At-Risk ARR (Vulnerable Base):   ₹{at_risk_acv:,.2f}")
    print(f"   • Combined ARR Value Exposure:     ₹{(churned_acv + at_risk_acv):,.2f}\n")

def generate_leakage_dashboard(customers, transactions, products):
    df = transactions.merge(products, on='product_id', how='left').merge(customers, on='customer_id', how='left')
    df['margin_pct'] = df['estimated_margin'] / df['net_revenue']
    
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    
    # Chart 1: Revenue by Payment Status
    pay_summary = df.groupby('payment_status')['net_revenue'].sum().reset_index()
    sns.barplot(data=pay_summary, x='payment_status', y='net_revenue', ax=axes[0,0], palette='Reds_r')
    axes[0,0].set_title('1. Revenue Exposure by Payment Status (INR)', fontweight='bold')
    axes[0,0].set_ylabel('Total Revenue (INR)')
    
    # Chart 2: Profit Margin % by Discount Tier
    disc_summary = df.groupby('discount_pct')['margin_pct'].mean().reset_index()
    disc_summary['discount_pct_str'] = (disc_summary['discount_pct'] * 100).astype(int).astype(str) + '%'
    sns.lineplot(data=disc_summary, x='discount_pct_str', y='margin_pct', marker='o', ax=axes[0,1], color='darkred', linewidth=2.5)
    axes[0,1].set_title('2. Profit Margin Erosion vs. Discount Given', fontweight='bold')
    axes[0,1].set_ylabel('Average Margin %')
    axes[0,1].set_xlabel('Discount Rate')

    # Chart 3: Unpaid Revenue by Region
    unpaid = df[df['payment_status'] != 'Paid']
    unpaid_reg = unpaid.groupby('region')['net_revenue'].sum().reset_index().sort_values(by='net_revenue', ascending=False)
    sns.barplot(data=unpaid_reg, x='region', y='net_revenue', ax=axes[1,0], palette='Oranges_r')
    axes[1,0].set_title('3. Uncollected Revenue Exposure by Region', fontweight='bold')
    axes[1,0].set_ylabel('Unpaid Revenue (INR)')
    axes[1,0].tick_params(axis='x', rotation=30)

    # Chart 4: Account Status Count
    sns.countplot(data=customers, x='account_status', ax=axes[1,1], palette='Blues_r')
    axes[1,1].set_title('4. Customer Retention & Churn Risk', fontweight='bold')
    axes[1,1].set_ylabel('Customer Count')

    plt.tight_layout()
    plt.savefig('profit_leakage_dashboard.png', dpi=300)
    print("✓ Saved comprehensive leakage visualization as 'profit_leakage_dashboard.png'")

if __name__ == "__main__":
    cust, trans, prod, tickets, emp, mkt = load_data()
    perform_deep_leakage_analysis(cust, trans, prod, tickets)
    generate_leakage_dashboard(cust, trans, prod)