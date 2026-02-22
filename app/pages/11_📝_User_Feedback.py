"""User Feedback page - Collect and display user feedback.

This page allows users to submit feedback about the AI CFO Dashboard
and stores it in a local SQLite database for analysis.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

import streamlit as st
import pandas as pd

from core.i18n import t
from core.language_selector import render_language_selector
from core.components import render_nvidia_badge

st.set_page_config(
    page_title="User Feedback - AI CFO Dashboard",
    page_icon="📝",
    layout="wide",
)

# Database path
DB_PATH = Path("outputs/feedback.db")


def init_database():
    """Initialize the SQLite database with feedback table."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER,
            feedback_text TEXT NOT NULL,
            email TEXT,
            page_context TEXT,
            user_agent TEXT,
            language TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_feedback(
    category: str,
    feedback_text: str,
    rating: Optional[int] = None,
    email: Optional[str] = None,
    page_context: Optional[str] = None,
    language: str = "EN"
) -> bool:
    """Save feedback to the database.

    Args:
        category: Feedback category (e.g., "Bug", "Feature Request", "General")
        feedback_text: The actual feedback content
        rating: Optional satisfaction rating (1-5)
        email: Optional email for follow-up
        page_context: Optional context about which page the feedback is about
        language: User's language preference

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO feedback (timestamp, category, rating, feedback_text, email, page_context, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat() + "Z",
            category,
            rating,
            feedback_text,
            email,
            page_context,
            language
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving feedback: {e}")
        return False


def get_all_feedback() -> List[Dict[str, Any]]:
    """Retrieve all feedback from the database.

    Returns:
        List of feedback dictionaries
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, category, rating, feedback_text, email, page_context, language
            FROM feedback
            ORDER BY timestamp DESC
        """)

        columns = ["id", "timestamp", "category", "rating", "feedback_text", "email", "page_context", "language"]
        rows = cursor.fetchall()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]
    except Exception:
        return []


def get_feedback_stats() -> Dict[str, Any]:
    """Get feedback statistics.

    Returns:
        Dictionary with feedback statistics
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total = cursor.fetchone()[0]

        # Count by category
        cursor.execute("SELECT category, COUNT(*) FROM feedback GROUP BY category")
        by_category = dict(cursor.fetchall())

        # Average rating
        cursor.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]

        # Recent feedback count (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE datetime(timestamp) > datetime('now', '-7 days')
        """)
        recent = cursor.fetchone()[0]

        conn.close()

        return {
            "total": total,
            "by_category": by_category,
            "avg_rating": avg_rating,
            "recent": recent
        }
    except Exception:
        return {"total": 0, "by_category": {}, "avg_rating": None, "recent": 0}


def main():
    # Initialize database
    init_database()

    # Render language selector and get current language
    lang = render_language_selector()

    st.title("📝 " + ("User Feedback" if lang == "EN" else "Opinie Użytkowników"))
    st.markdown("**" + ("Help us improve the AI CFO Dashboard" if lang == "EN" else "Pomóż nam ulepszyć AI CFO Dashboard") + "**")

    st.divider()

    # Create tabs for feedback form and viewing feedback
    tab1, tab2 = st.tabs([
        "📤 " + ("Submit Feedback" if lang == "EN" else "Wyślij Opinię"),
        "📊 " + ("View Feedback" if lang == "EN" else "Zobacz Opinie")
    ])

    with tab1:
        st.subheader("📬 " + ("Share Your Thoughts" if lang == "EN" else "Podziel się Swoimi Przemyśleniami"))

        if lang == "PL":
            st.markdown("""
            Twoja opinia jest dla nas bardzo ważna! Pomóż nam ulepszyć AI CFO Dashboard,
            dzieląc się swoimi doświadczeniami, sugestiami lub zgłaszając problemy.
            """)
        else:
            st.markdown("""
            Your feedback is very important to us! Help us improve the AI CFO Dashboard
            by sharing your experiences, suggestions, or reporting issues.
            """)

        # Feedback form
        with st.form("feedback_form"):
            # Category selection
            category_options = {
                "EN": ["General Feedback", "Bug Report", "Feature Request", "UI/UX Improvement", "Documentation", "Other"],
                "PL": ["Ogólna Opinia", "Zgłoszenie Błędu", "Prośba o Funkcję", "Poprawa UI/UX", "Dokumentacja", "Inne"]
            }

            category = st.selectbox(
                "Category" if lang == "EN" else "Kategoria",
                options=category_options.get(lang, category_options["EN"]),
                help="Select the type of feedback" if lang == "EN" else "Wybierz typ opinii"
            )

            # Map Polish categories back to English for storage
            category_map = {
                "Ogólna Opinia": "General Feedback",
                "Zgłoszenie Błędu": "Bug Report",
                "Prośba o Funkcję": "Feature Request",
                "Poprawa UI/UX": "UI/UX Improvement",
                "Dokumentacja": "Documentation",
                "Inne": "Other"
            }
            category_en = category_map.get(category, category)

            # Rating
            st.markdown("**" + ("How satisfied are you with the AI CFO Dashboard?" if lang == "EN" else "Jak bardzo jesteś zadowolony z AI CFO Dashboard?") + "**")
            rating = st.slider(
                "Rating" if lang == "EN" else "Ocena",
                min_value=1,
                max_value=5,
                value=4,
                help="1 = Very Dissatisfied, 5 = Very Satisfied" if lang == "EN" else "1 = Bardzo Niezadowolony, 5 = Bardzo Zadowolony"
            )

            # Rating indicators
            rating_labels = {
                "EN": {1: "😞 Very Dissatisfied", 2: "😕 Dissatisfied", 3: "😐 Neutral", 4: "🙂 Satisfied", 5: "😀 Very Satisfied"},
                "PL": {1: "😞 Bardzo Niezadowolony", 2: "😕 Niezadowolony", 3: "😐 Neutralny", 4: "🙂 Zadowolony", 5: "😀 Bardzo Zadowolony"}
            }
            st.caption(rating_labels.get(lang, rating_labels["EN"]).get(rating, ""))

            # Page context
            page_options = {
                "EN": ["General / Not specific", "XML Analysis", "CFO Chat", "Board Memo", "Anomaly Detection", "NL Query", "P&L", "Balance Sheet", "Cash Flow", "Forecasting", "Batch Processing"],
                "PL": ["Ogólne / Nieokreślone", "Analiza XML", "Czat CFO", "Board Memo", "Wykrywanie Anomalii", "Zapytania NL", "RZiS", "Bilans", "Przepływy Pieniężne", "Prognozowanie", "Przetwarzanie Wsadowe"]
            }

            page_context = st.selectbox(
                "Which page is this about?" if lang == "EN" else "Której strony dotyczy ta opinia?",
                options=page_options.get(lang, page_options["EN"]),
                help="Select the page your feedback relates to" if lang == "EN" else "Wybierz stronę, której dotyczy opinia"
            )

            # Main feedback text
            feedback_text = st.text_area(
                "Your Feedback" if lang == "EN" else "Twoja Opinia",
                height=150,
                placeholder="Please describe your feedback in detail..." if lang == "EN" else "Proszę opisać swoją opinię szczegółowo...",
                help="Be as specific as possible - it helps us improve!" if lang == "EN" else "Bądź jak najbardziej konkretny - to pomaga nam się rozwijać!"
            )

            # Optional email
            email = st.text_input(
                "Email (optional - for follow-up)" if lang == "EN" else "Email (opcjonalnie - do kontaktu)",
                placeholder="your.email@example.com",
                help="We may contact you for more details about your feedback" if lang == "EN" else "Możemy się skontaktować w celu uzyskania więcej informacji"
            )

            # Submit button
            submitted = st.form_submit_button(
                "📤 " + ("Submit Feedback" if lang == "EN" else "Wyślij Opinię"),
                type="primary",
                use_container_width=True
            )

            if submitted:
                if not feedback_text.strip():
                    st.error("Please enter your feedback before submitting." if lang == "EN" else "Proszę wprowadzić opinię przed wysłaniem.")
                else:
                    success = save_feedback(
                        category=category_en,
                        feedback_text=feedback_text.strip(),
                        rating=rating,
                        email=email.strip() if email else None,
                        page_context=page_context,
                        language=lang
                    )

                    if success:
                        st.success("🎉 " + ("Thank you for your feedback! We appreciate your input." if lang == "EN" else "Dziękujemy za Twoją opinię! Doceniamy Twój wkład."))
                        st.balloons()
                    else:
                        st.error("Failed to save feedback. Please try again." if lang == "EN" else "Nie udało się zapisać opinii. Proszę spróbować ponownie.")

    with tab2:
        st.subheader("📊 " + ("Feedback Overview" if lang == "EN" else "Przegląd Opinii"))

        # Get stats
        stats = get_feedback_stats()

        # Display stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Feedback" if lang == "EN" else "Łączna Liczba",
                stats["total"]
            )

        with col2:
            avg_rating = stats.get("avg_rating")
            if avg_rating:
                st.metric(
                    "Avg Rating" if lang == "EN" else "Średnia Ocena",
                    f"{avg_rating:.1f} ⭐"
                )
            else:
                st.metric("Avg Rating" if lang == "EN" else "Średnia Ocena", "N/A")

        with col3:
            st.metric(
                "Last 7 Days" if lang == "EN" else "Ostatnie 7 Dni",
                stats.get("recent", 0)
            )

        with col4:
            categories = stats.get("by_category", {})
            bugs = categories.get("Bug Report", 0)
            st.metric(
                "Bug Reports" if lang == "EN" else "Zgłoszenia Błędów",
                bugs
            )

        st.divider()

        # Category breakdown
        if stats.get("by_category"):
            st.subheader("📈 " + ("Feedback by Category" if lang == "EN" else "Opinie według Kategorii"))
            category_df = pd.DataFrame([
                {"Category": k, "Count": v}
                for k, v in stats["by_category"].items()
            ])
            st.bar_chart(category_df.set_index("Category"))

        st.divider()

        # Recent feedback
        st.subheader("📋 " + ("Recent Feedback" if lang == "EN" else "Ostatnie Opinie"))

        feedback_list = get_all_feedback()

        if feedback_list:
            for i, feedback in enumerate(feedback_list[:10]):  # Show last 10
                with st.expander(
                    f"**{feedback['category']}** - {feedback['timestamp'][:10]} - {'⭐' * (feedback['rating'] or 0)}",
                    expanded=(i == 0)
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Feedback:**")
                        st.write(feedback['feedback_text'])

                    with col2:
                        if feedback.get('rating'):
                            st.metric("Rating", f"{feedback['rating']}/5 ⭐")
                        if feedback.get('page_context'):
                            st.caption(f"Page: {feedback['page_context']}")
                        if feedback.get('language'):
                            st.caption(f"Language: {feedback['language']}")

            # Export option
            st.divider()
            if st.button("📥 " + ("Export All Feedback (CSV)" if lang == "EN" else "Eksportuj Wszystkie Opinie (CSV)")):
                df = pd.DataFrame(feedback_list)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name="feedback_export.csv",
                    mime="text/csv"
                )
        else:
            st.info("No feedback submitted yet." if lang == "EN" else "Brak przesłanych opinii.")

    # Footer
    st.divider()
    st.caption("💡 " + ("Your feedback helps us build a better product!" if lang == "EN" else "Twoja opinia pomaga nam tworzyć lepszy produkt!"))

    render_nvidia_badge()


if __name__ == "__main__":
    main()
