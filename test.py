import matplotlib.pyplot as plt
import numpy as np

# Configuration du style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
colors_sector = ['#1f77b4', '#ff7f0e']  # Bleu pour Public, Orange pour Privé
colors_levels = ['#2ca02c', '#1f77b4', '#d62728', '#9467bd']

# ==========================================
# 1. Graphique 1: Répartition globale (Public vs Privé)
# ==========================================
labels_global = ['Enseignement Public', 'Enseignement Privé']
counts_global = [2318463, 262445]

plt.figure(figsize=(7, 6))
plt.pie(counts_global, labels=labels_global, autopct='%1.1f%%', startangle=140, 
        colors=colors_sector, explode=(0.05, 0), shadow=True, textprops={'fontsize': 11})
plt.title('Répartition Globale des Élèves par Secteur (2025/2026)', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()


# ==========================================
# 2. Graphique 2: Comparaison Public vs Privé par Niveau
# ==========================================
levels = ['Enseignement Primaire', 'Collège & Lycée']
public_counts = [1152752, 1097279]
private_counts = [136422, 126023]

x = np.arange(len(levels))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 6))
rects1 = ax.bar(x - width/2, public_counts, width, label='Public', color='#1f77b4')
rects2 = ax.bar(x + width/2, private_counts, width, label='Privé', color='#ff7f0e')

ax.set_ylabel("Nombre d'Élèves", fontsize=12)
ax.set_title('Comparaison Élèves Public vs Privé par Niveau d\'Enseignement', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(levels, fontsize=11)
ax.legend(fontsize=11)

# Affichage des chiffres au-dessus des barres
ax.bar_label(rects1, padding=3, fmt='%d', fontsize=10)
ax.bar_label(rects2, padding=3, fmt='%d', fontsize=10)

plt.tight_layout()
plt.show()


# ==========================================
# 3. Graphique 3: Répartition détaillée du Secteur Public
# ==========================================
labels_public_breakdown = [
    'Année Préparatoire (55 873)', 
    'Primaire (1 152 752)', 
    'Collège & Lycée Général (1 097 279)', 
    'Collège Technique (12 559)'
]
counts_public_breakdown = [55873, 1152752, 1097279, 12559]

plt.figure(figsize=(8, 7))
wedges, texts, autotexts = plt.pie(counts_public_breakdown, labels=labels_public_breakdown, 
                                  autopct='%1.1f%%', startangle=90, colors=colors_levels, 
                                  pctdistance=0.85, textprops={'fontsize': 10})

# Transformation en Donut Chart
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title('Répartition des Élèves dans l\'Enseignement Public par Niveau', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()