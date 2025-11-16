import streamlit as st
import json
import os
import secrets
from datetime import date
import smtplib
from email.mime.text import MIMEText

# =========================
# CONFIG GÉNÉRALE
# =========================

st.set_page_config(
    page_title="AQ + EQ en ligne",
    page_icon="🧩",
    layout="wide",
)

DATA_DIR = "data_aq_eq"
os.makedirs(DATA_DIR, exist_ok=True)

NOTIFICATION_EMAIL = "beatricemilletre@gmail.com"  # destinataire des notifications


# =========================
# OUTILS FICHIERS
# =========================

def generate_code(n_chars: int = 8) -> str:
    """Génère un code patient pseudo-aléatoire."""
    return secrets.token_hex(n_chars // 2).upper()


def save_response(patient_code: str, payload: dict):
    path = os.path.join(DATA_DIR, f"{patient_code}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_response(patient_code: str):
    path = os.path.join(DATA_DIR, f"{patient_code}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# OUTIL EMAIL
# =========================

def send_email_notification(patient_code: str, payload: dict):
    """
    Envoie un mail à Béatrice lorsqu'un questionnaire est rempli.
    ATTENTION : nécessite une config SMTP dans st.secrets["smtp"] :

    [smtp]
    HOST = "smtp.votre_fournisseur"
    PORT = 465
    USER = "votre_login"
    PASSWORD = "votre_mot_de_passe"
    FROM = "adresse@expediteur.com"
    """
    try:
        smtp_conf = st.secrets["smtp"]
    except Exception:
        # Aucune config SMTP -> on ne fait rien
        return

    subject = f"Nouveau questionnaire AQ/EQ – code patient {patient_code}"
    body_lines = [
        "Un nouveau questionnaire AQ/EQ a été rempli.",
        "",
        f"Code patient : {patient_code}",
        f"Identifiant (saisi) : {payload.get('patient_id', '')}",
        f"Sexe : {payload.get('sex', '')}",
        f"Date de naissance : {payload.get('dob', '')}",
        f"Date de passation : {payload.get('test_date', '')}",
        f"Code praticien saisi : {payload.get('practitioner_code', '')}",
        "",
        "Les réponses détaillées sont disponibles dans l’espace praticien de l’app.",
    ]
    msg = MIMEText("\n".join(body_lines), _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_conf.get("FROM", smtp_conf.get("USER", "no-reply@example.com"))
    msg["To"] = NOTIFICATION_EMAIL

    try:
        with smtplib.SMTP_SSL(smtp_conf["HOST"], int(smtp_conf["PORT"])) as server:
            server.login(smtp_conf["USER"], smtp_conf["PASSWORD"])
            server.send_message(msg)
    except Exception:
        # On évite d'afficher une erreur au patient
        st.sidebar.warning("⚠️ Notification email non envoyée (problème SMTP).")


# =========================
# QUESTIONS
# =========================

AQ_ITEMS = {
    1: "Je préfère réaliser des activités avec d’autres personnes plutôt que seul(e).",
    2: "Je préfère tout faire continuellement de la même manière.",
    3: "Quand j’essaye d’imaginer quelque chose, il est très facile de m’en représenter une image mentalement.",
    4: "Je suis fréquemment tellement absorbé(e) par une chose que je perds tout le reste de vue.",
    5: "Mon attention est souvent attirée par des bruits discrets que les autres ne remarquent pas.",
    6: "Je fais habituellement attention aux numéros de plaques d’immatriculation ou à d’autres types d’informations de ce genre.",
    7: "Les gens me disent souvent que ce que j’ai dit était impoli, même quand je pense moi que c’était poli.",
    8: "Quand je lis une histoire, je peux facilement imaginer à quoi les personnages pourraient ressembler.",
    9: "Je suis fasciné(e) par les dates.",
    10: "Au sein d’un groupe, je peux facilement suivre les conversations de plusieurs personnes à la fois.",
    11: "Je trouve les situations de la vie en société faciles.",
    12: "J’ai tendance à remarquer certains détails que les autres ne voient pas.",
    13: "Je préfèrerais aller dans une bibliothèque plutôt qu’à une fête.",
    14: "Je trouve facile d’inventer des histoires.",
    15: "Je suis plus facilement attiré(e) par les gens que par les objets.",
    16: "J’ai tendance à avoir des centres d’intérêt très importants. Je me tracasse lorsque je ne peux m’y consacrer.",
    17: "J’apprécie le bavardage en société.",
    18: "Quand je parle, il n’est pas toujours facile pour les autres de placer un mot.",
    19: "Je suis fasciné(e) par les chiffres.",
    20: "Quand je lis une histoire, je trouve qu’il est difficile de me représenter les intentions des personnages.",
    21: "Je n’aime pas particulièrement lire des romans.",
    22: "Je trouve qu’il est difficile de se faire de nouveaux amis.",
    23: "Je remarque sans cesse des schémas réguliers dans les choses qui m’entourent.",
    24: "Je préfèrerais aller au théâtre qu’au musée.",
    25: "Cela ne me dérange pas si mes habitudes quotidiennes sont perturbées.",
    26: "Je remarque souvent que je ne sais pas comment entretenir une conversation.",
    27: "Je trouve qu’il est facile de « lire entre les lignes » lorsque quelqu’un me parle.",
    28: "Je me concentre habituellement plus sur l’ensemble d’une image que sur les petits détails de celle-ci.",
    29: "Je ne suis pas très doué(e) pour me souvenir des numéros de téléphone.",
    30: "Je ne remarque habituellement pas les petits changements dans une situation ou dans l’apparence de quelqu’un.",
    31: "Je sais m’en rendre compte quand mon interlocuteur s’ennuie.",
    32: "Je trouve qu’il est facile de faire plus d’une chose à la fois.",
    33: "Quand je parle au téléphone, je ne suis pas sûr(e) de savoir quand c’est à mon tour de parler.",
    34: "J’aime faire les choses de manière spontanée.",
    35: "Je suis souvent le(la) dernier(ère) à comprendre le sens d’une blague.",
    36: "Je trouve qu’il est facile de décoder ce que les autres pensent ou ressentent juste en regardant leur visage.",
    37: "Si je suis interrompu(e), je peux facilement revenir à ce que j’étais en train de faire.",
    38: "Je suis doué(e) pour le bavardage en société.",
    39: "Les gens me disent souvent que je répète continuellement les mêmes choses.",
    40: "Quand j’étais enfant, j’aimais habituellement jouer à des jeux de rôle avec les autres.",
    41: "J’aime collectionner des informations sur des catégories de choses (types de voitures, d’oiseaux, de trains, de plantes, ...).",
    42: "Je trouve qu’il est difficile de s’imaginer dans la peau d’un autre.",
    43: "J’aime planifier avec soin toute activité à laquelle je participe.",
    44: "J’aime les événements sociaux.",
    45: "Je trouve qu’il est difficile de décoder les intentions des autres.",
    46: "Les nouvelles situations me rendent anxieux(se).",
    47: "J’aime rencontrer de nouvelles personnes.",
    48: "Je suis une personne qui a le sens de la diplomatie.",
    49: "Je ne suis pas très doué(e) pour me souvenir des dates de naissance des gens.",
    50: "Je trouve qu’il est très facile de jouer à des jeux de rôle avec des enfants.",
}

EQ_ITEMS = {
    1: "Je peux facilement dire quand quelqu’un veut entamer une conversation.",
    2: "Je préfère les animaux aux êtres humains.",
    3: "J’essaie de être à la mode.",
    4: "Je trouve difficile d’expliquer aux autres des choses que j’ai comprises facilement et que eux n’ont pas comprises du premier coup.",
    5: "Je rêve la plupart des nuits.",
    6: "J’aime prendre soin des autres.",
    7: "J’essaie de résoudre mes problèmes moi-même plutôt que d’en discuter avec d’autres.",
    8: "Je trouve difficile de savoir ce qu’il faut faire dans les relations sociales.",
    9: "C’est le matin que je suis le(la) plus efficace.",
    10: "On me dit souvent que je vais trop loin quand j’expose mon point de vue dans une discussion.",
    11: "Cela ne m’ennuie pas trop d’être en retard à un rendez-vous fixé à un ami.",
    12: "Les relations sociales sont si difficiles que j’essaie de ne pas m’en soucier.",
    13: "Je ne ferais jamais rien d’illégal même si ce n’est pas très grave.",
    14: "J’ai souvent du mal à juger si quelque chose est grossier ou familier.",
    15: "Dans une conversation, j’ai tendance à me centrer sur mes propres pensées plutôt que sur celles de mon interlocuteur.",
    16: "Je préfère les farces aux jeux de mots.",
    17: "Je vis au jour le jour.",
    18: "Quand j’étais enfant, j’aimais couper des vers de terre pour voir ce qui se passe.",
    19: "Je détecte rapidement si quelqu’un dit une chose qui en signifie une autre.",
    20: "J’ai de solides convictions sur la moralité.",
    21: "Je ne comprends pas comment des choses vexent tant certaines personnes.",
    22: "Il est pour moi facile de me mettre à la place de quelqu’un d’autre.",
    23: "Je pense que les bonnes manières sont la meilleure chose que des parents peuvent apprendre à leurs enfants.",
    24: "J’aime agir sur un coup de tête.",
    25: "Je prédis assez bien le ressenti des autres.",
    26: "Dans un groupe, je repère facilement quand quelqu’un se sent gêné ou mal à l’aise.",
    27: "Si j’offense quelqu’un en parlant, j’estime que c’est son problème et pas le mien.",
    28: "Si quelqu’un me demandait mon avis sur sa coupe de cheveux, je répondrais honnêtement même si elle ne me plaît pas.",
    29: "Je ne comprends pas toujours pourquoi une personne peut être offensée par une remarque.",
    30: "On me dit souvent que je suis imprévisible.",
    31: "En groupe, j’aime être le centre d’intérêt.",
    32: "Voir quelqu’un pleurer ne me touche pas vraiment.",
    33: "J’adore parler politique.",
    34: "Je ne mâche pas mes mots, ce qui est souvent pris pour de la grossièreté même si ce n’est pas mon intention.",
    35: "En général, je comprends facilement les situations sociales.",
    36: "On me dit généralement que je comprends bien les sentiments et les pensées des autres.",
    37: "Quand je discute avec quelqu’un, j’essaie de parler de ses expériences plutôt que des miennes.",
    38: "Ça me bouleverse de voir un animal souffrant.",
    39: "Je suis capable de prendre des décisions sans être influencé(e) par les sentiments des autres.",
    40: "Je ne peux pas me détendre sans avoir fait tout ce que j’avais planifié pour la journée.",
    41: "Je remarque facilement si quelqu’un est intéressé ou ennuyé par ce que je dis.",
    42: "Lorsque je regarde le journal télévisé, je suis triste de voir des personnes qui souffrent.",
    43: "Mes amis me parlent généralement de leurs problèmes car ils disent que je suis très compréhensif(ve).",
    44: "Je peux sentir quand je dérange les autres, même s’ils ne me le disent pas.",
    45: "Je commence souvent de nouveaux passe-temps qui m’ennuient vite et je passe à autre chose.",
    46: "Des fois, on me dit que j’exagère quand je charrie les gens.",
    47: "Je serais bien trop anxieux(se) de monter sur un manège de montagnes russes.",
    48: "On me dit souvent que je suis insensible même si je ne vois pas toujours pourquoi.",
    49: "Si je vois qu’il y a un nouveau venu dans un groupe de personnes, je crois que c’est à elles d’essayer de l’intégrer.",
    50: "D’habitude, je ne m’implique pas émotionnellement lorsque je regarde un film.",
    51: "J’aime être très organisé(e) dans ma vie de tous les jours, et je fais souvent des listes de ce que j’ai à faire.",
    52: "Je peux me mettre à l’écoute du ressenti des autres rapidement et intuitivement.",
    53: "Je n’aime pas prendre de risques.",
    54: "Je peux facilement comprendre ce que quelqu’un veut dire.",
    55: "Je peux deviner si quelqu’un masque ses émotions.",
    56: "Je pèse toujours le pour et le contre avant de prendre une décision.",
    57: "Je n’essaie pas de déchiffrer de façon consciente les règles en jeu dans les situations sociales.",
    58: "Je suis bon(ne) pour prédire ce que quelqu’un va faire.",
    59: "J’ai tendance à m’impliquer émotionnellement dans les problèmes de mes amis.",
    60: "Habituellement, je comprends le point de vue des autres même si je ne le partage pas.",
}

# Échelle de réponse (1 à 4)
ANSWER_LABELS = {
    1: "Tout à fait d’accord",
    2: "Plutôt d’accord",
    3: "Plutôt pas d’accord",
    4: "Pas du tout d’accord",
}

# =========================
# COTATION AQ
# =========================

# Items AQ où l’ACCORD (1 ou 2) = réponse "autistique"
AQ_AGREE_ITEMS = {
    2, 4, 5, 6, 7, 9, 12, 13,
    16, 18, 19, 20, 21, 22, 23,
    26, 33, 35, 39, 41, 42, 43,
    45, 46,
}

def is_aq_autistic(item: int, resp: int) -> bool:
    """True si la réponse va dans le sens 'autistique' pour cet item AQ."""
    if resp is None:
        return False
    if item in AQ_AGREE_ITEMS:
        return resp in (1, 2)  # accord
    else:
        return resp in (3, 4)  # désaccord


def score_aq_officiel(aq_answers: dict) -> int:
    """Cotation officielle AQ (0–50)."""
    return sum(1 for item, resp in aq_answers.items() if is_aq_autistic(item, resp))


# Sous-échelles AQ (10 items chacune)
AQ_SUBSCALES = {
    "A. Compétences sociales": [1, 11, 13, 15, 22, 36, 44, 45, 47, 48],
    "B. Flexibilité / Attention switching": [2, 4, 10, 16, 25, 32, 34, 37, 43, 46],
    "B’. Attention aux détails": [5, 6, 9, 12, 19, 23, 28, 29, 30, 49],
    "C. Communication": [7, 17, 18, 26, 27, 31, 33, 35, 38, 39],
    "D. Imagination": [3, 8, 14, 20, 21, 24, 40, 41, 42, 50],
}

def score_aq_subscales(aq_answers: dict) -> dict:
    """Retourne {nom_sous_échelle: score (0–10)}."""
    subscores = {}
    for name, items in AQ_SUBSCALES.items():
        s = 0
        for item in items:
            resp = aq_answers.get(item)
            if is_aq_autistic(item, resp):
                s += 1
        subscores[name] = s
    return subscores


# =========================
# BLOCS DSM / CLASS CLINIC
# =========================

CLASS_A_ITEMS = AQ_SUBSCALES["A. Compétences sociales"]
CLASS_B_ITEMS = AQ_SUBSCALES["B. Flexibilité / Attention switching"] + AQ_SUBSCALES["B’. Attention aux détails"]
CLASS_C_ITEMS = AQ_SUBSCALES["C. Communication"]
CLASS_D_ITEMS = AQ_SUBSCALES["D. Imagination"]

DSM_A_ITEMS = set(CLASS_A_ITEMS)
DSM_B_ITEMS = set(CLASS_B_ITEMS)
DSM_C_ITEMS = set(CLASS_C_ITEMS)
DSM_D_ITEMS = set(CLASS_D_ITEMS)

def build_dsm_blocks(aq_answers: dict) -> dict:
    """
    Construit les blocs A, B, C, D façon DSM, en listant les items AQ
    cotés dans le sens 'autistique' avec leur texte.
    """
    blocks = {"A": [], "B": [], "C": [], "D": []}

    # Bloc A : interaction sociale
    for item in sorted(DSM_A_ITEMS):
        if is_aq_autistic(item, aq_answers.get(item)):
            blocks["A"].append(f"{AQ_ITEMS[item]} (AQ{item})")

    # Bloc B : comportements / intérêts restreints et répétitifs
    for item in sorted(DSM_B_ITEMS):
        if is_aq_autistic(item, aq_answers.get(item)):
            blocks["B"].append(f"{AQ_ITEMS[item]} (AQ{item})")

    # Bloc C : communication
    for item in sorted(DSM_C_ITEMS):
        if is_aq_autistic(item, aq_answers.get(item)):
            blocks["C"].append(f"{AQ_ITEMS[item]} (AQ{item})")

    # Bloc D : imagination
    for item in sorted(DSM_D_ITEMS):
        if is_aq_autistic(item, aq_answers.get(item)):
            blocks["D"].append(f"{AQ_ITEMS[item]} (AQ{item})")

    return blocks


def compute_class_clinic_counts(aq_answers: dict) -> dict:
    """
    Renvoie les comptes pour la grille CLASS CLINIC :
    { "A": {"name": ..., "required": 3, "observed": n, "max_items": m}, ... }
    """
    sections = {
        "A": {
            "label": "Social",
            "items": CLASS_A_ITEMS,
            "required": 3,
        },
        "B": {
            "label": "Obsessions / intérêts restreints",
            "items": CLASS_B_ITEMS,
            "required": 3,
        },
        "C": {
            "label": "Communication",
            "items": CLASS_C_ITEMS,
            "required": 3,
        },
        "D": {
            "label": "Imagination",
            "items": CLASS_D_ITEMS,
            "required": 1,
        },
    }

    out = {}
    total_obs = 0
    for key, sec in sections.items():
        obs = 0
        for item in sec["items"]:
            if is_aq_autistic(item, aq_answers.get(item)):
                obs += 1
        total_obs += obs
        out[key] = {
            "label": sec["label"],
            "required": sec["required"],
            "observed": obs,
            "max_items": len(sec["items"]),
        }

    out["TOTAL"] = {
        "label": "Total A+B+C+D",
        "required": 10,  # comme dans ton tableau (3+3+3+1)
        "observed": total_obs,
        "max_items": 18,  # max théorique de la grille
    }

    return out


def build_class_clinic_summary(section_counts: dict, prereq_flags: dict) -> str:
    """
    Produit une phrase de synthèse type CLASS CLINIC, sans faire de diagnostic formel.
    section_counts : résultat de compute_class_clinic_counts
    prereq_flags : dict {"E": bool, ..., "I": bool}
    """
    core_ok = all(
        section_counts[s]["observed"] >= section_counts[s]["required"]
        for s in ["A", "B", "C", "D"]
    )
    prereq_ok = all(prereq_flags.values())

    msg_parts = []

    msg_parts.append(
        f"A: Social – {section_counts['A']['observed']} symptômes (≥ {section_counts['A']['required']} requis)."
    )
    msg_parts.append(
        f"B: Obsessions / intérêts restreints – {section_counts['B']['observed']} symptômes (≥ {section_counts['B']['required']} requis)."
    )
    msg_parts.append(
        f"C: Communication – {section_counts['C']['observed']} symptômes (≥ {section_counts['C']['required']} requis)."
    )
    msg_parts.append(
        f"D: Imagination – {section_counts['D']['observed']} symptômes (≥ {section_counts['D']['required']} requis)."
    )
    msg_parts.append(
        f"Total A+B+C+D : {section_counts['TOTAL']['observed']} symptômes (seuil indicatif = {section_counts['TOTAL']['required']})."
    )

    if core_ok and prereq_ok:
        msg_parts.append(
            "L’ensemble des blocs A–D atteint le seuil indicatif, et les prérequis E–I rapportés par le patient sont cochés : "
            "le profil est compatible avec un fonctionnement de type TSA/Asperger, "
            "dans le cadre d’une évaluation clinique globale (ce résultat ne constitue pas un diagnostic à lui seul)."
        )
    elif core_ok and not prereq_ok:
        msg_parts.append(
            "Les blocs A–D atteignent les seuils indicatifs, mais un ou plusieurs prérequis E–I rapportés par le patient ne sont pas remplis "
            "(ou restent incertains). Un diagnostic de TSA doit être envisagé avec prudence et replacé dans le contexte clinique complet."
        )
    elif not core_ok and prereq_ok:
        msg_parts.append(
            "Les prérequis E–I rapportés par le patient sont cochés, mais l’un au moins des blocs A–D n’atteint pas le seuil indicatif. "
            "On peut évoquer des traits du spectre autistique ou des particularités neurodéveloppementales, "
            "sans que les critères complets soient réunis selon cette grille."
        )
    else:
        msg_parts.append(
            "Ni les seuils symptomatiques ni certains prérequis ne sont réunis : "
            "le profil décrit des particularités de fonctionnement, mais ne remplit pas, en l’état, "
            "les critères d’un tableau type TSA selon cette grille."
        )

    return "\n\n".join(msg_parts)


# =========================
# COTATION EQ
# =========================

EQ_EMPATHY_ITEMS = {
    1, 4, 6, 8, 10, 11, 12, 14, 15, 18,
    19, 21, 22, 25, 26, 27, 28, 29, 32, 34,
    35, 36, 37, 38, 39, 41, 42, 43, 44, 46,
    48, 49, 50, 52, 54, 55, 57, 58, 59, 60,
}

EQ_POSITIVE_AGREE = {
    1, 6, 19, 22, 25, 26,
    35, 36, 37, 38,
    41, 42, 43, 44,
    52, 54, 55,
    57, 58, 59, 60,
}
EQ_NEGATIVE_AGREE = EQ_EMPATHY_ITEMS - EQ_POSITIVE_AGREE

def score_eq_officiel(eq_answers: dict) -> int:
    """Cotation officielle EQ (0–80)."""
    score = 0
    for item, resp in eq_answers.items():
        if resp is None or item not in EQ_EMPATHY_ITEMS:
            continue
        if item in EQ_POSITIVE_AGREE:
            if resp == 1:
                score += 2
            elif resp == 2:
                score += 1
        else:
            if resp == 4:
                score += 2
            elif resp == 3:
                score += 1
    return score


# =========================
# UI – CHOIX DU MODE
# =========================

st.title("🧩 AQ + EQ en ligne")

mode = st.sidebar.radio(
    "Mode d’utilisation",
    ("Je suis un répondant (patient / participant)",
     "Je suis le praticien"),
)

# =========================
# MODE RÉPONDANT
# =========================

if mode.startswith("Je suis un répondant"):

    st.header("Passation des questionnaires AQ + EQ")

    with st.form("form_repondant"):

        st.subheader("Informations générales")

        patient_id = st.text_input("Identifiant (initiales ou code fourni)", "")
        sex = st.selectbox("Sexe", ["", "Féminin", "Masculin", "Autre"])
        dob = st.date_input(
            "Date de naissance",
            value=date(2000, 1, 1),
            format="DD/MM/YYYY",
        )
        test_date = st.date_input(
            "Date de passation",
            value=date.today(),
            format="DD/MM/YYYY",
        )
        practitioner_code = st.text_input(
            "Code praticien (fourni par votre psychologue / praticien)",
            "",
        )

        st.markdown("---")
        st.subheader("Questionnaire AQ (50 items)")

        aq_answers = {}
        for i, label in AQ_ITEMS.items():
            aq_answers[i] = st.radio(
                f"{i}. {label}",
                options=list(ANSWER_LABELS.keys()),
                format_func=lambda x, _labels=ANSWER_LABELS: _labels[x],
                horizontal=True,
                key=f"AQ_{i}",
            )

        st.markdown("---")
        st.subheader("Questionnaire EQ (60 items)")

        eq_answers = {}
        for i, label in EQ_ITEMS.items():
            eq_answers[i] = st.radio(
                f"{i}. {label}",
                options=list(ANSWER_LABELS.keys()),
                format_func=lambda x, _labels=ANSWER_LABELS: _labels[x],
                horizontal=True,
                key=f"EQ_{i}",
            )

        st.markdown("---")
        st.subheader("Questions générales sur votre parcours")

        def radio_oui_non(label: str, key: str) -> bool:
            rep = st.radio(label, ["Oui", "Non"], key=key, horizontal=True)
            return rep == "Oui"

        prereq_E = radio_oui_non(
            "Ces difficultés (sociales, de communication, intérêts spécifiques, etc.) sont présentes depuis toujours (depuis l’enfance).",
            "prereq_E",
        )
        prereq_F = radio_oui_non(
            "Ces difficultés ont déjà eu un impact important sur votre vie (isolement, souffrance, échec ou difficultés importantes à l’école / au travail, etc.).",
            "prereq_F",
        )
        prereq_G = radio_oui_non(
            "Dans votre souvenir (ou celui de vos parents), il n’y a pas eu de retard important de langage dans l’enfance.",
            "prereq_G",
        )
        prereq_H = radio_oui_non(
            "Vous n’avez pas eu (à votre connaissance) de trouble spécifique majeur des apprentissages (lecture, écriture, calcul) qui explique à lui seul vos difficultés.",
            "prereq_H",
        )
        prereq_I = radio_oui_non(
            "Vous n’avez jamais présenté de symptômes psychotiques (perte de contact avec la réalité, idées délirantes, hallucinations diagnostiquées par un psychiatre).",
            "prereq_I",
        )

        submitted = st.form_submit_button("Envoyer mes réponses")

    if submitted:
        # Générer un code patient
        patient_code = generate_code(8)

        prereq_flags = {
            "E": prereq_E,
            "F": prereq_F,
            "G": prereq_G,
            "H": prereq_H,
            "I": prereq_I,
        }

        payload = {
            "patient_code": patient_code,
            "patient_id": patient_id,
            "sex": sex,
            "dob": dob.isoformat(),
            "test_date": test_date.isoformat(),
            "practitioner_code": practitioner_code,
            "aq_answers": aq_answers,
            "eq_answers": eq_answers,
            "prereq": prereq_flags,
        }

        save_response(patient_code, payload)
        send_email_notification(patient_code, payload)

        st.success("Merci, vos réponses ont été enregistrées.")
        st.info(
            f"Communiquez **ce code** à votre praticien : **{patient_code}**\n\n"
            "Les résultats détaillés seront discutés avec lui/elle."
        )

# =========================
# MODE PRATICIEN
# =========================

else:
    st.header("Espace praticien")

    with st.form("form_praticien"):
        patient_code = st.text_input("Code patient", "")
        submitted = st.form_submit_button("Charger les résultats")

    if submitted:
        data = load_response(patient_code.strip().upper())
        if data is None:
            st.error("Aucune donnée trouvée pour ce code patient.")
        else:
            st.subheader("Données générales du patient")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Identifiant** : {data.get('patient_id', '')}")
                st.write(f"**Code patient** : {data.get('patient_code', '')}")
                st.write(f"**Sexe** : {data.get('sex', '')}")
            with col2:
                st.write(f"**Date de naissance** : {data.get('dob', '')}")
                st.write(f"**Date de passation** : {data.get('test_date', '')}")
                st.write(f"**Code praticien enregistré** : {data.get('practitioner_code', '')}")

            # Les réponses sont stockées en JSON => clés en str
            aq_answers = {int(k): int(v) for k, v in data["aq_answers"].items()}
            eq_answers = {int(k): int(v) for k, v in data["eq_answers"].items()}

            # Pré-requis remplis par le patient (peut ne pas exister pour d’anciens enregistrements)
            prereq_data = data.get("prereq", {})
            prereq_flags = {
                "E": bool(prereq_data.get("E", False)),
                "F": bool(prereq_data.get("F", False)),
                "G": bool(prereq_data.get("G", False)),
                "H": bool(prereq_data.get("H", False)),
                "I": bool(prereq_data.get("I", False)),
            }

            # Scores
            aq_score = score_aq_officiel(aq_answers)
            eq_score = score_eq_officiel(eq_answers)
            aq_subscores = score_aq_subscales(aq_answers)
            dsm_blocks = build_dsm_blocks(aq_answers)
            class_counts = compute_class_clinic_counts(aq_answers)

            st.markdown("---")
            st.subheader("Synthèse des scores")

            c1, c2 = st.columns(2)
            with c1:
                st.metric("Score AQ (0–50)", aq_score)
                st.caption(
                    "AQ total (cotation officielle). "
                    "Un score ≥ 32 est souvent retrouvé chez les profils TSA/HFA."
                )
            with c2:
                st.metric("Score EQ (0–80)", eq_score)
                st.caption(
                    "EQ total (40 items d’empathie). "
                    "Les scores bas sont associés à une empathie plus faible."
                )

            st.markdown("### Sous-échelles AQ")
            sub_rows = []
            for name, items in AQ_SUBSCALES.items():
                sub_rows.append(
                    {
                        "Sous-échelle": name,
                        "Score": aq_subscores[name],
                        "Max": len(items),
                    }
                )
            st.table(sub_rows)

            st.markdown("### Analyse qualitative – blocs DSM / CLASS CLINIC")

            # Bloc A
            st.markdown("#### A. Trouble qualitatif de l’interaction sociale")
            if dsm_blocks["A"]:
                for phrase in dsm_blocks["A"]:
                    st.markdown(f"- {phrase}")
            else:
                st.markdown("_Aucun item AQ significatif dans ce bloc avec le seuil actuel._")

            # Bloc B
            st.markdown("#### B. Comportements, intérêts et activités restreints, répétitifs et stéréotypés")
            if dsm_blocks["B"]:
                for phrase in dsm_blocks["B"]:
                    st.markdown(f"- {phrase}")
            else:
                st.markdown("_Aucun item AQ significatif dans ce bloc avec le seuil actuel._")

            # Bloc C
            st.markdown("#### C. Troubles qualitatifs de la communication (verbale et non verbale)")
            if dsm_blocks["C"]:
                for phrase in dsm_blocks["C"]:
                    st.markdown(f"- {phrase}")
            else:
                st.markdown("_Aucun item AQ significatif dans ce bloc avec le seuil actuel._")

            # Bloc D
            st.markdown("#### D. Troubles de l’imagination")
            if dsm_blocks["D"]:
                for phrase in dsm_blocks["D"]:
                    st.markdown(f"- {phrase}")
            else:
                st.markdown("_Aucun item AQ significatif dans ce bloc avec le seuil actuel._")

            st.markdown("### Grille CLASS CLINIC – Synthèse quantitative")

            table_rows = []
            for key in ["A", "B", "C", "D"]:
                c = class_counts[key]
                table_rows.append(
                    {
                        "Section": key,
                        "Domaine": c["label"],
                        "Nb requis": c["required"],
                        "Nb observés": c["observed"],
                        "Nb items possibles": c["max_items"],
                    }
                )
            total = class_counts["TOTAL"]
            table_rows.append(
                {
                    "Section": "Total",
                    "Domaine": total["label"],
                    "Nb requis": total["required"],
                    "Nb observés": total["observed"],
                    "Nb items possibles": total["max_items"],
                }
            )
            st.table(table_rows)

            st.markdown("### Pré-requis E–I (réponses du patient)")

            def format_flag(flag: bool) -> str:
                return "✅ Oui" if flag else "❌ Non"

            st.markdown(f"- **E. Présence depuis l’enfance** : {format_flag(prereq_flags['E'])}")
            st.markdown(f"- **F. Impact fonctionnel significatif** : {format_flag(prereq_flags['F'])}")
            st.markdown(f"- **G. Pas de retard majeur du langage** : {format_flag(prereq_flags['G'])}")
            st.markdown(f"- **H. Pas de trouble spécifique majeur des apprentissages** : {format_flag(prereq_flags['H'])}")
            st.markdown(f"- **I. Pas de traits psychotiques** : {format_flag(prereq_flags['I'])}")

            st.markdown("### Synthèse clinique automatique (aide à la réflexion, non diagnostic)")

            summary_text = build_class_clinic_summary(class_counts, prereq_flags)
            st.markdown(summary_text.replace("\n\n", "\n\n---\n\n"))

            st.caption(
                "⚠️ Cette synthèse est un outil d'aide à l'analyse clinique et ne constitue pas un diagnostic en soi. "
                "Elle doit toujours être interprétée dans le cadre d'une évaluation globale (anamnèse, observation clinique, "
                "autres instruments, contexte développemental, etc.)."
            )

            st.markdown("---")
            st.subheader("Réponses détaillées AQ")

            aq_table = []
            for i in sorted(aq_answers.keys()):
                aq_table.append(
                    {
                        "Item": i,
                        "Réponse": ANSWER_LABELS[aq_answers[i]],
                    }
                )
            st.dataframe(aq_table, use_container_width=True)

            st.subheader("Réponses détaillées EQ")

            eq_table = []
            for i in sorted(eq_answers.keys()):
                eq_table.append(
                    {
                        "Item": i,
                        "Réponse": ANSWER_LABELS[eq_answers[i]],
                    }
                )
            st.dataframe(eq_table, use_container_width=True)
