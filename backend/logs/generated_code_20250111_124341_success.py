# Query: Create a bar chart of constructor points in 2023
# Generated at: 2025-01-11T12:43:41.812017
# Status: success
# Data Type: standings


# Constructor Standings Visualization
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
sns.barplot(data=df.sort_values('points', ascending=False), 
            x='constructorName', 
            y='points',
            palette='viridis')
plt.title('Constructor Standings')
plt.xticks(rotation=45)
plt.tight_layout()

# Add value labels on top of bars
for i, v in enumerate(df['points']):
    plt.text(i, v, str(v), ha='center', va='bottom')

# Save the plot
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plt.savefig(f'plots/constructor_standings_{timestamp}.png', bbox_inches='tight', dpi=300)
plt.close()
