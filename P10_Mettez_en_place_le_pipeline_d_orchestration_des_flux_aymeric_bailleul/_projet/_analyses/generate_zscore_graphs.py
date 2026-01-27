import matplotlib.pyplot as plt
import numpy as np

# Données BottleNeck
mu = 32.49      # Prix moyen
sigma = 27.81   # Écart-type
z_threshold = 2 # Seuil z-score
premium_threshold = mu + z_threshold * sigma  # 88.11€

# Créer figure avec un seul graphique
fig, ax = plt.subplots(figsize=(12, 7))

# ==========================================
# HISTOGRAMME DES PRIX
# ==========================================

# Simuler des prix basés sur les vraies stats (714 produits)
np.random.seed(42)
simulated_prices = np.random.normal(mu, sigma, 714)
simulated_prices = np.clip(simulated_prices, 5, 250)  # Prix réalistes entre 5€ et 250€

# Créer histogramme
counts, bins, patches = ax.hist(simulated_prices, bins=30, color='skyblue', 
                                edgecolor='black', alpha=0.7)

# Colorer les barres premium en rouge
for i, patch in enumerate(patches):
    if bins[i] >= premium_threshold:
        patch.set_facecolor('red')
        patch.set_alpha(0.8)

# Lignes verticales pour les seuils
ax.axvline(premium_threshold, color='red', linestyle='--', linewidth=2.5, 
           label=f'Seuil Premium (z=2) = {premium_threshold:.2f}€')
ax.axvline(mu, color='black', linestyle='--', linewidth=2, 
           label=f'Moyenne = {mu}€')

# Annotations
ax.text(premium_threshold + 5, max(counts)*0.85, 
        f'30 vins\nPREMIUM\n(z > 2)', 
        fontsize=13, color='red', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', linewidth=2))

ax.text(mu - 20, max(counts)*0.65, 
        f'684 vins\nORDINAIRES\n(z ≤ 2)', 
        fontsize=13, color='blue', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='blue', linewidth=2))

# Légendes et titres
ax.set_xlabel('Prix (€)', fontsize=14, fontweight='bold')
ax.set_ylabel('Nombre de vins', fontsize=14, fontweight='bold')
ax.set_title('Classification des Vins par Prix - Méthode du Z-Score\nCatalogue BottleNeck (714 produits)', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(loc='upper right', fontsize=12, framealpha=0.95)
ax.grid(True, alpha=0.3, axis='y', linestyle='--')

# Ajuster l'espacement
plt.tight_layout()

# Sauvegarder l'image haute résolution pour PowerPoint
plt.savefig('classification_zscore_bottleneck.png', dpi=300, bbox_inches='tight')
print("✅ Graphique sauvegardé : classification_zscore_bottleneck.png")
print(f"📊 Seuil Premium : {premium_threshold:.2f}€ (prix moyen + 2 écarts-types)")
print(f"📈 30 vins Premium | 684 vins Ordinaires")

# Afficher
plt.show()
