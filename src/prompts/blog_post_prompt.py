blog_post_prompt = """

Génère un article SEO/GEO optimisé au format JSON avec les spécifications suivantes :

INSTRUCTIONS TECHNIQUES :
1. Format JSON avec échappement correct des caractères spéciaux
2. Structure HTML sémantique pour la colonne "Contenu article"
   - Utilisation appropriée des balises HTML5 (article, section, aside, figure, etc.)
   - Balisage Schema.org pour le contenu principal
   - Attributs alt descriptifs pour les images
   - Structure de titres logique (H1 > H2 > H3)
3. Optimisation E-E-A-T renforcée
   - Citations de sources autoritaires (études, experts)
   - Dates récentes (2024-2025)
   - Mentions d'expertise professionnelle
   - Références locales et géographiques
4. Optimisation Mobile-first
   - Paragraphes courts (2-3 phrases maximum)
   - Espacement optimal pour la lecture mobile
   - Points clés en début de paragraphe
   - Listes à puces pour les informations importantes
5. Métriques de contenu
   - Durée de lecture : 6-8 minutes
   - Densité de mots-clés : 1-2%
   - Longueur optimale : 1500-2000 mots
   - Readability score : 60-70 (Flesch)

STRUCTURE DE CONTENU :
1. Introduction (10% du contenu)
   - Hook accrocheur avec mot-clé principal
   - Réponse directe à l'intention de recherche
   - Preview des points clés (featured snippet optimization)

2. Table des matières
   - Structure HTML avec ancres
   - Hiérarchie claire des sections
   - Mots-clés naturellement intégrés

3. Corps de l'article (75% du contenu)
   - 3 sections principales maximum (H2)
   - Sous-sections pertinentes (H3)
   - Pour chaque section :
     * Introduction du concept
     * Développement avec exemples
     * Points clés ou takeaways
     * Éléments visuels suggérés
   - Inclure :
     * Au moins 2 listes à puces
     * 1-2 citations expertes (blockquote)
     * Données statistiques récentes
     * Exemples locaux/géographiques
     * FAQ structurée (3-5 questions)

4. Conclusion (15% du contenu)
   - Résumé des points clés
   - CTA stratégique : <a href="{{cta_link}}">texte d'appel à l'action</a>
   - Question ouverte pour l'engagement

OPTIMISATION SEO/GEO 2025 :
1. Intent Mapping
   - Informationnel
   - Transactionnel
   - Local/Géographique
   - Navigationnel

2. Semantic Search
   - Entités et relations
   - Questions associées
   - Termes connexes
   - Variations linguistiques

3. Local SEO
   - Mentions géographiques naturelles
   - Références culturelles locales
   - Adaptation régionale du vocabulaire
   - Citations d'experts locaux

4. Core Web Vitals
   - Structure HTML légère
   - Suggestions d'optimisation images
   - Mise en page fluide
   - Temps de lecture estimé

FORMAT JSON REQUIS :
{
  "Titre": "string - Titre optimisé pour CTR",
  "Slug": "string - URL optimisée SEO",
  "Date de publication": "string - Format DD/MM/YYYY",
  "Durée de lecture": "string - X minutes",
  "Table des matières": "string - HTML avec ancres",
  "Contenu article": "string - HTML complet et structuré",
  "Type d'article": "string - Catégorie principale",
  "Type d'article 2-8": "string - Catégories secondaires",
  "Résumé de l'article": "string - 155-160 caractères",
  "Balise title": "string - 50-60 caractères",
  "META DESCRIPTION": "string - 150-160 caractères avec CTA"
}

CRITÈRES DE QUALITÉ :
1. Pertinence
   - Réponse directe à l'intention de recherche
   - Contenu actionnable et utile
   - Expertise démontrée

2. Crédibilité
   - Sources citées
   - Données vérifiables
   - Expertise établie

3. Engagement
   - Style conversationnel
   - Questions rhétoriques
   - Appels à l'action naturels

4. Technique
   - Balisage HTML propre
   - Structure cohérente
   - Optimisation multiplateforme

Ne remplir que les champs pour lesquels vous avez des informations pertinentes et fiables.
Utiliser \n\n pour les sauts de section et \\" pour les guillemets dans le contenu HTML.

MOTS-CLÉS CIBLES : 

{keywords}

"""
