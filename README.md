# 📦 Courier Management System (Django-based)

## 🔧 Project Overview
This is a web-based Courier Management System built using Django. It allows efficient management of:
- Clients
- Service Providers
- Shipments
- Billing and Invoicing

It supports Excel import/export, automatic bill generation, and a print-ready invoice system.

---

## 🧩 Core Modules & Pages

### 1. Clients Management
- **`clients.html`**: Displays all clients with options to view, edit, and delete.
- **`addclient.html`**: Form to add a new client with:
  - Client name, GST number, email, phone, fuel surcharge %, address.

### 2. Service Providers
- **`providers.html`**: Lists all providers.
  - Modal form to add new provider with name, contact person, phone, email.

### 3. Shipments
- **`addshipment.html`**: Form to add shipment with inputs like:
  - Date, Document No, Client, Provider, Destination, Weight, Travel By, Service Type, Item Type, etc.
  - Below form: Recent shipments with Edit/Delete options.

- **`shipments.html`**: Lists all shipments with filters:
  - Filter by date, document no, client, provider.
  - Options to download sample Excel and upload bulk data.

- **`update-shipment.html`**: Pre-filled form to update existing shipment details.

### 4. Billing System
- **`bill.html`**: Manage all bills with:
  - List of all bills showing subtotal, GST, fuel, total, and related client.
  - Modal to create new bill with:
    - Client selection
    - Bill date and period
    - Dynamic shipment list fetch
    - Fuel & GST rate

- **`bill-preview.html`**: Professional tax invoice format (printable). Includes:
  - Shipment details
  - Subtotal, Fuel Charges, GST (CGST + SGST)
  - Total amount and payment info

- **`show_bill.html`**: Another printable format of the tax invoice.

---

## 💡 Layout & Structure
- **`base.html`**: Master layout template with `{% block 'main' %}` for injecting page-specific content.
- Includes common elements via `header.html` and `footer.html`.

---

## 🔄 Dynamic Features
- JavaScript for:
  - Fetching shipments by client during bill creation.
  - Auto-filling fuel surcharge and GST.
  - Select-all shipments checkbox.

---

## ✅ Requirements
- Django backend to supply views, URLs, context data.
- Bootstrap 5 and FontAwesome for frontend UI/UX.
- Proper URL and view setup for CRUD and data-fetching APIs.

---

## 📌 Note
- All forms use Django CSRF protection and built-in form validation.
- All invoice views are styled for printing.
