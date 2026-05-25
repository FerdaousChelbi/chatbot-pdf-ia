"""
Chatbot Intelligent pour Répondre aux Questions d'un Cours PDF
Application Streamlit avec IA générative
"""

import streamlit as st
import os
from datetime import datetime
from utils.pdf_processor import PDFProcessor
from utils.vector_store import VectorStore
from utils.chat_handler import ChatHandler

# Configuration de la page
st.set_page_config(
    page_title="Chatbot PDF Intelligent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 5px solid #4caf50;
    }
    .source-info {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background-color: #f9f9f9;
        border-radius: 5px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'pdf_loaded' not in st.session_state:
    st.session_state.pdf_loaded = False
if 'current_pdf_name' not in st.session_state:
    st.session_state.current_pdf_name = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# En-tête principal
st.markdown("""
<div class="main-header">
    <h1>📚 Chatbot Intelligent pour Cours PDF</h1>
    <p>Posez vos questions et obtenez des réponses intelligentes basées sur votre document</p>
</div>
""", unsafe_allow_html=True)

# Barre latérale
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.title("🤖 Assistant IA")
    st.markdown("---")
    
    # Upload de PDF
    st.subheader("📄 Charger un document")
    uploaded_file = st.file_uploader("Choisissez un fichier PDF", type="pdf")
    
    if uploaded_file is not None:
        if st.button("📖 Traiter le document"):
            with st.spinner("🔄 Traitement du PDF en cours..."):
                try:
                    # Sauvegarde temporaire
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Extraction du texte
                    processor = PDFProcessor()
                    text = processor.extract_text(temp_path)
                    
                    # Découpage en segments
                    chunks = processor.chunk_text(text)
                    
                    # Création des embeddings et stockage vectoriel
                    vector_store = VectorStore()
                    vector_store.create_index(chunks)
                    
                    st.session_state.vector_store = vector_store
                    st.session_state.pdf_loaded = True
                    st.session_state.current_pdf_name = uploaded_file.name
                    st.session_state.chunks = chunks
                    
                    # Nettoyage
                    os.remove(temp_path)
                    
                    st.success(f"✅ Document chargé avec succès ! {len(chunks)} segments créés.")
                    
                    # Réinitialiser la conversation
                    st.session_state.messages = []
                    st.session_state.conversation_history = []
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {str(e)}")
    
    st.markdown("---")
    
    # Options supplémentaires
    st.subheader("⚙️ Options")
    
    show_sources = st.checkbox("Afficher les sources", value=True)
    auto_summary = st.button("📝 Générer un résumé")
    
    if auto_summary and st.session_state.pdf_loaded:
        with st.spinner("Génération du résumé..."):
            chat_handler = ChatHandler()
            summary = chat_handler.generate_summary(st.session_state.chunks[:5])
            st.info(f"**Résumé du document :**\n\n{summary}")
    
    st.markdown("---")
    
    # Téléchargement de l'historique
    if st.session_state.messages:
        if st.button("💾 Télécharger l'historique"):
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            st.download_button(
                label="📥 Sauvegarder",
                data=history_text,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    st.markdown("---")
    st.caption("🚀 Propulsé par IA générative | Modèle FLAN-T5")

# Zone principale - Chat
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Conversation")
    
    # Affichage des messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Vous :</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Assistant :</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                if show_sources and "sources" in message:
                    st.markdown(f"""
                    <div class="source-info">
                        <strong>📚 Sources :</strong><br>
                        {message["sources"]}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Zone de saisie
    if st.session_state.pdf_loaded:
        user_question = st.text_area("Posez votre question :", key="question_input", height=100)
        
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            send_button = st.button("📤 Envoyer", use_container_width=True)
        with col_btn2:
            clear_button = st.button("🗑️ Effacer la conversation", use_container_width=True)
        
        if clear_button:
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        if send_button and user_question:
            # Ajouter la question de l'utilisateur
            st.session_state.messages.append({"role": "user", "content": user_question})
            st.session_state.conversation_history.append({"role": "user", "content": user_question})
            
            with st.spinner("🤔 Réflexion en cours..."):
                # Recherche des passages pertinents
                relevant_chunks = st.session_state.vector_store.search_similar(user_question, k=3)
                
                # Génération de la réponse
                chat_handler = ChatHandler()
                response, sources = chat_handler.generate_response(
                    user_question, 
                    relevant_chunks,
                    st.session_state.conversation_history[-5:]  # Contexte des 5 derniers messages
                )
                
                # Ajouter la réponse
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "sources": sources
                })
                st.session_state.conversation_history.append({"role": "assistant", "content": response})
            
            st.rerun()
    else:
        st.info("📌 Veuillez charger un document PDF dans la barre latérale pour commencer.")

with col2:
    st.subheader("📊 Informations")
    
    if st.session_state.pdf_loaded:
        st.success(f"**Document actif :**\n{st.session_state.current_pdf_name}")
        st.info(f"**Nombre de segments :** {len(st.session_state.chunks) if hasattr(st.session_state, 'chunks') else 0}")
        st.info(f"**Messages échangés :** {len(st.session_state.messages)}")
        
        # Exemples de questions
        st.markdown("---")
        st.subheader("💡 Exemples de questions")
        questions_examples = [
            "Quels sont les points clés de ce document ?",
            "Pouvez-vous résumer le chapitre 1 ?",
            "Quelle est la définition du concept principal ?",
            "Expliquez-moi la partie la plus importante."
        ]
        
        for q in questions_examples:
            if st.button(q, key=q):
                # Auto-remplir la question
                st.session_state.question_input = q
    else:
        st.warning("⚠️ Aucun document chargé")
        st.markdown("""
        **Instructions :**
        1. 📁 Chargez un fichier PDF
        2. ⚙️ Attendez le traitement
        3. 💬 Posez vos questions
        4. 📚 Obtenez des réponses précises
        """)

# Pied de page
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎓 Projet pédagogique - Chatbot Intelligent avec IA Générative | Support multilingue | Recherche sémantique</p>
</div>
""", unsafe_allow_html=True)