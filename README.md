# Warehouse_Management_System (WMS).
  A lightweight, CLI-based Warehouse Management System built with Python and MySQL. This application features role-based access control, 
  real-time stock updates, order dispatch workflows, supplier tracking, and reporting.

---

## Features

- **Authentication & Security**
  - Role-based dashboard (Admin vs. Staff).
  - Secure credential checks & password modification.
- **Product & Inventory Management**
  - CRUD operations for inventory items.
  - Category search and warehouse location tracking.
- **Supplier Tracking**
  - Manage supplier details and assign products to suppliers.
- **Stock Movements**
  - Automatic inventory adjustments for Stock-In / Stock-Out.
  - Movement transaction logs (`Stock_History`).
  - Prevention of negative stock levels.
- **Order Management**
  - Pending, Dispatched, and Cancelled order states.
  - Safe dispatch verification ensuring stock availability.
- **Reports & Analytics**
  - Total inventory valuation.
  - Low-stock warning thresholds.
  - Real-time stock movement audits.

---

## Database Schema Highlights

   - Users: Stores authentication details and assigned roles (admin, staff).

   - Products: Inventory items linked via foreign keys to suppliers and locations.

   - Suppliers: Contact information for active suppliers.

   - Orders: Customer purchase requests tracking workflow status.

   - Stock_History: Audit table logging every inward/outward item movement.

---

## Default Login Credentials:

   - The SQL setup script creates two default user accounts:

        Role  |  Username  |  Password

        Admin |  admin     |  admin123    
        Staff |   staff    |   staff123

  ---  
