import streamlit as st
import json
import os
import secrets
from datetime import date

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

# =========================
# OUTILS
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
# QUESTIONS
# =========================
# Pour ne pas saturer le code, je mets ici des libellés simples.
# Tu peux remplacer chaque "Question AQ X" / "Question EQ X"
# par le texte français exact de tes fichiers AQ_French / EQ-French.

AQ_ITEMS = {i: f"Question AQ {i}" for i in range(1, 51)}
EQ_ITEMS = {i: f"Question EQ {i}" for i in range(1, 61)}

# Échelle de réponse (1 à 4) type Baron-Cohen
ANSWER_LABELS = {
    1: "Tout à fait d’accord",
    2: "Plutôt d’accord",
    3: "Plutôt pas d’accord",
    4: "Pas du tout d’accord",
}

# =========================
# COTATION (VERSION DE TRAVAIL)
# =========================

# Pour l’AQ officiel :
# - chaque item rapporte 1 point si la réponse est « autistique »
#   (définit par la clé AQ originale : soit accord, soit désaccord selon l’item)
# Ici, par défaut, je mets une version *approx* :
#   - items où l’accord va dans le sens d’un trait autistique apparent
#   - items où le désaccord va dans le sens du trait autistique
# 👉 Liste à affiner en t’appuyant sur AQ_Scoring_Key.doc

AGREE_IS_AUTISTIC = {
    # Exemple (à compléter/ajuster) :
    2, 4, 5, 6, 7, 9, 12, 13, 16, 18, 19, 21, 22, 23,
    25, 26, 29, 30, 33, 35, 39, 41, 42, 45, 46, 49
}
# Les autres items seront considérés comme "DISAGREE_IS_AUTISTIC"

def score_aq_approx(aq_answers: dict) -> int:
    """
    AQ ~0–50.
    aq_answers : {item_number: response_int_1_to_4}
    Cotation simplifiée : 1 point si réponse autistique, 0 sinon.
    """
    score = 0
    for item, resp in aq_answers.items():
        if resp is None:
            continue
        if item in AGREE_IS_AUTISTIC:
            if resp in (1, 2):  # accord
                score += 1
        else:
            if resp in (3, 4):  # désaccord
                score += 1
    return score


def score_eq_brut(eq_answers: dict) -> int:
    """
    Score brut EQ : somme des réponses 1–4.
    Ce n’est PAS encore la cotation 0/1/2 de la clé officielle.
    """
    return sum(resp for resp in eq_answers.values() if resp is not None)


# Placeholders si tu veux recoder exactement comme Excel/macro :
def score_aq_officiel(aq_answers: dict) -> int:
    """
    TODO : remplacer score_aq_approx par une cotation EXACTE en utilisant AQ_Scoring_Key.
    Pour l’instant, on renvoie le score approx.
    """
    return score_aq_approx(aq_answers)


def score_eq_officiel(eq_answers: dict) -> int:
    """
    TODO : implémenter la vraie cotation EQ (0–80) à partir de ta clé complète.
    Pour l’instant, on renvoie 0 pour marquer que ce n’est pas fait.
    """
    return 0


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

        submitted = st.form_submit_button("Envoyer mes réponses")

    if submitted:
        # Générer un code patient
        patient_code = generate_code(8)

        payload = {
            "patient_code": patient_code,
            "patient_id": patient_id,
            "sex": sex,
            "dob": dob.isoformat(),
            "test_date": test_date.isoformat(),
            "practitioner_code": practitioner_code,
            "aq_answers": aq_answers,
            "eq_answers": eq_answers,
        }

        save_response(patient_code, payload)

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
        # Optionnel : tu peux aussi filtrer sur un code praticien
        # practitioner_code = st.text_input("Votre code praticien", "")
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

            aq_answers = {int(k): int(v) for k, v in data["aq_answers"].items()}
            eq_answers = {int(k): int(v) for k, v in data["eq_answers"].items()}

            # Scores
            aq_approx = score_aq_approx(aq_answers)
            aq_off = score_aq_officiel(aq_answers)
            eq_brut = score_eq_brut(eq_answers)
            eq_off = score_eq_officiel(eq_answers)

            st.markdown("---")
            st.subheader("Synthèse des scores (version de travail)")

            c1, c2 = st.columns(2)
            with c1:
                st.metric("AQ (approx, 0–50)", aq_approx)
                st.caption(
                    "Cotation approchée (1 point pour chaque réponse « autistique » probable). "
                    "À affiner avec la clé AQ originale."
                )
            with c2:
                st.metric("EQ brut (somme 1–4)", eq_brut)
                st.caption(
                    "Somme brute des réponses EQ (1–4). "
                    "La cotation officielle 0/1/2 reste à implémenter."
                )

            if eq_off != 0 or aq_off != aq_approx:
                st.info(
                    f"Version officielle (si tu la codes plus tard) – AQ: {aq_off}, EQ: {eq_off}"
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

            st.markdown(
                "> ⚙️ Quand tu voudras, on pourra reprendre ensemble la cotation exacte "
                "de l’AQ (clé officielle) et de l’EQ (0–80) et la logique CLASS CLINIC "
                "en reprenant point par point ta macro."
            )
