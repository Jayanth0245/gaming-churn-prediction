#Installing libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Plot styling
sns.set_theme(style="darkgrid")
plt.rcParams["figure.figsize"] = (10, 5)

#Loading Data
df = pd.read_csv("gaming_master.csv")

#First Look
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nColumn types:")
print(df.dtypes)
print("\nMissing values:")
print(df.isnull().sum())

#Basic statistics
print("=" * 50)
print("DATASET OVERVIEW")
print("=" * 50)

print(f"Total players: {len(df)}")
print(f"Churned players: {df['churned'].sum()}")
print(f"Churn rate: {df['churned'].mean()*100:.1f}%")
print(f"Average age: {df['age'].mean():.1f}")
print(f"Average sessions: {df['total_sessions'].mean():.1f}")
print(f"Average playtime: {df['total_playtime_mins'].mean():.1f} mins")
print(f"Average spending: ${df['total_spent_usd'].mean():.2f}")


#Comparing Churned VS Loyal players
print("\n" + "=" * 50)
print("CHURNED vs LOYAL PLAYERS")
print("=" * 50)

churn_summary = df.groupby('churned')[['total_sessions','avg_session_mins','total_playtime_mins','total_spent_usd','max_level']].mean().round(1)

churn_summary.index = ['Loyal Players', 'Churned Players']
print(churn_summary)


#Visualize Churn Distribution
fig, axes = plt.subplots(1,2, figsize=(12, 5))
fig.suptitle("Player Churn Overview", fontsize=16, fontweight='bold')

#Chart 1: Count of Churned vs Loyal
churn_counts = df['churned'].value_counts()
axes[0].bar(['Loyal Players', 'Churned Players'], churn_counts.values,color=['#2ecc71', '#e74c3c'])
axes[0].set_title("Churned vs Loyal Players")
axes[0].set_ylabel("Number of Players")

for i, v in enumerate(churn_counts.values):
    axes[0].text(i, v + 5, str(v), ha='center', fontweight='bold')

#Chart 2: Pie chart of churn percentage
axes[1].pie(churn_counts.values, labels=['Loyal Players', 'Churned Players'], colors=['#2ecc71', '#e74c3c'], autopct='%1.1f%%', startangle=90)
axes[1].set_title("Churn Rate Breakdown")
plt.tight_layout()
plt.savefig("chart1_churn_overview.png", dpi=150, bbox_inches='tight')
plt.show()
print("✅Chart 1 saved!")


#Analyzing Player Behavior
fig, axes = plt.subplots(1, 3, figsize=(16,5))
fig.suptitle("Player Behavior: Churned vs Loyal", fontsize = 16, fontweight = 'bold')

#Chart 1: Total Sessions
sns.boxplot(data=df, x = 'churned', y = 'total_sessions', palette = ['#2ecc71', '#e74c3c'], ax = axes[0])
axes[0].set_title("Total Sessions")
axes[0].set_xlabel("0 = Loyal | 1 = Churned")
axes[0].set_ylabel("Number of Sessions")

#Chart 2: Total Playtime
sns.boxplot(data=df, x = 'churned', y = 'total_playtime_mins', palette = ['#2ecc71', '#e74c3c'], ax = axes[1])
axes[1].set_title("Total Playtime (mins)")
axes[1].set_xlabel("0 = Loyal | 1 = Churned")
axes[1].set_ylabel("Total Minutes Played")

#Chart 3: Max Level Reached
sns.boxplot(data=df, x = 'churned', y = 'max_level', palette = ['#2ecc71', '#e74c3c'], ax = axes[2])
axes[2].set_title("Max Level Reached")
axes[2].set_xlabel("0 = Loyal | 1 = Churned")
axes[2].set_ylabel("Highest Level")

plt.tight_layout()
plt.savefig("chart2_player_behavior.png", dpi = 150, bbox_inches = 'tight')
plt.show()
print("✅Chart 2 saved!")


#Analyzing Spending Patterns
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Spending Patterns: Churned vs Loyal", fontsize=16, fontweight='bold')

#Chart 1 - Total spent:
sns.boxplot(data=df, x = 'churned', y = 'total_spent_usd', palette = ['#2ecc71', '#e74c3c'], ax = axes[0])
axes[0].set_title("Total Money Spent")
axes[0].set_xlabel("0 = Loyal | 1 = Churned")
axes[0].set_ylabel("Total Spent (USD)")

#Chart 2 - Number of purchases:
sns.boxplot(data = df, x = 'churned', y = 'num_purchases', palette = ['#2ecc71', '#e74c3c'], ax = axes[1])
axes[1].set_title("Number of Purchases")
axes[1].set_xlabel("0 = Loyal | 1 = Churned")
axes[1].set_ylabel("Number of Purchases")

plt.tight_layout()
plt.savefig("chart3_spending_patterns.png", dpi = 150, bbox_inches = 'tight')
plt.show()
print("✅Chart 3 saved!")


#Churn by Country, Device & Account type
fig, axes = plt.subplots(1, 3, figsize=(16,5))
fig.suptitle("Churn Rate by Player Segment", fontsize=16, fontweight='bold')

#Calculating Churn rate
country_churn = df.groupby('country')['churned'].mean()*100
device_churn = df.groupby('device')['churned'].mean()*100
account_churn = df.groupby('account_type')['churned'].mean()*100

#Chart 1 - Churn by Country:
country_churn.sort_values(ascending = False).plot(
    kind = 'bar',
    ax = axes[0],
    color = '#3498db',
    edgecolor = 'black')
axes[0].set_title("Churn rate by Country")
axes[0].set_ylabel("Churn Rate (%)")
axes[0].set_xlabel("")
axes[0].tick_params(axis = 'x', rotation = 45)

#Chart 2 - Churn by Device:
device_churn.sort_values(ascending = False).plot(
    kind = 'bar',
    ax = axes[1],
    color = '#9b59b6',
    edgecolor = 'black')
axes[1].set_title("Churn rate by Device")
axes[1].set_ylabel("Churn Rate (%)")
axes[1].set_xlabel("")
axes[1].tick_params(axis = 'x', rotation = 0)

#Chart 3 - Churn by Account Type:
account_churn.sort_values(ascending = False).plot(
    kind = 'bar',
    ax = axes[2],
    color = '#e67e22',
    edgecolor = 'black')
axes[2].set_title("Churn rate by Account Type")
axes[2].set_ylabel("Churn Rate (%)")
axes[2].set_xlabel("")
axes[2].tick_params(axis = 'x', rotation = 0)

plt.tight_layout()
plt.savefig("chart4_churn_by_segment.png", dpi = 150, bbox_inches = 'tight')
plt.show()
print("✅Chart 4 saved")


#Correlation Heatmap
fig, ax = plt.subplots(figsize=(10, 8))
numeric_cols = ['age', 'total_sessions', 'avg_session_mins', 'total_playtime_mins', 'max_level', 'num_purchases', 'total_spent_usd', 'churned']
correlation_matrix = df[numeric_cols].corr()
sns.heatmap(correlation_matrix, annot = True, fmt = '.2f', cmap = 'RdBu_r', center = 0, ax = ax, linewidths = 0.5)
ax.set_title("Feature Correlation Heatmap", fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig("chart5_correlation_heatmap.png", dpi=150, bbox_inches='tight')
plt.show()
print("✅Chart 5 saved!")
