import json
import streamlit as st
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re

@dataclass
class Question:
    id: int
    question: str
    level: str
    category: str

class QueryGuidance:
    def __init__(self, json_path: str = "utils/questionbank.json"):
        """Initialize the Query Guidance system."""
        self.questions: List[Question] = []
        self._load_questions(json_path)
        
    def _load_questions(self, json_path: str) -> None:
        """Load and parse questions from the JSON file."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            for category_group in data:
                level = category_group['level']
                category = category_group['category']
                for q in category_group['questions']:
                    self.questions.append(Question(
                        id=q['id'],
                        question=q['question'],
                        level=level,
                        category=category
                    ))
        except Exception as e:
            st.error(f"Error loading questions: {str(e)}")
            self.questions = []

    def filter_questions(self, query: str, max_suggestions: int = 2) -> List[Question]:
        """Filter questions based on user input."""
        if not query:
            # Return a diverse set of initial questions
            selected_questions = []
            levels = ['Expert', 'Users']  # Reduced to just two levels
            for level in levels:
                level_questions = [q for q in self.questions if q.level == level]
                if level_questions:
                    selected_questions.append(level_questions[0])
                if len(selected_questions) >= max_suggestions:
                    break
            return selected_questions[:max_suggestions]
        
        # Convert query to lowercase for case-insensitive matching
        query = query.lower()
        
        # Score each question based on relevance
        scored_questions: List[Tuple[float, Question]] = []
        for q in self.questions:
            score = self._calculate_relevance_score(q, query)
            if score > 0:
                scored_questions.append((score, q))
        
        # Sort by score and return top matches
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        return [q for _, q in scored_questions[:max_suggestions]]

    def _calculate_relevance_score(self, question: Question, query: str) -> float:
        """Calculate relevance score for a question based on the query."""
        q_text = question.question.lower()
        
        # Exact match gets highest score
        if query == q_text:
            return 1.0
            
        # Contains full query as substring
        if query in q_text:
            return 0.8
            
        # Check for word matches
        query_words = set(re.findall(r'\w+', query))
        question_words = set(re.findall(r'\w+', q_text))
        
        matching_words = query_words.intersection(question_words)
        if matching_words:
            return 0.5 * len(matching_words) / len(query_words)
            
        return 0.0

    def render_query_cards(self, key: str = "query_guidance", is_landing: bool = True) -> Tuple[str, str]:
        """Render floating query cards in the main interface."""
        # Add custom CSS for the floating cards
        st.markdown("""
        <style>
        .query-cards {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 20px 0;
        }
        .query-card {
            background: rgba(32, 33, 35, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex: 1 1 calc(33.333% - 12px);
            min-width: 250px;
            backdrop-filter: blur(10px);
        }
        .query-card:hover {
            background: rgba(52, 53, 65, 0.9);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .query-text {
            color: #E5E5E5;
            font-size: 14px;
            margin: 0;
            line-height: 1.4;
        }
        .category-badge {
            display: inline-block;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 12px;
            margin-bottom: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: #A0A0A0;
        }
        .search-container {
            position: relative;
            margin: 20px 0;
        }
        .search-input {
            width: 100%;
            padding: 12px 48px;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(32, 33, 35, 0.7);
            color: white;
            font-size: 16px;
            backdrop-filter: blur(10px);
        }
        .search-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #A0A0A0;
        }
        
        /* Add styles for form submission */
        .input-form {
            margin-bottom: 20px;
        }
        .input-form textarea {
            padding-right: 40px !important;
        }
        .execute-button {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #E5E5E5;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            z-index: 100;
        }
        </style>
        
        <script>
        // Handle Enter key in textarea
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey && e.target.matches('textarea')) {
                e.preventDefault();
                e.target.form.requestSubmit();
            }
        });
        </script>
        """, unsafe_allow_html=True)

        # Create the search input with different layouts for landing and chat
        if is_landing:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form(key=f"{key}_form", clear_on_submit=True):
                    query = st.text_area(
                        "",
                        placeholder="Ask anything... (Press Enter to execute)",
                        key=f"{key}_input",
                        label_visibility="collapsed",
                        height=68
                    )
                    submitted = st.form_submit_button("Execute", type="primary")
        else:
            with st.form(key=f"{key}_form", clear_on_submit=True):
                query = st.text_area(
                    "",
                    placeholder="Ask anything... (Press Enter to execute)",
                    key=f"{key}_input",
                    label_visibility="collapsed",
                    height=68
                )
                submitted = st.form_submit_button("Execute", type="primary")

        # Get filtered suggestions
        suggestions = self.filter_questions(query)
        
        if suggestions:
            st.markdown('<div class="query-cards">', unsafe_allow_html=True)
            
            for suggestion in suggestions:
                card_html = f"""
                <div class="query-card">
                    <div class="query-content">
                        <div class="category-badge">{suggestion.level} • {suggestion.category}</div>
                        <p class="query-text">{suggestion.question}</p>
                    </div>
                    <button class="execute-button" onclick="
                        var input = document.querySelector('#{key}_input');
                        if (input) {{
                            input.value = '{suggestion.question}';
                            input.form.requestSubmit();
                        }}">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6 0V12M0 6H12" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </button>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        return query if submitted else "", None

    def get_question_by_id(self, question_id: int) -> Question:
        """Retrieve a question by its ID."""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None