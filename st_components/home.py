import streamlit as st
from utils import translate

# Initialisiere den Session State für die Navigation und Click-Zähler
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "clicks_chat" not in st.session_state:
    st.session_state.clicks_chat = 0
if "clicks_quiz" not in st.session_state:
    st.session_state.clicks_quiz = 0
if "clicks_challenge" not in st.session_state:
    st.session_state.clicks_challenge = 0
if "clicks_stats" not in st.session_state:
    st.session_state.clicks_stats = 0


def render_home():
    # Hide Streamlit default elements
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8fafc;
        }
        .block-container {
            padding-top: 1rem;
            max-width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full HTML/CSS Implementation
    st.html(f"""
            <!-- Header -->
				<div id="header-wrapper">
					<div class="container">

						<!-- Banner -->
							<div id="banner">
								<h2><strong>{translate("DGS Training Workshop:", "DGS Ausbildungswerkstatt:")}</strong>
								<br />
                                {translate("Learning with sign language, engaging and interactive", "Lernen mit Gebärden, ansprechend und interaktiv")}</h2>
								<a href="#main-wrapper" class="button large icon solid fa-check-circle">{translate("More info", "Weitere info")}</a>
							</div>

					</div>
				</div>

			<!-- Main Wrapper -->
				<div id="main-wrapper">
					<div class="wrapper style1">
						<div class="inner">

							<!-- Feature 1 -->
								<section class="container box feature1">
									<div class="row">
										<div class="col-12">
											<header class="first major">
												<h2>{translate("Welcome to Your Learning Platform", "Willkommen bei Deinem Lern-Platform")}</h2>
												<p>{translate("specially developed for", "speziell entwickelt für")}
                                                    <strong>{translate("deaf trainees", "gehörlose Auszubildende")}</strong>
                                                    {translate("in the first year of training as skilled worker for", "im ersten Lehrjahr der Fachkraft für")}
                                                    <strong>{translate("Metal Technology", "Metalltechnik")}</strong></p>
											</header>
										</div>
										<div class="col-4 col-12-medium">
											<section>
												<a href="#" class="image featured"><img src="https://imgpx.com/en/w0A1CmPNwSnn.png" alt="" /></a>
												<header class="second icon solid fa-user">
													<h3>{translate("Quick Help", "Schnelle Hilfe")}</h3>
													<p>{translate("Metal technology bot expert", "Metalltechnik bot expert")}</p>
												</header>
											</section>
										</div>
										<div class="col-4 col-12-medium">
											<section>
												<a href="#" class="image featured"><img src="https://imgpx.com/en/BksuQEdKnDqd.png" alt="" /></a>
												<header class="second icon solid fa-cog">
													<h3>{translate("Interactive Learning", "Interaktives Lernen")}</h3>
													<p>{translate("Workshop quiz simulations", "Werkstatt-Quiz-Simulationen")}</p>
												</header>
											</section>
										</div>
										<div class="col-4 col-12-medium">
											<section>
												<a href="#" class="image featured"><img src="https://www.addrc.org/wp-content/uploads/2020/10/asl-icon.png" alt="" /></a>
												<header class="second icon solid fa-chart-bar">
													<h3>{translate("DGS Recognition", "DGS-Erkennung")}</h3>
													<p>{translate("Learn sign language", "Lerne Gebärden")}</p>
												</header>
											</section>
										</div>
										<div class="col-12">
											<p>{translate("Answers questions about the learning material and vocational school - based on the current curricula, framework guidelines and learning materials for inclusive education. Based on the learning fields of the 1st training year, our camera challenge tests your sign language in real time", "Beantwortet Fragen zum Lernstoff und zur Berufsschule - basierend auf den aktuellen Curricula, Rahmenrichtlinien und Lernmaterialien für inklusive Bildung. Basierend auf den Lernfeldern des 1. Ausbildungsjahres usnsere Kamera-Challenge prüft Deine Gebärden in Echtzeit")}</p>
										</div>
									</div>
								</section>

						</div>
					</div>
					<div class="wrapper style2">
						<div class="inner">

							<!-- Feature 2 -->
								<section class="container box feature2">
									<div class="row">
										<div class="col-6 col-12-medium">
											<section>
												<header class="major">
													<h2>{translate("Discover Metal Technology Interactively", "Metalltechnik interaktiv entdecken")}</h2>
													<p>{translate("Learning with chatbot and intelligent hand sign recognition", "Lernen mit Chatbot und intelligenter Handzeichenerkennung")}</p>
												</header>
												<p>{translate("With our learning chatbot, you can explore the basics of metal technology easily and intuitively. The integrated camera recognizes your hand signs and makes operation particularly easy and natural. Step by step, you receive understandable explanations, practical examples and direct feedback on your inputs.", "Mit unserem Lern-Chatbot kannst du die Grundlagen der Metalltechnik einfach und intuitiv erforschen. Die integrierte Kamera erkennt deine Handzeichen und macht so die Bedienung besonders leicht und natürlich. Schritt für Schritt erhältst du verständliche Erklärungen, praktische Beispiele und direkte Rückmeldungen zu deinen Eingaben.")}</p>
											</section>
										</div>
										<div class="col-6 col-12-medium">
											<section>
												<header class="major">
													<h2>{translate("Test Metal Technology Playfully", "Metalltechnik spielerisch prüfen")}</h2>
													<p>{translate("Solve quizzes through hand signs and smart evaluation", "Quiz lösen durch Handzeichen und smarte Auswertung")}</p>
												</header>
												<p>{translate("Test your knowledge in an interactive quiz all about metal technology. Thanks to hand sign recognition, you can conveniently give answers via gestures and receive immediate feedback. The combination of movement, technology and playful learning helps you consolidate content sustainably and clearly recognize your progress.", "Teste dein Wissen in einem interaktiven Quiz rund um die Metalltechnik. Dank der Handzeichenerkennung kannst du Antworten bequem per Gesten geben und erhältst sofortiges Feedback. Die Kombination aus Bewegung, Technik und spielerischem Lernen hilft dir, Inhalte nachhaltig zu festigen und deinen Fortschritt klar zu erkennen.")}</p>
											</section>
										</div>
									</div>
								</section>

							</div>
					</div>
				</div>
		</div>
                    
    """)
    
    # Streamlit Buttons Section
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 Chat", type="primary", use_container_width=True, key="chat_btn"):
            st.session_state.clicks_chat += 1
            st.session_state.page = "Learn Chat"
            st.rerun()
    
    with col2:
        if st.button("🛠️ Werkstatt-Quiz", use_container_width=True, key="quiz_btn"):
            st.session_state.clicks_quiz += 1
            st.session_state.page = "Martins page"
            st.rerun()
    
    # Footer
    st.html("""
    <div class="dgs-container">
        <div class="footer-note">
            <p style="text-align: center; margin-top: 200px;">
            Made with love by Hema, Martin and Wojtek @ WBS - November 2025</p>
        </div>
    </div>
            
    <!-- jQuery -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

    <!-- jQuery Dropotron (dropdown menu plugin) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.dropotron/1.4.3/jquery.dropotron.min.js"></script>
    """)


if __name__ == "__main__":
    render_home()