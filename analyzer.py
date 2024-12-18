# import & dependencies


# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# functions

def fetch_user_stats(username: str) -> Optional[Dict]:
    """Fetch user statistics from TypeRacer API."""
    pass

def fetch_data(player_id: str, universe: str, n: int, before_id: str = None) -> Optional[List[Dict[str, Any]]]:
    """Fetch data from TypeRacer API with improved error handling"""
    pass

def save_to_database(data: List[Dict[str, Any]], player_id: str, db_name: str = "racer_data.db") -> None:
    """Save fetched data to SQLite database"""
    pass

def load_data_from_db(db_path: str = "racer_data.db") -> Optional[pd.DataFrame]:
    """Load data from SQLite database"""
    pass

def generate_code(df: pd.DataFrame, user_question: str) -> str:
    """
    Generate code via Claude API by prompting the prompt.py function custom_prompt()
    The question and dataframe is attached to the prompt from the custom_prompt() function
    """

    pass

def extract_code_block(response: str) -> Optional[str]:
    """Extract code block from Claude's response and return code"""
    pass

def execute_code_safely(code: str, df: pd.DataFrame) -> Tuple[bool, str, str]:
    """
    Execute code in a safe environment with proper setup to see if it generated code has a plot/figure or not
    the safe execution uses all the variable_mapper.py and plotting.py file for execution
    """
    pass

def regenerate_code_with_error(df: pd.DataFrame, question: str, error_message: str, modified_code: str = None) -> str:
    """
    Regenerate code with error context via Claude API
    The prompt is attached to the code from the prompt.py file
    the function used is custom_prompt_with_error()
    """
    pass

def main():
 
 
    
    # Sidebar for data input and stats
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        if st.session_state.connected_username is None:
            st.header("Connect Database")
            username = st.text_input("Username:", placeholder="e.g., 'user123'")
            
            if st.button("Connect", key="connect_button"):
                if username:
                    user_stats = fetch_user_stats(username)
                    if user_stats:
                        # Get total completed games from user stats
                        total_games = user_stats['tstats']['cg']
                        # Fetch all available games
                        data = fetch_data(
                            player_id=f"tr:{username}", 
                            universe="play",
                            n=total_games,
                            before_id=str(total_games)
                        )
                        if data:
                            st.session_state.df = load_data_from_db()
                            st.session_state.user_stats = user_stats
                            st.session_state.connected_username = username
                            st.rerun()
        else:
            st.header("TypeRacer Stats")
            
            if st.session_state.user_stats:
                stats = st.session_state.user_stats['tstats']
                
                # Display user stats in cards using style.css classes
                st.markdown("""
                    <div class="stats-card">
                        <div class="stats-value">{:.1f}</div>
                        <div class="stats-label">Average WPM</div>
                    </div>
                """.format(stats['wpm']), unsafe_allow_html=True)
                
                st.markdown("""
                    <div class="stats-card">
                        <div class="stats-value">{:.1f}</div>
                        <div class="stats-label">Recent Average WPM</div>
                    </div>
                """.format(stats['recentAvgWpm']), unsafe_allow_html=True)
                
                st.markdown("""
                    <div class="stats-card">
                        <div class="stats-value">{:.1f}</div>
                        <div class="stats-label">Best WPM</div>
                    </div>
                """.format(stats['bestGameWpm']), unsafe_allow_html=True)
                
                st.markdown("""
                    <div class="stats-card">
                        <div class="stats-value">{}</div>
                        <div class="stats-label">Games Completed</div>
                    </div>
                """.format(stats['cg']), unsafe_allow_html=True)
                
                if st.button("Update Stats"):
                    user_stats = fetch_user_stats(st.session_state.connected_username)
                    if user_stats:
                        # Get total completed games from user stats
                        total_games = user_stats['tstats']['cg']
                        # Fetch all available games
                        data = fetch_data(
                            player_id=f"tr:{st.session_state.connected_username}", 
                            universe="play",
                            n=total_games,
                            before_id=str(total_games)
                        )
                        if data:
                            st.session_state.df = load_data_from_db()
                            st.session_state.user_stats = user_stats
                            st.rerun()
            
            if st.button("Disconnect"):
                st.session_state.connected_username = None
                st.session_state.user_stats = None
                st.session_state.df = None
                st.session_state.has_asked_question = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    # Main content area
    if st.session_state.df is None:
        # Welcome screen with centered query input
        st.markdown("<h1 style='text-align: center; margin-top: 40px;'>TypeRacer Analytics</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2em; color: #A0A0A0; margin-bottom: 40px;'>Where typing insights begin</p>", unsafe_allow_html=True)
        
        # Display query cards in landing layout
        query, selected_question = st.session_state.query_guidance.render_query_cards(is_landing=True)
    else:
        # MAIN CHAT INTERFACE STARTS HERE (DONT DELETE THIS EVER)
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        
        # Query input first
        query, selected_question = st.session_state.query_guidance.render_query_cards(is_landing=False)
        
        # Display Generated Results
        if st.session_state.chat_history:
            for entry in st.session_state.chat_history:
                if entry.get('figure'):
                    st.pyplot(entry['figure'])
                    plt.close()
                if entry.get('output'):
                    st.markdown(f"""
                        <div style='padding: 16px; border-radius: 12px; margin: 10px 0; 
                        background-color: rgba(52, 53, 65, 0.7);'>
                            <pre style='margin: 0; white-space: pre-wrap; color: #E5E5E5;'>{entry['output']}</pre>
                        </div>
                    """, unsafe_allow_html=True)
                if entry.get('error'):
                    st.markdown(f"""
                        <div style='padding: 16px; border-radius: 12px; margin: 10px 0; 
                        background-color: rgba(220, 53, 69, 0.3);'>
                            <b style='color: #dc3545;'>Error:</b> 
                            <span style='color: #E5E5E5;'>{entry['error']}</span>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Handle query execution
    execute_query = None
    if query and query.strip():
        execute_query = query
    elif selected_question:
        execute_query = selected_question
        
    if execute_query and st.session_state.df is not None:
        with st.spinner("Analyzing..."):
            response = generate_code(st.session_state.df, execute_query)
            code = extract_code_block(response)
            
            if code:
                success, output, modified_code = execute_code_safely(code, st.session_state.df)
                
                # Create output container
                output_container = st.empty()
                
                # Log the attempt
                st.session_state.eval_logger.log_entry(
                    question=execute_query,
                    original_code=code,
                    modified_code=modified_code,
                    error=None if success else output,
                    figure=plt.gcf() if plt.get_fignums() else None,
                    claude_response=response,
                    execution_success=success
                )
                
                if not success:
                    with output_container:
                        st.error(f"Analysis failed: {output}")
                    
                    st.info("Attempting to fix...")
                    new_response = regenerate_code_with_error(
                        st.session_state.df, execute_query, output, modified_code
                    )
                    new_code = extract_code_block(new_response)
                    
                    if new_code:
                        success2, output2, modified_code2 = execute_code_safely(new_code, st.session_state.df)
                        
                        # Log the retry attempt
                        st.session_state.eval_logger.log_entry(
                            question=execute_query,
                            original_code=new_code,
                            modified_code=modified_code2,
                            error=None if success2 else output2,
                            figure=plt.gcf() if plt.get_fignums() else None,
                            claude_response=new_response,
                            execution_success=success2
                        )
                        
                        if success2:
                            with output_container:
                                if plt.get_fignums():
                                    st.pyplot(plt.gcf())
                                    plt.close()
                                if output2:
                                    st.code(output2)
                        else:
                            with output_container:
                                st.error("Could not fix the analysis")
                else:
                    with output_container:
                        if plt.get_fignums():
                            st.pyplot(plt.gcf())
                            plt.close()
                        if output:
                            st.code(output)
                
                # Store the result for future reference
                chat_entry = {}
                if success:
                    if plt.get_fignums():
                        chat_entry['figure'] = plt.gcf()
                    if output:
                        chat_entry['output'] = output
                else:
                    chat_entry['error'] = output
                
                st.session_state.chat_history = [chat_entry] if chat_entry else []
    elif execute_query:
        st.warning("Please connect to your TypeRacer data first using the sidebar.")

if __name__ == "__main__":
    main() 