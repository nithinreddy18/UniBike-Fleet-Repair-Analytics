import gradio as gr
from src.api.rag_chain import query_assistant


def respond(message, chat_history):
    bot_message, docs = query_assistant(message)

    if docs:
        sources_md = "\n\n<details><summary><b>Source Documents</b></summary>\n\n"
        for i, doc in enumerate(docs):
            source_name = doc.metadata.get("source", f"Doc {i+1}")
            sources_md += f"**{source_name}**:\n{doc.page_content}\n\n---\n"
        sources_md += "</details>"
        bot_message += sources_md

    chat_history.append((message, bot_message))
    return "", chat_history


def create_assistant_tab():
    with gr.Blocks() as tab:
        gr.Markdown("## 🛠️ DIY Repair Assistant")
        gr.Markdown(
            "Ask me how to fix common bicycle issues! My answers are grounded in official maintenance manuals."
        )

        chatbot = gr.Chatbot(
            height=400,
            elem_id="rag-chatbot",
            show_copy_button=True,
            avatar_images=(None, "https://api.iconify.design/fluent-emoji:robot.svg"),
        )

        with gr.Row():
            msg = gr.Textbox(
                label="Your Question",
                placeholder="e.g., How do I adjust the rear derailleur?",
                scale=4,
                elem_id="chat-input",
            )
            gr.ClearButton([msg, chatbot], scale=1)

        msg.submit(respond, [msg, chatbot], [msg, chatbot])

    return tab
