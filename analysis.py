import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))

# Pull data from FRED
print("Fetching data from FRED...")
imports = fred.get_series('IMPCH')
exports = fred.get_series('EXPCH')
balance = fred.get_series('BOPGSTB')

# Convert to DataFrames
df = pd.DataFrame({
    'Imports from China': imports,
    'Exports to China': exports,
}, index=imports.index)
df = df[df.index >= '2000-01-01']

# Tariff event dates and labels
events = {
    "July '18": '2018-07-01',
    "Sept '19": '2019-09-01',
    "Jan '25": '2025-01-01',
}

# Plot
fig, ax = plt.subplots(figsize=(14, 12))
fig.canvas.manager.set_window_title('U.S.-China Trade Policy Analysis 21st Century')

ax.plot(df.index, df['Imports from China'], label='U.S. Imports from China', color='tomato', linewidth=2)
ax.plot(df.index, df['Exports to China'], label='U.S. Exports to China', color='steelblue', linewidth=2)

# Add tariff event lines and reveal the quantitative impact (events loop)
ax.autoscale()
v_offsets = [0.13, 0.15, 0.17]
for i, (label, date) in enumerate(events.items()):
    ts = pd.Timestamp(date)
    ax.axvline(ts, color='gray', linestyle='--', linewidth=1.2)
    before = df.loc[ts - pd.DateOffset(months=3):ts]['Imports from China'].mean()
    after = df.loc[ts:ts + pd.DateOffset(months=3)]['Imports from China'].mean()
    pct = ((after - before) / before) * 100
    y_pos = ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * v_offsets[i]
    ax.text(ts, y_pos, f"{label}: Chinese Imports {pct:+.1f}%", fontsize=7, color='gray', ha='center', va='top', clip_on=False)

# Formatting
ax.set_title('U.S.-China Trade Policy Analysis In The 21st Century', fontsize=16, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Value (Millions of USD)')
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
plt.xticks(rotation=45)

plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig('U.S.-China_Trade_Policy_Analysis_21st_Century.png', dpi=150)
print("Chart saved as U.S.-China_Trade_Policy_Analysis_21st_Century.png")
plt.show(block=False)
plt.pause(0.1)

# Before/after table
print("\n--- Before/After Tariff Analysis ---")
for label, date in events.items():
    ts = pd.Timestamp(date)
    before = df.loc[ts - pd.DateOffset(months=12):ts]['Imports from China'].mean()
    after = df.loc[ts:ts + pd.DateOffset(months=12)]['Imports from China'].mean()
    change = after - before
    print(f"\n{label.replace(chr(10), ' ')}")
    print(f"  Avg imports 12mo before: ${before:,.0f}M")
    print(f"  Avg imports 12mo after:  ${after:,.0f}M")
    print(f"  Change: ${change:,.0f}M")

    # --- CHART 2: Trade Diversion ---
print("Fetching trade diversion data...")
imports_vietnam = fred.get_series('IMP5520')
imports_mexico = fred.get_series('IMPMX')

# Build new dataframe from 2000 onward
df2 = pd.DataFrame({
    'China': imports,
    'Vietnam': imports_vietnam,
    'Mexico': imports_mexico,
}, index=imports.index)
df2 = df2[df2.index >= '2000-01-01']

# Plot
fig2, ax2 = plt.subplots(figsize=(14, 9))
fig2.canvas.manager.set_window_title('Trade Diversion Analysis')

ax2.plot(df2.index, df2['China'], label='Imports from China', color='tomato', linewidth=2)
ax2.plot(df2.index, df2['Vietnam'], label='Imports from Vietnam', color='seagreen', linewidth=2)
ax2.plot(df2.index, df2['Mexico'], label='Imports from Mexico', color='steelblue', linewidth=2)

ax2.autoscale()
fig2.canvas.draw()
y_min = ax2.get_ylim()[0]
y_max = ax2.get_ylim()[1]
y_range = y_max - y_min
v_offsets = [0.12, 0.12, 0.12]
for i, (label, date) in enumerate(events.items()):
    ts = pd.Timestamp(date)
    ax2.axvline(ts, color='gray', linestyle='--', linewidth=1.2)
    y_pos = y_min - y_range * v_offsets[i]
    ax2.text(ts, y_pos, label, fontsize=7, color='gray', ha='center', va='top', clip_on=False)
ax2.set_title('Trade Diversion: Did Supply Chains Shift to Vietnam & Mexico?', fontsize=16, fontweight='bold')
ax2.set_xlabel('Date')
ax2.set_ylabel('Value (Millions of USD)')
ax2.legend()
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))
plt.xticks(rotation=45)

# Build table data
table_rows = []
col_labels = ["Shock", "Chinese Imports", "Vietnamese Imports", "Mexican Imports"]
for label, date in events.items():
    ts = pd.Timestamp(date)
    row = [label]
    for country in ['China', 'Vietnam', 'Mexico']:
        before = df2.loc[ts - pd.DateOffset(months=3):ts][country].mean()
        after = df2.loc[ts:ts + pd.DateOffset(months=3)][country].mean()
        pct = ((after - before) / before) * 100
        row.append(f"{pct:+.1f}%")
    table_rows.append(row)

table = plt.table(
    cellText=table_rows,
    colLabels=col_labels,
    cellLoc='center',
    loc='bottom',
    bbox=[0.0, -0.42, 1.0, 0.28]
)
table.auto_set_font_size(False)
table.set_fontsize(8)

# Color the header row
for j in range(4):
    table[0, j].set_facecolor('#2c2c2c')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Color code the data cells by country
country_colors = ['#ffd6d6', '#d6f0e0', '#d6e8f7']
for i in range(1, 4):
    table[i, 0].set_facecolor('#f2f2f2')
    for j in range(1, 4):
        table[i, j].set_facecolor(country_colors[j-1])

plt.tight_layout()
plt.subplots_adjust(bottom=0.35)
plt.savefig('trade_diversion_chart.png', dpi=150, bbox_inches='tight')
print("Chart 2 saved as trade_diversion_chart.png")
plt.show(block=False)
plt.pause(0.1)

# --- CHART 3: Price Effect ---
print("Fetching import price data...")
import_prices = fred.get_series('IR')

# Build dataframe from 2000 onward
df3 = pd.DataFrame({
    'Import Price Index': import_prices,
}, index=import_prices.index)
df3 = df3[df3.index >= '2000-01-01']

# Plot with two y-axes (volume and price are different scales)
fig3, ax3 = plt.subplots(figsize=(14, 9))
fig3.canvas.manager.set_window_title('Import Price Effect Analysis')

ax3_twin = ax3.twinx()

ax3.plot(df2.index, df2['China'], label='Import Volume (China)', color='tomato', linewidth=2)
ax3_twin.plot(df3.index, df3['Import Price Index'], label='Import Price Index', color='darkorange', linewidth=2, linestyle='dashed')

for label, date in events.items():
    ts = pd.Timestamp(date)
    ax3.axvline(ts, color='gray', linestyle='--', linewidth=1.2)

ax3.set_title('Import Volume vs. Import Prices: Did Consumers Pay More?', fontsize=16, fontweight='bold')
ax3.set_xlabel('Date')
ax3.set_ylabel('Import Volume (Millions of USD)', color='tomato')
ax3_twin.set_ylabel('Import Price Index', color='darkorange')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax3.xaxis.set_major_locator(mdates.YearLocator(2))
plt.xticks(rotation=45)

lines1, labels1 = ax3.get_legend_handles_labels()
lines2, labels2 = ax3_twin.get_legend_handles_labels()
ax3.legend(lines1 + lines2, labels1 + labels2)

# Build table data
table_rows = []
col_labels = ["Shock", "Import Volume Change", "Import Price Change"]
for label, date in events.items():
    ts = pd.Timestamp(date)
    # Volume pct change
    before_vol = df2.loc[ts - pd.DateOffset(months=3):ts]['China'].mean()
    after_vol = df2.loc[ts:ts + pd.DateOffset(months=3)]['China'].mean()
    pct_vol = ((after_vol - before_vol) / before_vol) * 100
    # Price pct change
    before_price = df3.loc[ts - pd.DateOffset(months=3):ts]['Import Price Index'].mean()
    after_price = df3.loc[ts:ts + pd.DateOffset(months=3)]['Import Price Index'].mean()
    pct_price = ((after_price - before_price) / before_price) * 100
    table_rows.append([label, f"{pct_vol:+.1f}%", f"{pct_price:+.1f}%"])

table3 = plt.table(
    cellText=table_rows,
    colLabels=col_labels,
    cellLoc='center',
    loc='bottom',
    bbox=[0.0, -0.38, 1.0, 0.24]
)
table3.auto_set_font_size(False)
table3.set_fontsize(8)

# Header row styling
for j in range(3):
    table3[0, j].set_facecolor('#2c2c2c')
    table3[0, j].set_text_props(color='white', fontweight='bold')

# Color code volume and price columns
for i in range(1, 4):
    table3[i, 0].set_facecolor('#f2f2f2')
    table3[i, 1].set_facecolor('#ffd6d6')
    table3[i, 2].set_facecolor('#fde8c8')

plt.tight_layout()
plt.subplots_adjust(bottom=0.32)
plt.savefig('price_effect_chart.png', dpi=150, bbox_inches='tight')
print("Chart 3 saved as price_effect_chart.png")
plt.show(block=False)
plt.pause(0.1)

# --- CHART 4: U.S. Consumer Spending - Imports vs Domestic ---
print("Fetching consumption data...")
pce_total = fred.get_series('PCE')
total_imports = fred.get_series('BOPGSTB')

df4 = pd.DataFrame({
    'Total Imports': total_imports,
    'Domestic Consumption (PCE)': pce_total,
}, index=pce_total.index).dropna()
df4 = df4[df4.index >= '2000-01-01']

# Calculate imports as share of total consumption
df4['Import Share of Consumption'] = (df4['Total Imports'].abs() / df4['Domestic Consumption (PCE)']) * 100

fig4, ax4 = plt.subplots(figsize=(14, 7))
fig4.canvas.manager.set_window_title('U.S. Consumer Spending: Imports vs Domestic')

ax4_twin = ax4.twinx()

ax4.plot(df4.index, df4['Domestic Consumption (PCE)'], label='Domestic Consumer Spending PCE', color='steelblue', linewidth=2)
ax4_twin.plot(df4.index, df4['Import Share of Consumption'], label='Relative Consumer Import Spending', color='tomato', linewidth=2, linestyle='dashed')

ax4.autoscale()
v_offsets = [0.13, 0.17, 0.21]
for i, (label, date) in enumerate(events.items()):
    ts = pd.Timestamp(date)
    ax4.axvline(ts, color='gray', linestyle='--', linewidth=1.2)
    before = df4.loc[ts - pd.DateOffset(months=3):ts]['Import Share of Consumption'].mean()
    after = df4.loc[ts:ts + pd.DateOffset(months=3)]['Import Share of Consumption'].mean()
    pct = ((after - before) / before) * 100
    y_pos = ax4.get_ylim()[0] - (ax4.get_ylim()[1] - ax4.get_ylim()[0]) * v_offsets[i]
    ax4.text(ts, y_pos, f"{label}: Relative Import Spending {pct:+.1f}%", fontsize=7, color='gray', ha='center', va='top', clip_on=False)

ax4.set_title('U.S. Consumer Spending: Domestic vs. Relative Import Spending', fontsize=16, fontweight='bold')
ax4.set_xlabel('Date')
ax4.set_ylabel('Domestic PCE (Billions of USD)', color='steelblue')
ax4_twin.set_ylabel('Imports as % of Total Consumption', color='tomato')
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax4.xaxis.set_major_locator(mdates.YearLocator(2))
plt.xticks(rotation=45)

lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4_twin.get_legend_handles_labels()
ax4.legend(lines1 + lines2, labels1 + labels2, loc='lower left')

plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig('consumption_chart.png', dpi=150)
print("Chart 4 saved as consumption_chart.png")
plt.show(block=False)
plt.pause(0.1)

#Close charts
input("Press 1 to close all charts...")