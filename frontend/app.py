import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="IntelliSupport",
    page_icon="🎫",
    layout="wide"
)


BACKEND_URL = "http://127.0.0.1:5000"

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        margin-top: 0;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 600;
    }

    .category-box {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .category-text {
        font-size: 26px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown(
    """
    # 🎫 IntelliSupport

    **AI-Powered Support Ticket Management**

    ---
    """
)

page = st.sidebar.radio(
    "Navigate",
    [
        "📩 Customer Portal",
        "🧑‍💻 Agent Dashboard"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "AI Classification Pipeline"
)

st.sidebar.caption(
    "TF-IDF + Linear SVM"
)

st.sidebar.caption(
    "Powered by Flask & MongoDB"
)


if page == "📩 Customer Portal":

    st.markdown(
        '<p class="main-title">🎫 IntelliSupport</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">'
        'AI-powered support ticket classification system'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="section-title">📩 Submit a Support Ticket</p>',
        unsafe_allow_html=True
    )

    st.write(
        "Describe your issue and our AI system will "
        "automatically identify the appropriate support category."
    )

    st.markdown("### Ticket Details")

    subject = st.text_input(
        "Subject",
        placeholder="Example: Payment issue"
    )

    body = st.text_area(
        "Describe your problem",
        placeholder=(
            "Example: I was charged twice for my subscription."
        ),
        height=150
    )

    st.write("")

    if st.button(
        "🚀 Submit Ticket",
        type="primary",
        use_container_width=True
    ):

        if not subject.strip() and not body.strip():

            st.warning(
                "Please enter a subject or describe your problem."
            )

        else:

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/tickets",
                    json={
                        "subject": subject,
                        "body": body
                    },
                    timeout=10
                )

                if response.status_code == 201:

                    result = response.json()

                    ticket = result["ticket"]

                    st.success(
                        "✅ Ticket submitted successfully!"
                    )

                    st.markdown("### 🤖 AI Classification")

                    st.markdown(
                        f"""
                        <div class="category-box">

                        <div>Predicted Category</div>

                        <div class="category-text">
                        🏷️ {ticket['category']}
                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.write(
                        f"**Ticket ID:** `{ticket['id']}`"
                    )

                else:

                    st.error(
                        f"Failed to create ticket. "
                        f"Status code: {response.status_code}"
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "❌ Could not connect to the Flask backend. "
                    "Make sure the Flask server is running."
                )

elif page == "🧑‍💻 Agent Dashboard":

    st.markdown(
        '<p class="main-title">🧑‍💻 Agent Dashboard</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">'
        'Monitor support tickets and AI-generated classifications'
        '</p>',
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 Refresh Tickets",
        use_container_width=False
    ):

        st.rerun()

    try:

        response = requests.get(
            f"{BACKEND_URL}/api/tickets",
            timeout=10
        )

        if response.status_code == 200:

            tickets = response.json()

            if len(tickets) == 0:

                st.info(
                    "📭 No support tickets have been submitted yet."
                )

            else:

                df = pd.DataFrame(tickets)



                if "timestamp" in df.columns:

                    df["timestamp"] = pd.to_datetime(
                        df["timestamp"]
                    ).dt.strftime(
                        "%d %b %Y, %I:%M %p"
                    )


                df = df.rename(
                    columns={
                        "id": "Ticket ID",
                        "subject": "Subject",
                        "body": "Complaint",
                        "category": "AI Category",
                        "timestamp": "Timestamp"
                    }
                )



                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "🎫 Total Tickets",
                        len(df)
                    )

                with col2:

                    st.metric(
                        "🤖 AI Classified",
                        len(df)
                    )

                st.divider()

                st.markdown("### 📋 Submitted Tickets")

                st.dataframe(
                    df[
                        [
                            "Ticket ID",
                            "Subject",
                            "Complaint",
                            "AI Category",
                            "Timestamp"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.error(
                f"Failed to retrieve tickets. "
                f"Status code: {response.status_code}"
            )

    except requests.exceptions.RequestException:

        st.error(
            "❌ Could not connect to the Flask backend. "
            "Make sure the Flask server is running."
        )