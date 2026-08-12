import gradio as gr
from src.ui.tabs.ticketing import create_ticketing_tab
from src.ui.tabs.assistant import create_assistant_tab
from src.ui.tabs.kpi import create_kpi_tab
from src.core.config import settings

def main():
    custom_css = """
    /* Mobile-first touch targets */
    #bike-id-input input, #issue-type-input select, #desc-input textarea, #submit-ticket-btn {
        min-height: 48px !important;
        font-size: 16px !important; /* Prevents iOS zoom */
        border-radius: 0 !important; /* Sharp geometric edges */
    }
    
    /* Rose Bikes Premium Aesthetic: Monochromatic + Red Accent */
    .gradio-container { max-width: 900px !important; font-family: 'Inter', sans-serif !important; }
    
    /* High contrast CTA buttons */
    button.primary { 
        background: #e53935 !important; /* Rose Bikes Red */
        color: white !important; 
        text-transform: uppercase;
        font-weight: 800 !important;
        letter-spacing: 0.05em;
        border: none !important;
        border-radius: 0 !important; /* Sharp edges */
        transition: background 0.2s ease-in-out;
    }
    button.primary:hover {
        background: #b71c1c !important;
    }
    
    /* High contrast status colors */
    .status-available { color: #000000 !important; font-weight: 900; }
    .status-broken { color: #e53935 !important; font-weight: 900; }
    """

    theme = gr.themes.Monochrome(
        primary_hue="red",
        secondary_hue="neutral",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        radius_size=gr.themes.sizes.radius_none,
    )
    
    with gr.Blocks(theme=theme, css=custom_css, title="UniBike Analytics") as demo:
        gr.Markdown("# 🚲 UniBike Fleet & Repair Analytics")
        
        with gr.Tabs():
            with gr.TabItem("🎫 QR Ticketing"):
                ticketing_tab, bike_id_input = create_ticketing_tab()
                
            with gr.TabItem("🤖 DIY Assistant"):
                create_assistant_tab()
                
            with gr.TabItem("📈 KPI Dashboard (Admin)"):
                create_kpi_tab()

        # Inject JS to extract ?bike_id= from URL on load
        demo.load(
            None, 
            inputs=[], 
            outputs=[bike_id_input], 
            js="() => { const params = new URLSearchParams(window.location.search); return params.get('bike_id') || ''; }"
        )

    # The requirements mention securing the admin tab using auth. 
    # Since Gradio's built-in auth applies to the entire app, we launch the entire app with auth.
    # For a real public deployment, FastAPI sub-mounting would be used.
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        auth=[(settings.gradio_admin_username, settings.gradio_admin_password.get_secret_value())],
        share=False
    )

if __name__ == "__main__":
    main()
