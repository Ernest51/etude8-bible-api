def generate_simple_theological_explanation(verse_text: str, book_name: str, chapter: int, verse_num: int) -> str:
    verse_lower = verse_text.lower()
    explanation_parts = []
    
    # Analyse contextuelle spécifique pour Genèse 1
    if book_name == "Genèse" and chapter == 1:
        # Image de Dieu (v26-27)
        if "image" in verse_lower and ("homme" in verse_lower or "créa" in verse_lower):
            explanation_parts.append("La création de l'homme à l'image de Dieu révèle la dignité unique de l'humanité et sa vocation à refléter la gloire divine. Cette image implique une capacité relationnelle, créatrice et morale qui distingue l'homme du reste de la création.")
        
        # Bénédiction et mandat (v28)
        elif ("bénit" in verse_lower or "fructifiez" in verse_lower) and "multipliez" in verse_lower:
            explanation_parts.append("Cette bénédiction divine établit le mandat créationnel : fructifier, multiplier, remplir et dominer la terre. La domination n'est pas exploitation mais intendance responsable sous l'autorité de Dieu.")
        
        # Provision alimentaire pour l'homme (v29)
        elif "plante" in verse_lower and "nourriture" in verse_lower and "vous" in verse_lower:
            explanation_parts.append("Dieu pourvoit généreusement aux besoins de l'humanité. Ce régime végétal initial révèle l'harmonie parfaite de la création avant la chute, où aucune mort n'était nécessaire pour la subsistance.")
        
        # Provision pour les animaux (v30)
        elif "animal" in verse_lower and "plante verte" in verse_lower:
            explanation_parts.append("La providence divine s'étend à toute créature vivante. Cette provision végétale universelle témoigne de l'ordre parfait voulu par Dieu, où toute vie trouve sa subsistance sans violence.")
        
        # Évaluation divine (v31)
        elif "très bon" in verse_lower or ("vit" in verse_lower and "bon" in verse_lower):
            explanation_parts.append("L'évaluation divine 'très bon' couronne l'œuvre créatrice. Cette perfection originelle contraste avec l'état actuel du monde et annonce la restauration future dans la nouvelle création.")
        
        # Séparation/organisation (autres versets Genèse 1)
        elif "sépara" in verse_lower or "divisa" in verse_lower:
            explanation_parts.append("L'acte divin de séparation révèle un Dieu d'ordre qui structure le cosmos. Cette organisation témoigne de sa sagesse et prépare un habitat propice à la vie.")
        
        # Création générale
        elif "créa" in verse_lower or "fit" in verse_lower:
            explanation_parts.append("Chaque acte créateur de Dieu témoigne de sa puissance souveraine et de sa bonté. La création ex nihilo (à partir de rien) révèle l'absolue transcendance divine.")
    
    # Autres livres - analyses contextuelles améliorées
    elif book_name == "Jean":
        if verse_num <= 18:  # Prologue
            if "parole" in verse_lower or "verbe" in verse_lower:
                explanation_parts.append("Le Logos éternel révèle la divinité préexistante du Christ et son rôle dans la création. Cette Parole est personnelle, créatrice et révélatrice.")
            elif "lumière" in verse_lower:
                explanation_parts.append("Christ comme lumière véritable illumine tout homme. Cette lumière révèle, sanctifie et juge, offrant la vie à ceux qui la reçoivent.")
            elif "monde" in verse_lower and "connu" in verse_lower:
                explanation_parts.append("Le drame de l'incarnation : le Créateur vient chez les siens qui ne le reconnaissent pas. Cette tragédie révèle l'aveuglement du péché.")
        else:
            explanation_parts.append("Ce témoignage révèle la divinité du Christ et la vie éternelle disponible par la foi en son nom.")
    
    elif book_name == "Psaumes":
        if "louange" in verse_lower or "béni" in verse_lower:
            explanation_parts.append("La louange authentique jaillit d'un cœur qui reconnaît la bonté et la fidélité divines dans toutes circonstances.")
        elif "péché" in verse_lower or "iniquité" in verse_lower:
            explanation_parts.append("La confession sincère ouvre la voie au pardon divin et à la restauration de la communion avec Dieu.")
        else:
            explanation_parts.append("Ce verset exprime l'authentique spiritualité dans la relation avec Dieu, mêlant adoration, supplication et confiance.")
    
    # Fallback par livre si pas d'analyse spécifique
    if not explanation_parts:
        book_contexts = {
            "Genèse": "Ce récit des origines révèle les fondements du plan divin pour l'humanité et la création.",
            "Exode": "Ce passage illustre l'œuvre libératrice de Dieu et établit les bases de l'alliance avec son peuple.",
            "Matthieu": "Cet enseignement du Roi révèle les principes du royaume des cieux et appelle à la transformation du cœur.",
            "Romains": "Cette vérité doctrinale expose les fondements de la justification par la foi et la vie nouvelle en Christ.",
            "Éphésiens": "Ce passage révèle les richesses spirituelles du croyant et sa position glorieuse en Christ.",
        }
        explanation_parts.append(book_contexts.get(book_name, f"Ce verset révèle un aspect important de la révélation divine dans le livre de {book_name}."))
    
    full_explanation = " ".join(explanation_parts)
    return ' '.join(full_explanation.split())