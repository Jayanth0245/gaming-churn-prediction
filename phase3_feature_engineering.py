import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

#plot styling
sns.set_theme(style="darkgrid")
plt.rcParams["figure.figsize"] = (10,5)

#loading data
df = pd.read_csv("gaming_master.csv")

print("Shape: ", df.shape)
print("/nColumns: ", df.columns.tolist())
print("/nFirst 3 rows: ")
print(df.head(3))

#Creating new behavioral features
print("=" * 50)
print("FEATURE ENGINEERING")
print("=" * 50)
#Feature 1:
today = datetime(2024, 1, 1)
df['join_date'] = pd.to_datetime(df['join_date'])
df['days_since_joined'] = (today - df['join_date']).dt.days
print("✅ Feature 1 created : days_since_joined")
print(df['days_since_joined'].describe())
#Feature 2:
df['playtime_per_session'] = ( df['total_playtime_mins'] / df['total_sessions']).round(1)
print("\n✅ Feature 2 created : playtime_per_session")
print(df['playtime_per_session'].describe())
#Feature 3:
df['purchase_rate'] = (df['num_purchases'] / df['total_sessions']).round(3)
print("\n✅ Feature 3 created : purchase_rate")
print(df['purchase_rate'].describe())
#Feature 4:
spending_threshold = df['total_spent_usd'].quantile(0.75)
df['is_high_spender'] = (df['total_spent_usd'] > spending_threshold).astype(int)
print(f"\n✅ Feature 4 created : is_high_spender")
print(f"  Threshold : ${spending_threshold:.2f}")
print(f"  High spenders : {df['is_high_spender'].sum()}")
#Feature 5:
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
engagement_features = df[['total_sessions', 'total_playtime_mins', 'max_level']].copy()
scaled = scaler.fit_transform(engagement_features)
df['engagement_score'] = scaled.mean(axis=1).round(3)
print(f"\n✅ Feature 5 created : engagement_score")
print(df['engagement_score'].describe())
#Checking new features
print("\nNew dataset shape:", df.shape)
print("\nNew features preview:")
print(df[['player_id', 'days_since_joined', 'playtime_per_session', 'purchase_rate', 'is_high_spender', 'engagement_score', 'churned']].head())

#Encoding Categorical Variables
print("=" *50)
print("ENCODING CATEGORICAL VARIABLES")
print("=" *50)
#Label encode account type
df['account_type_encoded'] = (df['account_type'].map({'Free': 0, 'Premium': 1}))
print("✅ Label encoded: account_type")
print(df['account_type_encoded'].value_counts())
#One hot encode device &country
df = pd.get_dummies(df, columns=['device', 'country'], prefix=['device', 'country'], drop_first=True, dtype=int)
print("\n✅ One hot encoded: device, country")
print("New shape:", df.shape)
print("\nNew columns added:")
new_cols = [c for c in df.columns if 'device_' in c or 'country_' in c]
print(new_cols)

#Scaling Numerical Numbers:
print("=" *50)
print("SCALING NUMERICAL FEATURES")
print("=" *50)

cols_to_scale = ['age', 'total_sessions', 'avg_session_mins', 'total_playtime_mins', 'max_level', 'num_purchases', 'total_spent_usd', 'days_since_joined', 'playtime_per_session', 'purchase_rate', 'engagement_score']
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

print("✅Scaling complete!")
print("\nBefore scaling - total_playtime_mins:")
print(df['total_playtime_mins'].describe().round(1))
print("\nAfter scaling - total_playtime_mins:")
print(df_scaled['total_playtime_mins'].describe().round(3))
print("\nScaled sataset shape:", df_scaled.shape)

#Feature selection:
print("=" *50)
print("FEATURE SELECTION")
print("=" *50)

#Method 1 - Correlation with Churned:
cols_for_correlation = [c for c in df_scaled.columns if c not in ['player_id', 'churned', 'join_date', 'account_type', 'username']]
correlations = df_scaled[cols_for_correlation].corrwith(df_scaled['churned'])
correlations = correlations.abs().sort_values(ascending=False)
print("Top 10 features correlated with churn:")
print(correlations.head(10).round(3))

plt.figure(figsize=(10,6))
correlations.head(10).plot(kind='barh', color='#3498db', edgecolor='black')
plt.title("Top 10 Features Correlated with Churn", fontsize=14, fontweight='bold')
plt.xlabel("Absolute Correlation")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("chart6_feature_importance.png", dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 6 saved!")

#Method 2 - SelectKBest:
from sklearn.feature_selection import SelectKBest, f_classif
X =df_scaled[cols_for_correlation]
y = df_scaled['churned']
selector = SelectKBest(f_classif, k=10)
selector.fit(X, y)
feature_scores = pd.DataFrame({
    'feature': X.columns,
    'score': selector.scores_
}).sort_values('score', ascending=False)
print("\nSelectKBest Top 10 Features:")
print(feature_scores.head(10).round(2))

top_features = feature_scores.head(10)['feature'].tolist()
top_features.append('churned')
df_final = df_scaled[top_features].copy()
print("\n✅Final Features Selected!")
print("Final dataset shape:", df_final.shape)
print("Features:", top_features)

#Saving:
print("=" *50)
print("SAVING FINAL DATASET")
print("=" *50)

df_final.to_csv("gaming_final_features.csv", index=False)
df_scaled.to_csv("gaming_engineered.csv", index=False)
print("✅ gaming_final_features.csv saved!")
print("✅ gaming_engineered.csv saved!")
print("\nFinal dataset shape: {df_final.shape}")
print("\nFeatures going into ML model:")
for i, col in enumerate(df_final.columns, 1):
    print(f"   {i}.{col}")
