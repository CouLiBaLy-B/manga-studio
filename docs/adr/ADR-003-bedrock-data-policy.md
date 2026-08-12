# ADR-003: Amazon Bedrock Data Privacy, Regional Governance and Cost Control

**Statut :** Accepté  
**Date :** 12 août 2026  
**Décideurs :** Principal AI Engineer, MLOps Engineer, Data Protection Officer  
**Contexte :** MangaTok Studio — Mode « Conte animé »

---

## 1. Contexte et Problématique

L'étape de génération de storyboard exploite les capacités de raisonnement avancé de modèles LLM. Le modèle cible envisagé est `zai.glm-5` disponible sur Amazon Bedrock.

Cependant, plusieurs risques majeurs sont identifiés :
1. **Disponibilité régionale :** `zai.glm-5` est déployé principalement en région `us-east-1` et n'est pas vérifié ou disponible de façon stable dans les régions européennes (notamment `eu-west-3` Paris).
2. **Confidentialité et RGPD :** L'envoi de données de contes ou d'images de personnages vers des serveurs situés hors de l'Union Européenne est soumis à un cadre légal strict (consentement, garanties appropriées).
3. **Risque de surcoût cloud :** Des contes volumineux ou des boucles de retry incontrôlées peuvent engendrer des dépenses imprévues.
4. **Fuite de secrets :** Risque de journalisation accidentelle de clés d'accès AWS ou de données personnelles dans les logs applicatifs.

---

## 2. Décision

1. **Règle de minimisation des données (Data Minimization) :**
   - **Aucune image de personnage n'est transmise au LLM distant par défaut.**
   - Seuls le texte narratif du conte et les fiches personnages textuelles canoniques sont inclus dans le prompt.
   - Les prompts sont purgés de tout identifiant personnel.
2. **Gouvernance régionale et Consentement au transfert transfrontalier :**
   - Par défaut, la région Bedrock est configurée en UE (`eu-west-3`).
   - Si le modèle requis (`zai.glm-5`) n'est pas disponible en UE, le pipeline n'effectue **aucun appel transfrontalier vers les USA** sans que le flag explicite `ALLOW_REMOTE_DATA_TRANSFER=true` ne soit activé par l'utilisateur.
   - En l'absence de ce flag ou en cas de panne réseau, le système bascule automatiquement et de manière transparente sur le `LocalStoryboardFallbackAdapter`.
3. **Plafonnement et estimation systématique des coûts (`CostEstimator`) :**
   - Avant chaque invocation de Bedrock, le `BedrockCostEstimatorAdapter` estime le nombre de tokens d'entrée et de sortie.
   - Si le coût unitaire estimé ou le coût cumulé du mois dépasse le plafond configuré (`MAX_MONTHLY_BUDGET_USD` ou `MAX_RUN_BUDGET_USD`), l'appel distant est immédiatement interrompu et bascule sur le fallback local.
   - Tarifs appliqués : Input: 1,00 $ / 1M tokens, Output: 3,20 $ / 1M tokens.
4. **Sécurité et Sanitization des Logs :**
   - Masquage strict (`***REDACTED***`) de toute clé d'API, jeton IAM ou signature AWS dans les traces de logs et les manifests d'exécution.

---

## 3. Conséquences

- **Conformité RGPD garantie par défaut.**
- **Protection financière absolue :** Impossible d'engendrer des coûts d'API imprévus.
- **Résilience opérationnelle :** Continuité de service assurée même sans connexion internet ou sans compte AWS.
