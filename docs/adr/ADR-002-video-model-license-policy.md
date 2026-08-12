# ADR-002: Video Model Licensing and Territorial Compliance Policy (MiniMax H3)

**Statut :** Accepté  
**Date :** 12 août 2026  
**Décideurs :** Principal AI Engineer, AI Research Scientist, Legal & Compliance Team  
**Contexte :** MangaTok Studio — Mode « Conte animé »

---

## 1. Contexte et Problématique

Le modèle vidéo open-weight **MiniMax H3 (Hailuo 3.0)** publié le 3 août 2026 est distribué sous la **MiniMax H3 Community License Agreement** (datée du 2 août 2026 par Nanonoble Pte. Ltd.).

L'analyse légale de la licence révèle plusieurs clauses contraignantes :
1. **Clause territoriale (Section I.3) :** Le territoire applicable exclut formellement les **États-Unis (US)**, l'**Union Européenne (UE)**, le **Royaume-Uni (UK)** et la **Corée du Sud (KR)**.
2. **Clause de déploiement et outputs (Section I.3 & IV) :** Les utilisateurs situés dans les territoires exclus ne sont pas autorisés à exécuter les poids open-weights localement, ni à déployer commercialement les vidéos générées à partir de ces poids locaux.
3. **Plafond de revenus (Section IV.1) :** Les organisations réalisant un chiffre d'affaires supérieur à 20 millions USD requièrent une licence commerciale distincte.
4. **Attribution obligatoire (Section IV.2) :** Toute interface utilisateur commerciale basée sur H3 doit afficher de manière proéminente « MiniMax H3 ».
5. **Clause d'anti-distillation (Section V.3) :** Interdiction globale d'utiliser les sorties pour entraîner un modèle concurrent.

MangaTok Studio cible un déploiement sécurisé pour des créateurs de contenu francophones et internationaux, dans le respect strict des réglementations européennes (RGPD, AI Act) et du droit de la propriété intellectuelle.

---

## 2. Décision

1. **Intégration d'un composant obligatoire `LicenseGuard` :**
   - Tout appel à un générateur vidéo doit impérativement être validé en amont par le `LicenseGuardPort`.
   - Le `LicenseGuard` examine le triplet : `(model_id, deployment_profile, deployment_territory)`.
2. **Politique de refus strict en profil commercial :**
   - **Profil Commercial + Territoire UE / US / UK / KR + Modèle H3 Local :** **REFUS SYSTÉMATIQUE** (`LicenseViolationError`).
   - Le système refuse de lancer le job vidéo local et consigne le motif dans le rapport de manifest.
3. **Profil de Recherche (« Research / Non-Commercial ») :**
   - Autorisé uniquement sous condition de flag explicite `DEPLOYMENT_PROFILE=research` et `ENABLE_H3_LOCAL=true`.
   - Un message d'avertissement juridique explicite est inscrit dans les logs et le rapport d'exécution.
4. **Alternative de Production pour MangaTok Studio :**
   - Pour les environnements commerciaux en UE, MangaTok Studio supporte par conception une architecture de génération modulaire (ex: Wan2.1 Apache 2.0 ou CogVideoX Apache 2.0 + TTS français) ou l'API SaaS officielle MiniMax (non soumise à la clause d'exclusion d'exécution des poids locaux).

---

## 3. Conséquences

- **Sécurité juridique totale :** Aucun risque de violation de licence ou de contentieux de propriété intellectuelle pour les utilisateurs commerciaux de MangaTok Studio.
- **Transparence et Auditabilité :** Chaque `render_manifest.jsonl` consigne la licence, la version du modèle, l'URL source de la licence, la date de vérification et la décision formelle du guard.
- **Fail-Safe par défaut :** Le flag par défaut est `ENABLE_H3_LOCAL=false`.
