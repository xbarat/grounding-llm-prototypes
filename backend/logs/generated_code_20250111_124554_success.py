# Query: Create a bar chart of constructor points in 2023
# Generated at: 2025-01-11T12:45:54.761929
# Status: success
# Data Type: standings


# Constructor Standings Visualization
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os

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
plt.savefig(os.path.join('/Users/btsznh/giraffe/orbit-vi/backend/plots', f'constructor_standings_{timestamp}.png'), bbox_inches='tight', dpi=300)
plt.close()
