import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database.session import SessionLocal

def get_kpi_data():
    db = SessionLocal()
    try:
        # Load data into pandas
        work_orders_df = pd.read_sql("SELECT * FROM work_orders", db.bind)
        inventory_df = pd.read_sql("SELECT * FROM inventory", db.bind)
        
        # 1. Calculate MTTR (Mean Time to Repair) in days
        mttr_str = "N/A (No tickets)"
        missed_count = 0
        if not work_orders_df.empty:
            resolved_df = work_orders_df[work_orders_df['status'] == 'Resolved']
            if not resolved_df.empty:
                resolved_df['created_at'] = pd.to_datetime(resolved_df['created_at'])
                resolved_df['resolved_at'] = pd.to_datetime(resolved_df['resolved_at'])
                resolved_df['repair_time'] = (resolved_df['resolved_at'] - resolved_df['created_at']).dt.total_seconds() / 86400
                mttr = resolved_df['repair_time'].mean()
                mttr_str = f"{mttr:.1f} days"
            else:
                mttr_str = "N/A (No resolved tickets)"

            open_df = work_orders_df[work_orders_df['status'].isin(['Open', 'In Progress'])]
            if not open_df.empty:
                open_df['created_at'] = pd.to_datetime(open_df['created_at'])
                now = pd.to_datetime('today')
                missed = open_df[(now - open_df['created_at']).dt.total_seconds() > 7 * 86400]
                missed_count = len(missed)

        # Plot 1: Work Order Status Distribution
        if not work_orders_df.empty:
            status_counts = work_orders_df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.bar(status_counts, x='Status', y='Count', title="Work Order Statuses", color='Status', color_discrete_map={"Open": "#ef4444", "In Progress": "#f59e0b", "Resolved": "#22c55e"})
            fig_status.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        else:
            fig_status = go.Figure()
            fig_status.update_layout(title="No Work Orders Found")

        # Plot 2: Inventory Levels
        if not inventory_df.empty:
            fig_inv = px.bar(inventory_df, x='part_name', y='quantity', title="Inventory Levels", labels={'part_name': 'Part', 'quantity': 'Quantity'})
            # Add threshold line logic
            fig_inv.add_trace(go.Scatter(x=inventory_df['part_name'], y=inventory_df['threshold'], mode='lines+markers', name='Threshold', line=dict(color='red', dash='dash')))
            fig_inv.update_layout(margin=dict(l=20, r=20, t=40, b=20), barmode='group')
        else:
            fig_inv = go.Figure()
            fig_inv.update_layout(title="No Inventory Data")

        # Format HTML/Markdown output
        report = f"""
        ### 📊 Fleet Health Overview
        
        **Mean Time to Repair (MTTR):** {mttr_str}  
        **Missed/Stalled Work Orders (> 7 days open):** {missed_count}
        """
        
        return report, fig_status, fig_inv, inventory_df[['part_name', 'quantity', 'threshold']]
    except Exception as e:
        return f"Error loading KPI data: {e}", go.Figure(), go.Figure(), pd.DataFrame()
    finally:
        db.close()

def create_kpi_tab():
    with gr.Blocks() as tab:
        gr.Markdown("## 📈 Admin KPI Dashboard")
        
        with gr.Row():
            refresh_btn = gr.Button("Refresh Data", variant="secondary")
        
        report_output = gr.Markdown(value="Click 'Refresh Data' to load KPIs.")
        
        with gr.Row():
            status_plot = gr.Plot(label="Work Orders")
            inv_plot = gr.Plot(label="Inventory Levels")
            
        inventory_table = gr.Dataframe(headers=["Part Name", "Quantity", "Threshold"], interactive=False)
        
        refresh_btn.click(
            fn=get_kpi_data,
            inputs=[],
            outputs=[report_output, status_plot, inv_plot, inventory_table]
        )
        
    return tab
