import streamlit as st
from openai import OpenAI
from llama_index import LlamaClient  # Replace with actual Llama SDK import
from claude import ClaudeClient  # Replace with actual Claude SDK import
from fpdf import FPDF
import base64

# Show title and description.
st.title("Create Great Practice Questions booklets for any topic you want to learn!")
st.write(
    "This is a simple chatbot that uses AI models to generate responses. "
    "To use this app, you need to provide an API key for OpenAI, Llama, or Claude."
)

# Ask user for their API key via `st.text_input`.
api_key = st.text_input("API Key", type="password")
if not api_key:
    st.info("Please add your API key to continue.", icon="🗝️")
else:
    # Create a client based on the selected model.
    model = st.selectbox("Select Model", ["OpenAI", "Llama", "Claude"])
    if model == "OpenAI":
        client = OpenAI(api_key=api_key)
    elif model == "Llama":
        client = LlamaClient(api_key=api_key)  # Replace with actual Llama client initialization
    elif model == "Claude":
        client = ClaudeClient(api_key=api_key)  # Replace with actual Claude client initialization

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Hardcoded system prompt
    system_prompt = "You are a helpful assistant that generates practice questions for any topic."

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("Enter the topic for practice questions:"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the selected AI model.
        if model == "OpenAI":
            response = client.Completion.create(
                model="gpt-4",
                prompt=system_prompt + "\n" + "\n".join([m["content"] for m in st.session_state.messages]),
                max_tokens=1500,
                n=1,
                stop=None,
                temperature=0.7,
            ).choices[0].text
        elif model == "Llama":
            response = client.generate(
                prompt=system_prompt + "\n" + "\n".join([m["content"] for m in st.session_state.messages]),
                max_tokens=1500,
                temperature=0.7,
            )
        elif model == "Claude":
            response = client.generate(
                prompt=system_prompt + "\n" + "\n".join([m["content"] for m in st.session_state.messages]),
                max_tokens=1500,
                temperature=0.7,
            )

        # Display the response and store it in session state.
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display the generated book content
        st.subheader("Generated Practice Questions Booklet")
        st.markdown(response)

        # Convert the response to PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, response)

        # Save the PDF to a file
        pdf_output = "practice_questions_booklet.pdf"
        pdf.output(pdf_output)

        # Provide a download link for the PDF
        with open(pdf_output, "rb") as f:
            pdf_data = f.read()
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{pdf_output}">Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)