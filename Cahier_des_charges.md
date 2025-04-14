
# **Cahier des Charges : Application de Matching Factures-Relevé Bancaire**

## **1. Description Générale**

### **1.1 Contexte**
La gestion des factures et des relevés bancaires peut être chronophage et sujette aux erreurs humaines. 
Aujourd'hui, il est crucial d'automatiser ce processus pour réduire les erreurs et optimiser le temps de traitement. 
Ce projet vise à développer une application web permettant de faire correspondre efficacement des factures scannées (JPG, JPEG, PNG) avec des transactions bancaires extraites de relevés au format CSV.

---

## **2. Objectifs du Projet**
Développer une application automatisée pour :
- Faire correspondre des factures avec les transactions bancaires.
- Optimiser le temps de traitement.
- Réduire les erreurs humaines.

---

## **3. Portée et Activités du Projet**

### **3.1 Activités majeures**

| Activité                        | Description                                                        |
|----------------------------------|--------------------------------------------------------------------|
| **Analyse automatique des factures** | Extraction et traitement des factures numériques (JPG, JPEG, PNG). |
| **Intégration des relevés bancaires** | Prise en charge des fichiers CSV pour une analyse des transactions bancaires. |
| **Matching intelligent**           | Algorithme de rapprochement des transactions bancaires et des factures avec un score de confiance. |
| **Visualisation des résultats**   | Interface pour afficher les correspondances et les statistiques. |
| **Structure du projet**           | Organisation en modules avec composants UI, services API et modèles de données. |


---

## **4. Fonctionnalités et spécifications Techniques**

### **4.1 Technologies Utilisées**
- **Frontend :** Streamlit
- **Backend :** Python
- **Pixtral :** API Pixtral (powered by Mistral)
- **Base de données :** Stockage en session

### **4.2 Le plus du projet**
- **Panel de navigation:**
	- **Home :** Page principale de matching
	- **Benchmark:** Pour retester les métrics + Matrice de confusion + Interprétation
	- **Pricing :** Calculatrice en ligne
	- **About :** Guide utilisateur

### **4.3 Architecture du Projet**

```
📁 Structure du Projet
├── src/
│   ├── client
│   │   ├── config
│   │   └── modules
│   │       ├── about
│   │       │   └── components
│   │       ├── benchmark
│   │       │   └── components
│   │       ├── home
│   │       │   ├── components
│   │       │   └── state
│   │       └── pricing
│   │           └── components
│   └── server/                  # Modules liés au backend / logique métier
│       ├── api
│       ├── config
│       ├── prompts
│       ├── config.py
│       ├── delete.py
│       ├── extract_data.py
│       ├── matching.py
│       └── main.py
│
├── storage                   	  # Pour la persistance des données en cas de refresh
│
├── sample
│   └── images
│   └── relevés
├── app.py                       # Script principal / Point d'entrée de l'application Streamlit
├── requirements.txt 
└── README.md                    # Ce fichier d'information

```

### **5. Contraintes Techniques**
- Temps de réponse < 5 secondes par facture
- Précision du matching > 90%
- Support des formats d'image courants
- Gestion des erreurs et des timeouts

---

## **6. Sécurité et Performance**

### **6.1 Sécurité**
- Validation des fichiers pour s'assurer de leur conformité.
- Protection des données sensibles.
- Gestion sécurisée des sessions utilisateur.

### **6.2 Performance**
- Traitement asynchrone pour éviter le blocage de l'interface.  
- Optimisation des appels API et gestion des erreurs.
- Mise en cache des résultats pour améliorer la performance.

**Gestion des erreurs API avec stratégie de retry intelligente :**  
En cas d’erreur lors d’un appel à l’API (ex. : Pixtral Mistral), le système applique une stratégie de tentative progressive :
- Une première tentative est effectuée normalement.
- En cas d’échec, le système attend 5 secondes.
- Une seconde tentative est lancée.
- Si cette tentative échoue également, le document est marqué comme **False Negative (FN)**.
- Le processus de matching est alors ignoré pour ce document.

Cette approche permet de :
- Éviter les blocages prolongés liés à des erreurs temporaires d’API.
- Réduire l’impact des limitations de requêtes ou des interruptions côté fournisseur.
- Maintenir des métriques fiables (le FN est bien comptabilisé).
- Préserver une expérience utilisateur fluide, sans interruption visuelle ou fonctionnelle.

---

Souhaites-tu que je t’envoie la version complète du cahier des charges mise à jour avec cet ajout ?

---

## **7. Aperçu de l'Horaire / Principales Étapes**

| Jalon                         | Date d'achèvement prévue | Description / Détails                                                |
|-------------------------------|---------------------------|---------------------------------------------------------------------|
| **Initialisation du projet**  | 31/03/2025                | Mise en place du repository et des structures de base.              |
| **Implémentation des modules**| 01/04/2025                | Développement des fonctionnalités principales.                      |
| **Version bêta, Tests et validation** | 02/04/2025          | Tests unitaires et ajustements. Version de pré-lancement pour retours utilisateurs. |
| **Lancement final**           | 03/04/2025                | Mise à disposition de l'application pour les utilisateurs finaux. |


---

## **8. Risques et Mitigations**

### **8.1 Risques Identifiés**
- **Limites de l'Pixtral** : Factures manuscrites ou mal structurées peuvent réduire l'efficacité de l'Pixtral.
- **Performance de l'API** : Risque de lenteur ou d'échec de l'API Mistral.
- **Complexité des Factures** : Certaines factures peuvent être difficiles à analyser.

### **8.2 Mitigations**
- Tests unitaires et d'intégration pour garantir la robustesse.
- Interface de validation manuelle des correspondances en cas de doute.
- Monitoring des performances pour détecter et résoudre rapidement les anomalies.


## **9. Livrables**

| Livrable                    | Description / Détails                                             |
|-----------------------------|-------------------------------------------------------------------|
| **Code source**              | Repository avec le code complet de l'application.                |
| **Documentation utilisateur** | Guide d'installation et d'utilisation (README). |
| **Interface utilisateur**    | Application Streamlit avec téléchargement de fichiers et affichage des résultats. |
| **Modèle de matching**       | Algorithme de correspondance des factures et transactions bancaires. |


---

## **9.1. Ce Projet ne Comprend Pas :**
- L'automatisation complète du traitement des erreurs humaines dans la saisie des factures.
- La gestion comptable complète en dehors du rapprochement factures-relevés bancaires.
- L'hébergement ou la mise en production de l'application.

---

## **9.2. Evaluation**

| **Terme / Métrique**   | **Définition métier**                                                                                             | **Formule**                                                 | **Interprétation métier**                                                                                          | **Exemple** |
|------------------------|--------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|-------------|
| **True Positive (TP)** | La facture existe dans le CSV **et** le système l’a correctement matchée à la bonne ligne.                              | -                                                            | ✅ Succès complet du système.                                                                                        | Une facture "Amazon" pour 100€ le 01/01/2024 est correctement associée à la bonne ligne dans le relevé bancaire. |
| **True Negative (TN)** | La facture n'existe pas dans le CSV **et** le système n’a proposé aucun match.                                          | -                                                            | ✅ Le système a correctement ignoré le cas sans correspondance.                                                     | Une facture test sans correspondance n’est pas prise en compte par le système. |
| **False Positive (FP)**| Deux cas : (1) la facture n’existe pas mais un match est proposé ; (2) la facture existe mais le match est incorrect.   | -                                                            | ❌ Erreur critique : fausse alarme → peut **induire le comptable en erreur**.                                      | Une facture "Amazon" est associée à une transaction "Fnac" car les montants sont proches. |
| **False Negative (FN)**| La facture existe dans le CSV **mais** le système ne trouve aucun match.                                                | -                                                            | ⚠️ Erreur non bloquante : match manqué → travail manuel pour le comptable.                                         | Une facture "Amazon" est présente mais ignorée à cause d'une différence de nom (ex : "AMZN"). |
| **Accuracy**           | Pourcentage de cas bien traités (matchés ou ignorés correctement) sur l’ensemble.                                       | (TP + TN) / (TP + TN + FP + FN)                              | Vue d’ensemble, mais peut masquer des déséquilibres entre erreurs graves (FP) et mineures (FN).                    | Sur 100 factures, 90 sont bien traitées → accuracy = 90%. |
| **Précision**          | Parmi les factures matchées par le système, combien sont correctement associées.                                        | TP / (TP + FP)                                               | Doit être **proche de 1** pour éviter les faux positifs (erreurs comptables).                                      | Sur 50 factures matchées, 48 sont correctes → précision = 96%. |
| **Recall (Rappel)**    | Parmi toutes les factures qui **devaient** être matchées, combien le système a effectivement trouvées.                  | TP / (TP + FN)                                               | Doit être élevé pour maximiser l’automatisation et limiter le travail manuel.                                      | Sur 60 factures attendues, 48 sont matchées → rappel = 80%. |
| **F1-Score**           | Moyenne harmonique entre précision et rappel. Permet de mesurer la performance globale du système.                     | 2 × (Precision × Recall) / (Precision + Recall)              | Bon indicateur pour équilibrer automatisation et fiabilité.                                                         | Si précision = 96% et rappel = 80%, alors F1-score ≈ 87,3%. |

 
--- 

## **10 Amélioration: Fonctionnalités Secondaires**
- Export des résultats
- Historique des traitements
- Interface multilingue (FR/EN)
- Traduction universelle du JSON pour prendre en compte les variations internationales dans les montants.

## **10.1 Interface Utilisateur**

### **Design**
#### **Thème et Couleurs**
- **Couleurs principales :** Bleu principal (#0d6efd), Gris foncé (#1a1a1a), Gris clair (#e9ecef), Blanc (#ffffff), Vert (#198754), Rouge (#dc3545), Orange (#ffc107).

#### **Typographie**
- **Police principale :** Inter ou Roboto
- **Tailles de texte :** Titres (24px), Sous-titres (20px), Texte normal (16px), Petits textes (14px).

#### **Composants UI**
**1. En-tête**
   - Logo et titre de l'application
   - Barre de navigation
   - Indicateur de progression

**2. Zones de dépôt**
   - Zones de glisser-déposer
   - Icônes explicites pour chaque type de fichier
   - Messages d'aide contextuels

**3. Boutons et Actions**
   - Boutons principaux et secondaires
   - États de survol et de clic

**4. Affichage des résultats**
   - Cartes pour chaque facture
   - Métriques avec icônes
   - Graphiques de progression

**5. Messages et Notifications**
   - Messages d'erreur, succès et avertissement

#### **Responsive Design**
- **Desktop** : Layout en 3 colonnes, Navigation latérale
- **Tablette** : Layout en 2 colonnes, Contenu redimensionné
- **Mobile** : Layout en 1 colonne, Navigation simplifiée

---

## **11. Remerciements**
- **Streamlit** pour le framework d'interface utilisateur
- **Mistral AI** pour l'API d'analyse
- **Pandas** pour le traitement des données

--- 

## **12. Licence**
Ce projet est open-source. Crédits @HETIC25

---