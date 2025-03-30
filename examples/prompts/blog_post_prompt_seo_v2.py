blog_post_prompt_seo_v2 = """
INSTRUCTIONS TECHNIQUES :
1. Format JSON avec échappement correct des caractères spéciaux
2. Structure HTML sémantique pour la colonne "Contenu article"
   - Utilisation appropriée des balises HTML5 (article, section, aside, figure, etc.)
   - Balisage Schema.org complet (Article, HowTo et FAQ schemas selon pertinence)
   - Attributs alt descriptifs et SEO-optimisés pour les images
   - Structure de titres sous forme de questions naturelles (H1 > H2 > H3)
3. Optimisation E-E-A-T renforcée
   - Citations de sources autoritaires (études, experts du domaine)
   - Inclure 1 content_reference (url) qui semble pertinent pour le sujet (à choisir parmi ceux des mots-clés fournis)
   - Dates récentes (2024-2025)
   - Mentions d'expertise professionnelle avec preuves d'expérience
   - Références locales et géographiques adaptées au sujet
4. Optimisation Mobile et Voice-first
   - Paragraphes courts (2-3 phrases maximum)
   - Espacement optimal pour la lecture mobile
   - Points clés en début de paragraphe sous forme de réponses directes (40-50 mots)
   - Listes à puces pour les informations importantes
   - Langage conversationnel adapté aux recherches vocales
5. Métriques de contenu
   - Durée de lecture : 6-8 minutes
   - Densité de mots-clés : 1-2%
   - Longueur optimale : 2500-3000 mots
   - Readability score : 60-70 (Flesch)
6. Optimisation pour extraction AI
   - Réponses directes et concises après chaque question-titre
   - Format extractible pour les assistants AI et moteurs génératifs
   - Structure en blocs de réponses pour faciliter l'extraction par AI

STRUCTURE DE CONTENU :
1. Introduction (10% du contenu)
   - Hook accrocheur avec mot-clé principal et réponse directe à la question principale
   - Réponse de 40-50 mots à l'intention de recherche principale
   - Preview des points clés (featured snippet optimization)
   - Position claire sur l'approche du sujet

2. Table des matières
   - Structure HTML avec ancres et attributs schema
   - Hiérarchie claire des sections sous forme de questions naturelles
   - Mots-clés naturellement intégrés dans les questions

3. Corps de l'article (75% du contenu)
   - Format question-réponse pour chaque section principale (optimisé AEO)
   - Maximum 3 questions principales (H2) formulées comme les utilisateurs les poseraient
   - Sous-questions pertinentes (H3) également formulées comme questions naturelles
   - Pour chaque section :
     * Réponse directe et concise (40-50 mots) en début de section
     * Développement avec exemples et preuves
     * Points clés ou takeaways en fin de section
     * Éléments visuels suggérés avec descriptions détaillées
   - Inclure :
     * Au moins 2 listes à puces pour les méthodes ou concepts
     * 1 citation experte (blockquote) d'une autorité du domaine
     * Données récentes et pertinentes au sujet
     * Exemples locaux/géographiques adaptés au contexte

4. Conclusion (15% du contenu)
   - Résumé des points clés avec réponse finale à la question principale
   - CTA stratégique : <a href="{{cta_link}}">texte d'appel à l'action</a>
   - Question ouverte pour l'engagement
   - Rappel du message principal de l'article

OPTIMISATION SEO/GEO/AEO 2025 :
1. Intent Mapping
   - Informationnel : réponses directes aux questions principales
   - Transactionnel : suggestions de produits/services pertinents
   - Local/Géographique : adaptations régionales si applicable
   - Navigationnel : liens vers ressources complémentaires
   - Intégration naturelle de l'intention de recherche dans chaque section

2. Optimisation AEO (Answer Engine Optimization)
   - Structure question-réponse pour chaque section (H2/H3 formulés comme questions)
   - Réponses directes de 40-50 mots après chaque titre-question
   - Mise en évidence des réponses pour extraction par AI
   - Format compatible avec assistants vocaux et générateurs AI
   - FAQ schema markup complet pour toutes les questions-réponses

3. Optimisation GEO (Generative Engine Optimization)
   - Structure en blocs informationnels clairement définis pour AI
   - Citations et références vérifiables et traçables
   - Relations d'entités clairement définies dans le domaine traité
   - Contenu factuellement exact et mise en contexte des concepts
   - Équilibre entre information complète et concision

4. Semantic Search
   - Entités et relations clairement définies selon le sujet
   - Questions associées en sous-titres H3 format "People Also Ask"
   - Termes connexes et vocabulaire spécialisé pertinent
   - Variations linguistiques adaptées au public cible

5. Local SEO
   - Mentions géographiques naturelles si pertinent pour le sujet
   - Références aux spécificités régionales/nationales si applicable
   - Adaptation régionale du vocabulaire selon la cible
   - Citations d'experts locaux si pertinent

6. Core Web Vitals
   - Structure HTML légère et optimisée
   - Suggestions d'optimisation images avec dimensions recommandées
   - Mise en page fluide et responsive
   - Temps de lecture estimé par section
   
7. Mots-clés à intégrer
   - Intégrer les mots-clés de manière naturelle et conversationnelle
   - Éviter d'utiliser les mêmes mots-clés dans plusieurs sections
   - Varier les formulations et le contexte d'utilisation
   - Privilégier les mots-clés à forte importance dans le cluster
   - Favoriser l'usage de questions naturelles contenant les mots-clés

FORMAT JSON REQUIS :
{
  "Titre": "string - Titre optimisé pour CTR avec 2025 ou l'année en cours si plus récente",
  "Slug": "string - URL optimisée SEO",
  "Date de publication": "string - Format DD/MM/YYYY -- Date aléatoire sur l'année YTD",
  "Durée de lecture": "string - X minutes",
  "Contenu article": "string - HTML complet et structuré",
  "Type d'article": "string - Catégorie principale",
  "Type d'article 2-8": "string - Catégories secondaires",
  "Résumé de l'article": "string - 155-160 caractères",
  "Balise title": "string - 50-60 caractères",
  "META DESCRIPTION": "string - 150-160 caractères avec CTA"
}

CRITÈRES DE QUALITÉ :
1. Pertinence
   - Réponse directe à l'intention de recherche en début de chaque section
   - Contenu actionnable et utile avec informations pratiques
   - Expertise démontrée par citations et références

2. Crédibilité
   - Sources fiables citées (études récentes, experts reconnus)
   - Données vérifiables avec dates et origines
   - Expertise établie avec mentions de qualifications pertinentes

3. Engagement
   - Style conversationnel adapté aux recherches vocales
   - Questions rhétoriques alignées avec les requêtes réelles des utilisateurs
   - Appels à l'action naturels et non-intrusifs

4. Technique
   - Balisage HTML propre avec schémas appropriés
   - Structure question-réponse cohérente pour AEO
   - Optimisation multiplateforme (mobile, desktop, voice)

Ne remplir que les champs pour lesquels vous avez des informations pertinentes et fiables.
Utiliser 
 pour les sauts de section et \" pour les guillemets dans le contenu HTML.

IMPORTANT: RESPECTER STRICTEMENT LA LIMITE DE 2500 MOTS. PRIORISER CONCISION ET CLARTÉ.

UTILISEZ LES MOTS-CLÉS FOURNIS: Intégrer naturellement les mots-clés fournis dans le format JSON, en respectant leur importance relative ( importance_in_cluster ) et l'intention de recherche associée ( intent ).

Local : 
Near me : Not specified
- Si 'Near Me' est spécifié, adapter le contenu à cette zone géographique précise
- Concentration sur les recherches "Near Me" / "Près de chez moi"
- Intégrer des références géographiques précises (ville, région, points d'intérêt)
- Sinon garder la zone indéfinie sans en mentionner une en particulier

MOTS-CLÉS CIBLES : 
{"cluster_name": "dressage de chien à domicile", "keywords": [{"primary_keyword": "dressage de chien à domicile", "importance_in_cluster": 0.5, "intent": "Commercial", "volume": 70, "competition": 0.0, "content_references": ["https://www.canibest.com/educateur-canin-domicile/", "https://www.pagesjaunes.fr/activites/dresseur-canin.html"]}, {"primary_keyword": "dresseur de chien à domicile", "importance_in_cluster": 0.5, "intent": "Commercial", "volume": 70, "competition": 0.0, "content_references": ["https://www.canibest.com/educateur-canin-domicile/", "https://www.pagesjaunes.fr/activites/dresseur-canin.html"]}]}
"""
