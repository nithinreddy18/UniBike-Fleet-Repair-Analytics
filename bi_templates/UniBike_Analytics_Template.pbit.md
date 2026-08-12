[Power BI Template Placeholder]

Since Power BI Templates (.pbit/.pbix) are proprietary binary/XML formats that require Windows Power BI Desktop to generate properly, this file serves as a placeholder.

To create the Power BI Dashboard for UniBike Analytics:

1. Open Power BI Desktop.
2. Click "Get Data" -> "PostgreSQL database".
3. Enter the connection details:
   - Server: `localhost` (or your Docker host IP)
   - Database: `unibike_db`
   - Data Connectivity mode: Import (or DirectQuery if preferred)
4. Authenticate using Database credentials:
   - Username: `unibike`
   - Password: `unibike_password`
5. Select the following tables:
   - `bikes`
   - `work_orders`
   - `inventory`
6. Create relationships (if not auto-detected):
   - `bikes.id` (1) <-> (*) `work_orders.bike_id`
7. Build Visuals:
   - MTTR (Mean Time To Repair): Calculate difference between `work_orders.created_at` and `work_orders.resolved_at`.
   - Inventory Levels: Bar chart of `inventory.part_name` by `inventory.quantity`, with a conditional formatting threshold line based on `inventory.threshold`.
8. Save as a `.pbit` (Power BI Template) file in this directory for distribution to AStA members.
