import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import os
import logging
import time

# Configuration du logger
logger = logging.getLogger(__name__)

def calculate_confusion_matrix(csv_data, matched_results, image_filename):
    """
    Calcule la matrice de confusion pour le matching de factures.
    
    Args:
        csv_data (pd.DataFrame): DataFrame contenant les données du CSV avec la colonne 'source'
        matched_results (list): Liste des résultats de matching
        image_filename (str): Nom du fichier image à analyser
        
    Returns:
        dict: Dictionnaire contenant la matrice de confusion et les métriques
    """
    logger.info(f"Calcul de la matrice de confusion pour l'image: {image_filename}")
    
    try:
        # Initialiser les compteurs
        TP = 0  # True Positive
        FP = 0  # False Positive
        TN = 0  # True Negative
        FN = 0  # False Negative
        
        # Convertir le nom du fichier image au format attendu dans le CSV
        expected_source = f"{os.path.basename(image_filename)}.json"
        logger.debug(f"Source attendue dans le CSV: {expected_source}")
        
        # Vérifier si l'image existe dans le CSV
        image_exists_in_csv = expected_source in csv_data['source'].values
        logger.debug(f"Image existe dans le CSV: {image_exists_in_csv}")
        
        # Vérifier si le matching a trouvé des résultats
        has_matches = len(matched_results) > 0 if matched_results else False
        logger.debug(f"Nombre de matches trouvés: {len(matched_results) if matched_results else 0}")
        
        # Calculer les métriques selon la logique décrite
        if image_exists_in_csv and has_matches:
            # Vérifier si le match est correct (TP) ou incorrect (FP)
            matched_sources = [result.get('source', '') for result in matched_results if result]
            if expected_source in matched_sources:
                TP += 1
                logger.info("True Positive: Match correct trouvé")
            else:
                FP += 1
                logger.info("False Positive: Mauvais match trouvé")
        elif image_exists_in_csv and not has_matches:
            FN += 1
            logger.info("False Negative: Image existe mais pas de match trouvé")
        elif not image_exists_in_csv and not has_matches:
            TN += 1
            logger.info("True Negative: Image n'existe pas et pas de match trouvé")
        elif not image_exists_in_csv and has_matches:
            FP += 1
            logger.info("False Positive: Match trouvé pour une image qui n'existe pas")
        
        # Créer la matrice de confusion
        conf_matrix = [[TN, FP], [FN, TP]]
        
        # Calculer les métriques de performance avec gestion des divisions par zéro
        total = TP + FP + TN + FN
        accuracy = (TP + TN) / total if total > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Logger les métriques
        logger.info("\nMatrice de confusion:")
        logger.info(f"[[{TN}, {FP}],")
        logger.info(f" [{FN}, {TP}]]")
        logger.info("\nMétriques de performance:")
        logger.info(f"Accuracy: {accuracy:.2f}")
        logger.info(f"Precision: {precision:.2f}")
        logger.info(f"Recall: {recall:.2f}")
        logger.info(f"F1-score: {f1:.2f}")
        
        return {
            "confusion_matrix": conf_matrix,
            "metrics": {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            },
            "counts": {
                "true_positive": TP,
                "false_positive": FP,
                "true_negative": TN,
                "false_negative": FN
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la matrice de confusion: {str(e)}", exc_info=True)
        return None

def evaluate_matching_performance(csv_path, matching_results, image_filename):
    """
    Évalue la performance globale du système de matching.
    
    Args:
        csv_path (str): Chemin vers le fichier CSV
        matching_results (list): Liste des résultats de matching pour toutes les images
        image_filename (str): Nom du fichier image à analyser
        
    Returns:
        dict: Résultats de l'évaluation
    """
    try:
        logger.info(f"Évaluation des performances pour l'image: {image_filename}")
        
        if not os.path.exists(csv_path):
            logger.error(f"Le fichier CSV n'existe pas: {csv_path}")
            return None
            
        logger.info(f"Chargement du fichier CSV: {csv_path}")
        
        # Charger les données du CSV avec gestion des erreurs
        try:
            csv_data = pd.read_csv(csv_path)
            if csv_data.empty:
                logger.warning("Le fichier CSV est vide")
                return None
            logger.debug(f"CSV chargé avec succès. Nombre de lignes: {len(csv_data)}")
        except pd.errors.EmptyDataError:
            logger.error("Le fichier CSV est vide ou mal formaté")
            return None
        except Exception as e:
            logger.error(f"Erreur lors du chargement du CSV: {str(e)}")
            return None
            
        # Vérifier les colonnes requises
        required_columns = ['source']
        if not all(col in csv_data.columns for col in required_columns):
            logger.error(f"Colonnes manquantes dans le CSV. Colonnes requises: {required_columns}")
            return None
            
        # Calculer la matrice de confusion
        results = calculate_confusion_matrix(csv_data, matching_results, image_filename)
        if results is None:
            logger.error("Échec du calcul de la matrice de confusion")
            return None
            
        return results
        
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation: {str(e)}", exc_info=True)
        return None

def benchmark(df, df_predicted):
    """
    Calculate benchmark metrics for model predictions.
    
    Args:
        df (pd.DataFrame): Ground truth dataframe
        df_predicted (pd.DataFrame): Predictions dataframe
        
    Returns:
        dict: Dictionary containing benchmark metrics
    """
    try:
        logger.info("Début du benchmark")
        
        if df.empty or df_predicted.empty:
            logger.error("Un des DataFrames est vide")
            return None
            
        # Vérifier les colonnes requises
        required_columns = ['date', 'amount', 'currency', 'vendor', 'source']
        for col in required_columns:
            if col not in df.columns or col not in df_predicted.columns:
                logger.error(f"Colonne manquante: {col}")
                return None
        
        # Merge the dataframes on common columns to align corresponding rows
        merged_df = pd.merge(
            df[required_columns], 
            df_predicted[required_columns], 
            on=['date', 'amount', 'currency', 'vendor'], 
            suffixes=('_actual', '_predicted')
        )
        
        if merged_df.empty:
            logger.warning("Aucune correspondance trouvée après fusion des DataFrames")
            return None
        
        # Extract actual and predicted labels
        y_actual = merged_df['source_actual']
        y_predicted = merged_df['source_predicted']
        
        # Calculate metrics with error handling
        try:
            metrics = {
                'accuracy': accuracy_score(y_actual, y_predicted) * 100,
                'precision': precision_score(y_actual, y_predicted, average='weighted', zero_division=0) * 100,
                'recall': recall_score(y_actual, y_predicted, average='weighted', zero_division=0) * 100,
                'f1_score': f1_score(y_actual, y_predicted, average='weighted', zero_division=0) * 100,
                'classification_report': classification_report(y_actual, y_predicted),
                'confusion_matrix': confusion_matrix(y_actual, y_predicted).tolist()
            }
            
            logger.info("Benchmark terminé avec succès")
            logger.debug(f"Métriques calculées: {metrics}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors du benchmark: {str(e)}", exc_info=True)
        return None