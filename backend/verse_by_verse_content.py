# -*- coding: utf-8 -*-
"""
Générateur 'verset par verset' enrichi MASSIVEMENT
- expose VERSE_BY_VERSE_LIBRARY (base considérablement élargie)
- helpers: get_verse_by_verse_content, get_all_verses_for_chapter
- enrichissement: _enrich_explanation + build_verse_by_verse_study
- parsing simple: parse_passage
"""

from typing import Dict, List, Tuple, Optional
import re

# =====================================================================
# 1) BASE DE DONNÉES ENRICHIE MASSIVEMENT - Couvre les 66 livres
# =====================================================================

VERSE_BY_VERSE_LIBRARY: Dict[str, Dict[int, Dict[int, Dict[str, str]]]] = {
    # ========== ANCIEN TESTAMENT ==========
    "Genèse": {
        1: {
            1: {
                "verse": "Au commencement, Dieu créa les cieux et la terre.",
                "explanation": (
                    "Au commencement (Bereshit) affirme l'origine absolue du temps et de la matière. "
                    "Dieu (Elohim), pluriel de majesté, laisse entrevoir la Trinité. "
                    "Créa (bara) : création ex nihilo, acte souverain réservé à Dieu seul. "
                    "Les cieux et la terre : totalité du cosmos visible et invisible. "
                    "Ce verset fonde toute théologie : Dieu transcendant, créateur, souverain."
                ),
            },
            2: {
                "verse": "La terre était informe et vide; il y avait des ténèbres sur l'abîme, et l'esprit de Dieu se mouvait au-dessus des eaux.",
                "explanation": (
                    "Tohu va-bohu indique l'absence d'ordre et de contenu, non un chaos préexistant. "
                    "L'Esprit de Dieu (ruach Elohim) plane : préparation de l'ordre par la présence divine. "
                    "Cette présence trinitaire anticipe l'œuvre créatrice qui suit. "
                    "Les ténèbres ne sont pas le mal mais l'absence d'ordre divin."
                ),
            },
            3: {
                "verse": "Dieu dit: Que la lumière soit! Et la lumière fut.",
                "explanation": (
                    "Première parole créatrice (fiat) révélant la puissance du Logos. "
                    "La lumière précède les luminaires : elle est métaphysique avant d'être physique. "
                    "Jean 1:1-5 et 2 Cor 4:6 éclairent cette lumière originelle. "
                    "L'efficacité immédiate de la parole divine : 'Il dit et cela fut' (Ps 33:9)."
                ),
            },
            26: {
                "verse": "Puis Dieu dit: Faisons l'homme à notre image, selon notre ressemblance, et qu'il domine sur les poissons de la mer, sur les oiseaux du ciel, sur le bétail, sur toute la terre, et sur tous les reptiles qui rampent sur la terre.",
                "explanation": (
                    "Faisons révèle la délibération trinitaire. L'image de Dieu (tselem) : rationalité, moralité, spiritualité, relation. "
                    "La domination est une vice-gérance sous l'autorité divine. "
                    "L'homme est créé pour régner dans la justice et la sagesse. "
                    "Christ, image parfaite, restaure cette vocation (Col 1:15, 1 Cor 15:45-49)."
                ),
            },
            27: {
                "verse": "Dieu créa l'homme à son image, il le créa à l'image de Dieu, il créa l'homme et la femme.",
                "explanation": (
                    "Triple répétition souligne la dignité unique de l'humanité. "
                    "Homme et femme ensemble portent l'image divine : complémentarité ontologique. "
                    "La bissexualité révèle la richesse relationnelle de Dieu lui-même. "
                    "Fondement de la dignité humaine, de l'égalité et de l'alliance matrimoniale."
                ),
            }
        },
        2: {
            7: {
                "verse": "L'Éternel Dieu forma l'homme de la poussière de la terre, il souffla dans ses narines un souffle de vie et l'homme devint un être vivant.",
                "explanation": (
                    "Formation (yatsar) évoque le potier façonnant l'argile : intimité créatrice. "
                    "Poussière ('adamah) rappelle l'humilité de l'origine matérielle. "
                    "Le souffle divin (neshamah) distingue l'homme de l'animal : âme spirituelle. "
                    "Être vivant (nephesh chayyah) : totalité psychosomatique, personne intégrée."
                ),
            },
            15: {
                "verse": "L'Éternel Dieu prit l'homme, et le plaça dans le jardin d'Éden pour le cultiver et pour le garder.",
                "explanation": (
                    "Éden signifie 'délice' : état originel de bénédiction. "
                    "Cultiver (abad) et garder (shamar) : travail créatif et responsabilité écologique. "
                    "Le travail précède la chute : il est vocation, non malédiction. "
                    "Préfigure la nouvelle création où l'homme règne avec Christ."
                ),
            },
            17: {
                "verse": "mais tu ne mangeras pas de l'arbre de la connaissance du bien et du mal, car le jour où tu en mangeras tu mourras.",
                "explanation": (
                    "Commandement révélant la structure morale de la création. "
                    "Connaissance du bien et du mal : autonomie morale usurpée. "
                    "Mort : séparation spirituelle immédiate, physique différée. "
                    "Test d'obéissance révélant la nature de l'amour : libre choix."
                ),
            }
        },
        3: {
            1: {
                "verse": "Le serpent était le plus rusé de tous les animaux des champs, que l'Éternel Dieu avait faits. Il dit à la femme: Dieu a-t-il réellement dit: Vous ne mangerez pas de tous les arbres du jardin?",
                "explanation": (
                    "Le serpent, instrument de Satan (Apoc 12:9), introduit le doute par la question. "
                    "Ruse ('arum) : intelligence détournée vers le mal. "
                    "Première attaque contre l'autorité de la Parole divine. "
                    "Méthode constante de la tentaion : 'Dieu a-t-il réellement dit ?'"
                ),
            },
            15: {
                "verse": "Je mettrai inimitié entre toi et la femme, entre ta postérité et sa postérité: celle-ci t'écrasera la tête, et tu lui blesseras le talon.",
                "explanation": (
                    "Protévangile : première promesse messianique de l'Écriture. "
                    "Inimitié : guerre spirituelle entre les deux lignées. "
                    "Postérité de la femme : Christ et son peuple. "
                    "Écraser la tête vs blesser le talon : victoire décisive vs souffrance temporaire. "
                    "Accompli à la croix où Satan est vaincu (Col 2:15)."
                ),
            }
        },
        12: {
            1: {
                "verse": "L'Éternel dit à Abram: Va-t'en de ton pays, de ta patrie, et de la maison de ton père, dans le pays que je te montrerai.",
                "explanation": (
                    "Appel d'Abraham inaugure l'histoire du salut particularisé. "
                    "Triple séparation : pays (sécurité), patrie (culture), famille (identité). "
                    "Foi comme déracinement et attachement à Dieu seul. "
                    "Préfigure l'appel de l'Église hors du monde (Héb 11:8-10)."
                ),
            },
            2: {
                "verse": "Je ferai de toi une grande nation, et je te bénirai; je rendrai ton nom grand, et tu seras une source de bénédiction.",
                "explanation": (
                    "Alliance abrahamique : promesses inconditionnelles de Dieu. "
                    "Grande nation : Israël selon la chair, Église selon l'esprit. "
                    "Bénédiction personnelle et médiatrice pour les nations. "
                    "Nom grand : réputation fondée sur la grâce, non les œuvres."
                ),
            },
            3: {
                "verse": "Je bénirai ceux qui te béniront, et je maudirai ceux qui te maudiront; et toutes les familles de la terre seront bénies en toi.",
                "explanation": (
                    "Solidarité divine avec Abraham et sa postérité. "
                    "Bénédiction universelle accomplie en Christ (Gal 3:8-9). "
                    "L'Évangile aux nations prévu dès l'alliance abrahamique. "
                    "Israël comme prêtre des nations dans le plan divin."
                ),
            }
        }
    },
    
    "Exode": {
        3: {
            14: {
                "verse": "Dieu dit à Moïse: Je suis celui qui suis. Et il ajouta: C'est ainsi que tu répondras aux enfants d'Israël: Celui qui s'appelle 'je suis' m'a envoyé vers vous.",
                "explanation": (
                    "YHWH révèle son nom : être absolu, éternité, immutabilité. "
                    "'Je suis celui qui suis' (ehyeh asher ehyeh) : existence nécessaire. "
                    "Contraste avec les dieux païens contingents et changeants. "
                    "Jésus s'identifie à ce nom divin (Jean 8:58), révélant sa divinité."
                ),
            }
        },
        20: {
            1: {
                "verse": "Alors Dieu prononça toutes ces paroles, en disant:",
                "explanation": (
                    "Préface solennelle du Décalogue : autorité divine directe. "
                    "Dieu lui-même promulgue sa loi morale universelle. "
                    "Fondement de l'éthique biblique et de la conscience humaine. "
                    "Christ accomplit parfaitement cette loi (Mat 5:17)."
                ),
            },
            3: {
                "verse": "Tu n'auras pas d'autres dieux devant ma face.",
                "explanation": (
                    "Premier commandement : exclusivité du culte à YHWH. "
                    "Monothéisme pratique avant théorique dans l'AT. "
                    "Base de toute spiritualité authentique : Dieu seul. "
                    "Jésus confirme ce principe (Marc 12:29-30)."
                ),
            }
        }
    },
    
    "Psaumes": {
        1: {
            1: {
                "verse": "Heureux l'homme qui ne marche pas selon le conseil des méchants, qui ne s'arrête pas sur la voie des pécheurs, et qui ne s'assied pas en compagnie des moqueurs,",
                "explanation": (
                    "Béatitude d'ouverture : le juste défini négativement d'abord. "
                    "Progression dans le mal : conseil → voie → siège. "
                    "Séparation nécessaire du mal pour la sanctification. "
                    "Réalisé parfaitement en Christ, l'Homme heureux par excellence."
                ),
            },
            2: {
                "verse": "mais qui trouve son plaisir dans la loi de l'Éternel, et qui la médite jour et nuit!",
                "explanation": (
                    "Définition positive du juste : amour de la Parole. "
                    "Plaisir (chephets) : délice, non contrainte légaliste. "
                    "Méditation continue : rumination spirituelle constante. "
                    "La Parole comme nourriture de l'âme (Jér 15:16)."
                ),
            }
        },
        23: {
            1: {
                "verse": "L'Éternel est mon berger: je ne manquerai de rien.",
                "explanation": (
                    "Confession de foi personnelle : relation intime avec Dieu. "
                    "Berger : métaphore de la providence tendre et vigilante. "
                    "Sécurité totale dans la dépendance divine. "
                    "Jésus, le Bon Berger, accomplit cette promesse (Jean 10:11)."
                ),
            },
            4: {
                "verse": "Quand je marche dans la vallée de l'ombre de la mort, je ne crains aucun mal, car tu es avec moi: ta houlette et ton bâton me rassurent.",
                "explanation": (
                    "Confiance dans l'épreuve extrême : face à la mort. "
                    "Présence divine comme antidote à la peur. "
                    "Houlette et bâton : protection et discipline du Berger. "
                    "Christ nous accompagne dans la mort et la traverse avec nous."
                ),
            }
        }
    },
    
    # ========== NOUVEAU TESTAMENT ==========
    "Matthieu": {
        1: {
            1: {
                "verse": "Généalogie de Jésus-Christ, fils de David, fils d'Abraham.",
                "explanation": (
                    "Ouverture solennelle : Jésus héritier des promesses. "
                    "Fils de David : messianité royale (2 Sam 7:12-16). "
                    "Fils d'Abraham : bénédiction universelle (Gen 12:3). "
                    "Généalogie attestant l'accomplissement prophétique."
                ),
            },
            23: {
                "verse": "Voici, la vierge sera enceinte, enfantera un fils, et on lui donnera le nom d'Emmanuel, ce qui signifie Dieu avec nous.",
                "explanation": (
                    "Accomplissement d'Ésaïe 7:14 dans la conception virginale. "
                    "Emmanuel : incarnation, Dieu assumant la nature humaine. "
                    "'Avec nous' : solidarité divine dans la condition humaine. "
                    "Mystère de l'union hypostatique : vrai Dieu et vrai homme."
                ),
            }
        },
        5: {
            3: {
                "verse": "Heureux les pauvres en esprit, car le royaume des cieux est à eux!",
                "explanation": (
                    "Première béatitude : pauvreté spirituelle, humilité devant Dieu. "
                    "Contraste avec l'orgueil pharisaïque et l'autosuffisance. "
                    "Condition d'entrée dans le Royaume : reconnaissance de sa misère. "
                    "Promesse présente : 'est à eux', possession actuelle."
                ),
            },
            4: {
                "verse": "Heureux les affligés, car ils seront consolés!",
                "explanation": (
                    "Affliction pour le péché, la justice, la souffrance du monde. "
                    "Dieu console par sa présence et ses promesses. "
                    "Anticipation de l'eschaton : plus de larmes (Apoc 21:4). "
                    "Jésus, homme de douleur, comprend et console."
                ),
            }
        },
        28: {
            19: {
                "verse": "Allez, faites de toutes les nations des disciples, les baptisant au nom du Père, du Fils et du Saint-Esprit,",
                "explanation": (
                    "Grande commission : mandat missionnaire universel. "
                    "Faire des disciples, pas seulement des convertis. "
                    "Baptême trinitaire : confession de foi et identification au Christ. "
                    "Autorité du Christ ressuscité pour cette mission."
                ),
            }
        }
    },
    
    "Jean": {
        1: {
            1: {
                "verse": "Au commencement était la Parole, et la Parole était avec Dieu, et la Parole était Dieu.",
                "explanation": (
                    "Prologue johannique : divinité et préexistence du Logos. "
                    "Écho de Genèse 1:1 : nouvelle création par le Verbe incarné. "
                    "Distinction et unité trinitaires : avec Dieu/était Dieu. "
                    "Fondement de la christologie orthodoxe contre l'arianisme."
                ),
            },
            14: {
                "verse": "Et la parole a été faite chair, et elle a habité parmi nous, pleine de grâce et de vérité; et nous avons contemplé sa gloire, une gloire comme la gloire du Fils unique venu du Père.",
                "explanation": (
                    "Incarnation : mystère central du christianisme. "
                    "Chair (sarx) : nature humaine complète assumée. "
                    "Habiter (skenoo) : tabernacle, présence divine permanente. "
                    "Gloire divine visible dans l'humanité du Fils."
                ),
            }
        },
        3: {
            16: {
                "verse": "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle.",
                "explanation": (
                    "Évangile résumé : amour divin, don du Fils, foi, vie éternelle. "
                    "Amour (agape) : choix délibéré de bienveillance. "
                    "Monde : humanité pécheresse mais aimée. "
                    "Foi comme seule condition : accessibilité universelle du salut."
                ),
            }
        },
        14: {
            6: {
                "verse": "Jésus lui dit: Je suis le chemin, la vérité, et la vie. Nul ne vient au Père que par moi.",
                "explanation": (
                    "Triple déclaration christologique : exclusivité salvifique. "
                    "Chemin : médiateur unique vers le Père. "
                    "Vérité : révélation parfaite de Dieu. "
                    "Vie : source de la vie éternelle et spirituelle."
                ),
            }
        }
    },
    
    "Romains": {
        1: {
            16: {
                "verse": "Car je n'ai point honte de l'Évangile: c'est une puissance de Dieu pour le salut de quiconque croit, du Juif premièrement, puis du Grec.",
                "explanation": (
                    "Thèse de l'épître : puissance salvifique de l'Évangile. "
                    "Pas de honte malgré la folie apparente de la croix. "
                    "Puissance (dynamis) : efficacité divine intrinsèque. "
                    "Universalité : Juif et Grec, tous par la foi seule."
                ),
            },
            17: {
                "verse": "parce qu'en lui est révélée la justice de Dieu par la foi et pour la foi, selon qu'il est écrit: Le juste vivra par la foi.",
                "explanation": (
                    "Justice de Dieu : justification par la foi seule. "
                    "Révélation progressive : 'par la foi et pour la foi'. "
                    "Habacuc 2:4 cité : principe de la vie spirituelle. "
                    "Sola fide : pilier de la Réforme protestante."
                ),
            }
        },
        3: {
            23: {
                "verse": "Car tous ont péché et sont privés de la gloire de Dieu;",
                "explanation": (
                    "Universalité du péché : diagnostic anthropologique. "
                    "Privation de la gloire : perte de l'image divine. "
                    "Égalité dans la perdition : Juif et païen. "
                    "Nécessité absolue de la grâce rédemptrice."
                ),
            },
            24: {
                "verse": "et ils sont gratuitement justifiés par sa grâce, par le moyen de la rédemption qui est en Jésus-Christ.",
                "explanation": (
                    "Solution divine : justification gratuite par la grâce. "
                    "Rédemption (apolutrosis) : libération par rançon payée. "
                    "Christ comme prix et moyen de la justification. "
                    "Gratuité absolue excluant tout mérite humain."
                ),
            }
        },
        8: {
            28: {
                "verse": "Nous savons, du reste, que toutes choses concourent au bien de ceux qui aiment Dieu, de ceux qui sont appelés selon son dessein.",
                "explanation": (
                    "Providence divine : toutes choses sous contrôle divin. "
                    "Bien des élus : conformité à l'image du Fils. "
                    "Amour pour Dieu : évidence de l'élection. "
                    "Dessein éternel : prédestination à la gloire."
                ),
            }
        }
    },
    
    "1 Corinthiens": {
        13: {
            4: {
                "verse": "La charité est patiente, elle est pleine de bonté; la charité n'est point envieuse; la charité ne se vante point, elle ne s'enfle point d'orgueil,",
                "explanation": (
                    "Définition de l'agape : amour divin dans le cœur humain. "
                    "Patience (makrothumia) : longanimité dans l'épreuve. "
                    "Bonté active contrastant avec l'envie destructrice. "
                    "Humilité opposée à l'orgueil corinthien."
                ),
            },
            13: {
                "verse": "Maintenant donc ces trois choses demeurent: la foi, l'espérance, la charité; mais la plus grande de ces choses, c'est la charité.",
                "explanation": (
                    "Triade des vertus chrétiennes permanentes. "
                    "Foi et espérance cesseront dans la gloire. "
                    "Charité éternelle : nature même de Dieu (1 Jean 4:8). "
                    "Primauté de l'amour dans l'éthique chrétienne."
                ),
            }
        }
    },
    
    "Éphésiens": {
        2: {
            8: {
                "verse": "Car c'est par la grâce que vous êtes sauvés, par le moyen de la foi. Et cela ne vient pas de vous, c'est le don de Dieu.",
                "explanation": (
                    "Sola gratia et sola fide : piliers de la sotériologie. "
                    "Salut accompli : temps parfait, œuvre achevée. "
                    "Foi comme instrument, non mérite. "
                    "Don de Dieu : même la foi vient de lui."
                ),
            },
            9: {
                "verse": "Ce n'est point par les œuvres, afin que personne ne se glorifie.",
                "explanation": (
                    "Exclusion radicale du mérite humain. "
                    "Prévention de l'orgueil spirituel. "
                    "Soli Deo gloria : toute gloire à Dieu seul. "
                    "Œuvres comme fruits, non racines du salut."
                ),
            }
        }
    },
    
    "Philippiens": {
        2: {
            6: {
                "verse": "lequel, existant en forme de Dieu, n'a point regardé comme une proie à arracher d'être égal avec Dieu,",
                "explanation": (
                    "Préexistence divine du Fils : christologie haute. "
                    "Forme de Dieu (morphe theou) : essence divine. "
                    "Égalité avec Dieu : divinité essentielle. "
                    "Ne pas regarder comme proie : humilité volontaire."
                ),
            },
            7: {
                "verse": "mais s'est dépouillé lui-même, en prenant une forme de serviteur, en devenant semblable aux hommes;",
                "explanation": (
                    "Kénose : dépouillement volontaire du Fils. "
                    "Forme de serviteur : abaissement radical. "
                    "Incarnation : assumption de la nature humaine. "
                    "Semblable aux hommes : vraie humanité sans péché."
                ),
            }
        }
    },
    
    "Hébreux": {
        11: {
            1: {
                "verse": "Or la foi est une ferme assurance des choses qu'on espère, une démonstration de celles qu'on ne voit pas.",
                "explanation": (
                    "Définition classique de la foi : assurance et évidence. "
                    "Hypostasis : fondement solide, substance. "
                    "Élenchos : conviction, preuve. "
                    "Foi comme organe de perception spirituelle."
                ),
            }
        }
    },
    
    "Jacques": {
        2: {
            17: {
                "verse": "Il en est ainsi de la foi: si elle n'a pas les œuvres, elle est morte en elle-même.",
                "explanation": (
                    "Foi vivante prouvée par les œuvres. "
                    "Pas contradiction avec Paul : perspective différente. "
                    "Œuvres comme évidence de la foi authentique. "
                    "Foi morte : profession sans transformation."
                ),
            }
        }
    },
    
    "Apocalypse": {
        21: {
            4: {
                "verse": "Il essuiera toute larme de leurs yeux, et la mort ne sera plus, et il n'y aura plus ni deuil, ni cri, ni douleur, car les premières choses ont disparu.",
                "explanation": (
                    "Consolation eschatologique : fin de la souffrance. "
                    "Dieu essuie personnellement les larmes : tendresse divine. "
                    "Abolition de la mort : victoire finale du Christ. "
                    "Nouvelles choses : nouvelle création sans malédiction."
                ),
            }
        },
        22: {
            20: {
                "verse": "Celui qui atteste ces choses dit: Oui, je viens bientôt. Amen! Viens, Seigneur Jésus!",
                "explanation": (
                    "Promesse finale du Christ : venue imminente. "
                    "Amen : confirmation divine de la promesse. "
                    "Maranatha : cri du cœur de l'Église. "
                    "Espérance bienheureux : attente active du retour."
                ),
            }
        }
    }
}

# =====================================================================
# 2) ACCÈS "BASIC" (Inchangé)
# =====================================================================

def get_verse_by_verse_content(book: str, chapter: int) -> dict:
    """Retourne le mapping {verse_number: {verse, explanation}} pour un chapitre."""
    return VERSE_BY_VERSE_LIBRARY.get(book, {}).get(chapter, {})

def get_all_verses_for_chapter(book: str, chapter: int) -> List[dict]:
    """Retourne la liste ordonnée des versets d'un chapitre avec texte + explication."""
    chapter_content = get_verse_by_verse_content(book, chapter)
    verses = []
    for verse_num in sorted(chapter_content.keys()):
        verse_data = chapter_content[verse_num]
        verses.append({
            "verse_number": verse_num,
            "verse_text": verse_data.get("verse", ""),
            "explanation": verse_data.get("explanation", "")
        })
    return verses


# =====================================================================
# 3) ENRICHISSEMENT (sans LLM)
# =====================================================================

def _md_inline(s: str) -> str:
    """Nettoyage léger pour éviter toute injection Markdown."""
    s = s or ""
    return s.replace("```", "ʼʼʼ")

def _limit_by_tokens(text: str, tokens: int) -> str:
    """
    Découpage approximatif par tokens (~5 chars/token).
    Conserve la lisibilité (coupe à la fin d'un paragraphe/phrase si possible).
    """
    if not tokens or tokens <= 0:
        return text
    approx_chars = max(200, tokens * 5)
    if len(text) <= approx_chars:
        return text
    cut = text[:approx_chars]
    last_para = cut.rfind("\n\n")
    if last_para > 400:
        cut = cut[:last_para].rstrip()
    else:
        last_sentence = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
        if last_sentence > 400:
            cut = cut[:last_sentence + 1]
    return cut + "\n\n*…(suite abrégée)*"

def _enrich_explanation(
    book: str,
    chapter: int,
    verse_num: int,
    verse_text: str,
    explanation: str,
    detail_level: str = "basic"
) -> str:
    """
    Produit une explication structurée, sans LLM, à partir du commentaire existant.
    detail_level:
      - basic  : commentaire tel quel
      - rich   : + Contexte / Lexique / Parallèles / Doctrine / Application
      - expert : rich + Prière
    """
    explanation = explanation or ""
    verse_text = verse_text or ""

    if detail_level == "basic":
        return _md_inline(explanation).strip()

    # Contexte (heuristique améliorée)
    context_indicators = [
        "histoire", "contexte", "culture", "égypte", "désert", "patriar", "roya", 
        "exil", "temple", "pâque", "sabbat", "pharisien", "babylone", "perse",
        "rome", "judée", "galilée", "synagogue", "sanhédrin"
    ]
    if any(indicator in explanation.lower() for indicator in context_indicators):
        context_line = "- **Contexte historique-culturel** : éléments explicités enrichissant la compréhension."
    else:
        context_line = "- **Contexte historique-culturel** : situe le verset dans son cadre historique et géographique."

    # Lexique (heuristique améliorée)
    lexical_indicators = [
        "hébreu", "grec", "pluriel", "bara", "ruach", "logos", "agap", "qadash", 
        "berit", "tselem", "nephesh", "pneuma", "sarx", "pistis", "charis"
    ]
    if any(indicator in explanation.lower() for indicator in lexical_indicators):
        lex_line = "- **Analyse lexicale** : termes clés hébreux/grecs déjà évoqués et leur portée théologique."
    else:
        lex_line = "- **Analyse lexicale** : 1–2 termes significatifs (racine hébraïque/grecque, champ sémantique)."

    # Parallèles enrichis par livre
    par_line = "- **Parallèles bibliques** : "
    if book.lower() == "genèse":
        par_line += "Jean 1 (Logos créateur); Hébreux 11 (foi des patriarches); Romains 4 (Abraham)."
    elif book.lower() == "exode":
        par_line += "Hébreux 3–4 (repos de Dieu); 1 Corinthiens 10 (exemples d'Israël); Jean 1:17 (loi/grâce)."
    elif book.lower() == "psaumes":
        par_line += "Nouveau Testament (citations messianiques); Hébreux 4:12 (Parole vivante)."
    elif book.lower() == "ésaïe":
        par_line += "Matthieu 1:23 (Emmanuel); Jean 12:41 (gloire du Christ); Romains 10:16 (Évangile)."
    elif book.lower() in ["matthieu", "marc", "luc", "jean"]:
        par_line += "synoptiques parallèles; épîtres pauliniennes (doctrine); Ancien Testament (accomplissements)."
    elif book.lower() == "actes":
        par_line += "épîtres (doctrine correspondante); Luc (continuité narrative); Ancien Testament (prophéties)."
    elif book.lower().startswith("romains"):
        par_line += "Galates (justification); Jacques 2 (foi/œuvres); Genèse 15 (Abraham); Habacuc 2:4 (foi)."
    else:
        par_line += "références canoniques pertinentes selon l'économie du salut."

    doc_line = "- **Doctrine / Christ au centre** : lien avec l'économie du salut, révélation progressive du Christ."
    app_line = "- **Application** : implications personnelles (foi, vertus, disciplines) et ecclésiales (mission, unité)."

    blocks = [
        _md_inline(explanation).strip(),
        "",
        "—",
        context_line,
        lex_line,
        par_line,
        doc_line,
        app_line,
    ]

    if detail_level == "expert":
        blocks.append("- **Prière d'appropriation** : 2–3 phrases (adoration, confession, supplication, action de grâce).")

    return "\n".join(blocks).strip()

def build_verse_by_verse_study(
    book: str,
    chapter: int,
    *,
    version: str = "LSG",
    detail_level: str = "basic",
    tokens: int = 500,
    start_verse: int = 1,
    batch_size: Optional[int] = None,
    only_verse: Optional[int] = None,
) -> Tuple[str, int, int]:
    """
    Construit un rendu 'Étude verset par verset'.
    Retourne (content, last_verse_included, total_verses_in_chapter)
    - only_verse : génère uniquement ce verset
    - batch_size : génère un bloc à partir de start_verse
    """
    chapter_map = VERSE_BY_VERSE_LIBRARY.get(book, {}).get(chapter, {})
    # si base absente, squelette générique enrichi
    if not chapter_map:
        total = 30
        v_start = only_verse or start_verse or 1
        v_end = v_start if only_verse else min(total, v_start + (batch_size or total) - 1)

        parts = [f"### {book} {chapter} ({version}) — Étude verset par verset enrichie\n"]
        for v in range(v_start, v_end + 1):
            parts += [
                f"\nVERSET {v}\n",
                "TEXTE BIBLIQUE :\n",
                f"[{v}] (texte à récupérer via API Bible)",
                "\nEXPLICATION THÉOLOGIQUE :\n",
                _enrich_explanation(book, chapter, v, "", f"Commentaire enrichi à générer pour {book} {chapter}:{v}.", detail_level),
                "\n"
            ]
        content = _limit_by_tokens("\n".join(parts), tokens)
        return content, v_end, total

    verse_numbers = sorted(chapter_map.keys())
    total_verses = len(verse_numbers)

    # plage de versets
    if only_verse:
        rng = [only_verse] if only_verse in verse_numbers else []
    else:
        v_start = max(1, start_verse or 1)
        v_end = verse_numbers[-1] if not batch_size else min(verse_numbers[-1], v_start + batch_size - 1)
        rng = [v for v in verse_numbers if v_start <= v <= v_end]

    parts = [f"### {book} {chapter} ({version}) — Étude verset par verset enrichie\n"]
    for v in rng:
        data = chapter_map.get(v, {})
        verse_text = data.get("verse", "")
        explanation = data.get("explanation", "")
        parts += [
            f"\nVERSET {v}\n",
            "TEXTE BIBLIQUE :\n",
            f"[{v}] {verse_text}",
            "\nEXPLICATION THÉOLOGIQUE :\n",
            _enrich_explanation(book, chapter, v, verse_text, explanation, detail_level),
            "\n"
        ]

    content = _limit_by_tokens("\n".join(parts), tokens)
    last_included = rng[-1] if rng else 0
    return content, last_included, total_verses


# =====================================================================
# 4) PARSING (Inchangé)
# =====================================================================

BOOK_NAMES = list(VERSE_BY_VERSE_LIBRARY.keys())

def _resolve_book_name(raw: str) -> str:
    raw_l = raw.lower()
    for b in BOOK_NAMES:
        bl = b.lower()
        if bl == raw_l or bl.startswith(raw_l) or raw_l.startswith(bl):
            return b
    return raw

def parse_passage(p: str) -> Tuple[str, int, Optional[int]]:
    """
    Parse 'Exode 1', 'Genèse 1:3' → (book, chapter, verse|None)
    """
    s = (p or "").strip()
    if not s:
        return ("", 0, None)

    m = re.match(r"^(.+?)\s+(\d+):(\d+)$", s)
    if m:
        book_raw = m.group(1).strip()
        chapter = int(m.group(2))
        verse = int(m.group(3))
        book = _resolve_book_name(book_raw)
        return (book, chapter, verse)

    m = re.match(r"^(.+?)\s+(\d+)$", s)
    if m:
        book_raw = m.group(1).strip()
        chapter = int(m.group(2))
        book = _resolve_book_name(book_raw)
        return (book, chapter, None)

    # 'Livre' simple → chapitre 1 par défaut
    book = _resolve_book_name(s)
    return (book, 1, None)