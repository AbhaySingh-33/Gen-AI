import gradio as gr
from gradio import ChatMessage
from app import Agent
import time

agent = Agent()

THINKING_FRAMES = [
    "🧠 Thinking",
    "🧠 Thinking ·",
    "🧠 Thinking · ·",
    "🧠 Thinking · · ·",
    "⚙️ Processing your request",
    "⚙️ Processing your request ·",
    "⚙️ Processing your request · ·",
    "🔍 Analyzing",
    "🔍 Analyzing ·",
    "🔍 Analyzing · ·",
    "🔍 Analyzing · · ·",
    "🤖 Working on it",
    "🤖 Working on it ·",
    "🤖 Working on it · ·",
    "✨ Almost there",
    "✨ Almost there ·",
    "✨ Almost there · ·",
]

def chat(message, history):
    history = history or []
    history = history + [
        ChatMessage(role="user", content=message),
        ChatMessage(role="assistant", content="🧠 Thinking ·")
    ]
    yield history, ""

    # Animate the thinking bubble while agent runs in background
    import threading
    result_holder = {}

    def run_agent():
        result_holder["result"] = agent.process_message(message)

    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()

    frame_idx = 0
    while thread.is_alive():
        history[-1] = ChatMessage(role="assistant", content=THINKING_FRAMES[frame_idx % len(THINKING_FRAMES)])
        yield history, ""
        frame_idx += 1
        time.sleep(0.35)

    thread.join()
    result = result_holder["result"]

    if "error" in result:
        raw = result.get("raw", "")
        response = f"❌ {result['error']}" + (f"\n\n**Raw model output:**\n```\n{raw}\n```" if raw else "")
    elif result.get("step") == "output":
        response = f"🤖 {result.get('content')}"
    else:
        response = str(result)

    history[-1] = ChatMessage(role="assistant", content=response)
    yield history, ""

with gr.Blocks(css="""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .gradio-container {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
        background-attachment: fixed !important;
    }
    
    .message-row {
        border-radius: 16px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        backdrop-filter: blur(10px) !important;
        animation: slideIn 0.3s ease-out !important;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user .message-row {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3) !important;
    }
    
    .bot .message-row {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
    }
    
    button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    .input-container {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    textarea, input {
        background: transparent !important;
        color: white !important;
        border: none !important;
    }
    
    textarea::placeholder, input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    .chatbot {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.3) !important;
    }
    
    .example-btn {
        background: rgba(102, 126, 234, 0.2) !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    .example-btn:hover {
        background: rgba(102, 126, 234, 0.4) !important;
        transform: scale(1.02) !important;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.8); }
    }
    
    .glow-effect {
        animation: glow 2s ease-in-out infinite;
    }
""") as demo:
    
    gr.HTML("""
    <div style='text-align: center; padding: 40px 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); border-radius: 24px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);'>
        <div style='display: inline-block; animation: float 3s ease-in-out infinite;'>
            <h1 style='color: white; font-size: 3em; margin: 0; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>✨ Cursor-Lite AI Agent</h1>
        </div>
        <p style='color: rgba(255,255,255,0.9); font-size: 1.3em; margin-top: 15px; font-weight: 500;'>Your intelligent coding assistant powered by Mistral AI 🚀</p>
        <div style='display: flex; justify-content: center; gap: 15px; margin-top: 20px; flex-wrap: wrap;'>
            <span style='background: rgba(102, 126, 234, 0.3); padding: 8px 16px; border-radius: 20px; color: white; font-size: 0.9em; border: 1px solid rgba(102, 126, 234, 0.5);'>🔥 Fast</span>
            <span style='background: rgba(118, 75, 162, 0.3); padding: 8px 16px; border-radius: 20px; color: white; font-size: 0.9em; border: 1px solid rgba(118, 75, 162, 0.5);'>🎯 Accurate</span>
            <span style='background: rgba(240, 147, 251, 0.3); padding: 8px 16px; border-radius: 20px; color: white; font-size: 0.9em; border: 1px solid rgba(240, 147, 251, 0.5);'>💡 Smart</span>
        </div>
    </div>
    <style>
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
    </style>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
            <style>
              .cap-card {
                background: linear-gradient(145deg, rgba(91, 108, 255, 0.15) 0%, rgba(123, 75, 227, 0.15) 45%, rgba(79, 156, 255, 0.15) 100%);
                padding: 28px;
                border-radius: 20px;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                position: relative;
                overflow: hidden;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
              }
              .cap-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 16px 50px rgba(102, 126, 234, 0.4);
              }
              .cap-card:before {
                content: "";
                position: absolute;
                inset: -40% 35% auto -20%;
                height: 200px;
                background: radial-gradient(circle, rgba(102, 126, 234, 0.3), rgba(255,255,255,0));
                transform: rotate(-8deg);
                animation: shimmer 4s ease-in-out infinite;
              }
              @keyframes shimmer {
                0%, 100% { opacity: 0.5; }
                50% { opacity: 0.8; }
              }
              .cap-title {
                margin: 0 0 15px 0;
                font-size: 1.4em;
                letter-spacing: 0.3px;
                font-weight: 700;
                position: relative;
                z-index: 1;
              }
              .cap-sub {
                opacity: 0.95;
                margin: 0 0 20px 0;
                font-size: 1em;
                position: relative;
                z-index: 1;
                line-height: 1.5;
              }
              .cap-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
              }
              .cap-badge {
                background: rgba(102, 126, 234, 0.3);
                border: 1px solid rgba(102, 126, 234, 0.5);
                border-radius: 999px;
                padding: 8px 14px;
                font-size: 0.88em;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                font-weight: 500;
              }
              .cap-badge:hover {
                background: rgba(102, 126, 234, 0.5);
                transform: scale(1.05);
              }
              .cap-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                position: relative;
                z-index: 1;
              }
              .cap-item {
                background: rgba(0, 0, 0, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 14px;
                padding: 14px 16px;
                font-size: 0.95em;
                line-height: 1.4;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
              }
              .cap-item:hover {
                background: rgba(102, 126, 234, 0.2);
                border-color: rgba(102, 126, 234, 0.4);
                transform: translateX(5px);
              }
              .cap-item b {
                display: block;
                font-size: 1.05em;
                margin-bottom: 4px;
                font-weight: 600;
              }
            </style>
            <div class='cap-card'>
                <h3 class='cap-title'>🚀 Agent Capabilities</h3>
                <p class='cap-sub'>Fast, local-first tooling with web search and command execution.</p>
                <div class='cap-badges'>
                  <div class='cap-badge'>⚡ JSON Tooling</div>
                  <div class='cap-badge'>🔍 DuckDuckGo Search</div>
                  <div class='cap-badge'>💻 Code Ops</div>
                  <div class='cap-badge'>📁 File Ops</div>
                </div>
                <div class='cap-grid'>
                  <div class='cap-item'><b>📄 File I/O</b>Read, write, delete</div>
                  <div class='cap-item'><b>🔎 Code Search</b>Fast keyword scans</div>
                  <div class='cap-item'><b>🌐 Web Search</b>DuckDuckGo results</div>
                  <div class='cap-item'><b>⚙️ Commands</b>Run terminal tasks</div>
                  <div class='cap-item'><b>📂 Listing</b>Explore directories</div>
                  <div class='cap-item'><b>🎯 Planning</b>Stepwise actions</div>
                </div>
            </div>
            """)
            
            gr.HTML("""
            <div style='background: linear-gradient(135deg, rgba(118, 75, 162, 0.15) 0%, rgba(102, 126, 234, 0.15) 100%); padding: 28px; border-radius: 20px; margin-top: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); transition: all 0.3s ease;'>
                <h3 style='color: white; margin-top: 0; font-size: 1.3em; font-weight: 700; margin-bottom: 20px;'>💬 Quick Commands</h3>
                <ul style='color: rgba(255, 255, 255, 0.95); font-size: 1.05em; line-height: 2.2; list-style: none; padding: 0; margin: 0;'>
                    <li style='padding: 10px 15px; background: rgba(102, 126, 234, 0.15); border-radius: 10px; margin-bottom: 10px; border-left: 3px solid #667eea; transition: all 0.3s ease;' onmouseover="this.style.background='rgba(102, 126, 234, 0.3)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(102, 126, 234, 0.15)'; this.style.transform='translateX(0)';">📋 "List all files"</li>
                    <li style='padding: 10px 15px; background: rgba(102, 126, 234, 0.15); border-radius: 10px; margin-bottom: 10px; border-left: 3px solid #764ba2; transition: all 0.3s ease;' onmouseover="this.style.background='rgba(102, 126, 234, 0.3)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(102, 126, 234, 0.15)'; this.style.transform='translateX(0)';">📖 "Read app.py"</li>
                    <li style='padding: 10px 15px; background: rgba(102, 126, 234, 0.15); border-radius: 10px; margin-bottom: 10px; border-left: 3px solid #667eea; transition: all 0.3s ease;' onmouseover="this.style.background='rgba(102, 126, 234, 0.3)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(102, 126, 234, 0.15)'; this.style.transform='translateX(0)';">🌐 "Search web for Python asyncio"</li>
                    <li style='padding: 10px 15px; background: rgba(102, 126, 234, 0.15); border-radius: 10px; margin-bottom: 10px; border-left: 3px solid #764ba2; transition: all 0.3s ease;' onmouseover="this.style.background='rgba(102, 126, 234, 0.3)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(102, 126, 234, 0.15)'; this.style.transform='translateX(0)';">✨ "Create test.py"</li>
                    <li style='padding: 10px 15px; background: rgba(102, 126, 234, 0.15); border-radius: 10px; margin-bottom: 10px; border-left: 3px solid #667eea; transition: all 0.3s ease;' onmouseover="this.style.background='rgba(102, 126, 234, 0.3)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(102, 126, 234, 0.15)'; this.style.transform='translateX(0)';">🔍 "Search for 'function'"</li>
                    <li style='padding: 10px 15px; background: rgba(102, 126, 234, 0.15); border-radius: 10px; border-left: 3px solid #764ba2; transition: all 0.3s ease;' onmouseover="this.style.background='rgba(102, 126, 234, 0.3)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(102, 126, 234, 0.15)'; this.style.transform='translateX(0)';">⚡ "Run ls command"</li>
                </ul>
            </div>
            """)
        
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=550,
                show_label=False,
                avatar_images=(None, "https://em-content.zobj.net/source/twitter/376/robot_1f916.png")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="✨ Ask me anything... (e.g., 'List project files', 'Search web for...', 'Create a file')",
                    show_label=False,
                    scale=9,
                    container=False
                )
                submit = gr.Button("🚀 Send", scale=1, variant="primary")
            
            gr.Examples(
                examples=[
                    "List all files in current directory",
                    "Create a hello.py file with print hello",
                    "Search web for Python asyncio",
                ],
                inputs=msg
            )
    
    gr.HTML("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%); border-radius: 16px; margin-top: 25px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);'>
        <p style='color: rgba(255, 255, 255, 0.95); margin: 0; font-size: 1.05em; font-weight: 500;'>Made with ❤️ using <span style='background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>Gradio</span> & <span style='background: linear-gradient(135deg, #764ba2, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>Mistral AI</span></p>
        <p style='color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0; font-size: 0.9em;'>🌟 Powered by advanced AI technology</p>
    </div>
    """)

    submit.click(chat, [msg, chatbot], [chatbot, msg])
    msg.submit(chat, [msg, chatbot], [chatbot, msg])

if __name__ == "__main__":
    demo.queue()
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="blue",
            neutral_hue="slate",
            font=["Inter", "system-ui", "sans-serif"]
        ).set(
            body_background_fill="*primary_950",
            body_background_fill_dark="*primary_950",
            button_primary_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            button_primary_background_fill_hover="linear-gradient(135deg, #7b8cff 0%, #8b5bb8 100%)",
            button_primary_text_color="white",
            input_background_fill="rgba(255, 255, 255, 0.05)",
            input_border_color="rgba(255, 255, 255, 0.1)",
        )
    )
