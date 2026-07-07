# Database Schema

This document outlines the PostgreSQL database schema for the Retail Intelligence Platform.

## Schemas
1. **staging**: Used for landing raw extracted data.
2. **warehouse**: Stores the core Star Schema entities.
3. **metadata**: Stores pipeline metadata and data quality metrics.
4. **analytics**: (Implicitly created/managed by Spark or Analytics operators) Stores pre-aggregated views and reports.

## Warehouse Star Schema Diagram

```mermaid
erDiagram
    customers ||--o{ orders : places
    products ||--o{ orders : contains
    orders ||--|| payments : has
    orders ||--|| shipping : has
    products ||--o{ inventory : stored_in
    customers ||--o{ reviews : writes
    products ||--o{ reviews : receives
    customers ||--o{ website_events : generates

    customers {
        varchar customer_id PK
        varchar first_name
        varchar last_name
        varchar email
        varchar phone
        varchar gender
        date date_of_birth
        varchar city
        varchar state
        varchar country
        varchar zipcode
        timestamp signup_date
        boolean is_active
        varchar customer_segment
        integer customer_age
        integer customer_tenure_days
    }

    products {
        varchar product_id PK
        varchar product_name
        varchar category
        varchar brand
        varchar supplier
        decimal cost_price
        decimal selling_price
        decimal profit_margin
        decimal weight
        decimal rating
        date launch_date
        boolean is_active
        varchar sku
        boolean low_margin_flag
        decimal profit
    }

    orders {
        varchar order_id PK
        varchar customer_id FK
        timestamp order_date
        varchar product_id FK
        integer quantity
        decimal unit_price
        decimal discount
        decimal tax
        decimal shipping_cost
        varchar payment_id
        varchar shipping_id
        varchar order_status
        decimal total_amount
        integer order_year
        integer order_month
        integer order_quarter
        decimal discount_percentage
        decimal order_value
        integer items_count
    }

    payments {
        varchar payment_id PK
        varchar order_id FK
        varchar payment_method
        varchar payment_status
        timestamp transaction_time
        decimal amount
    }

    shipping {
        varchar shipping_id PK
        varchar order_id FK
        varchar carrier
        varchar tracking_number
        timestamp dispatch_date
        timestamp delivery_date
        varchar shipping_status
        varchar delivery_city
    }

    inventory {
        varchar inventory_id PK
        varchar product_id FK
        varchar warehouse
        integer current_stock
        integer reorder_level
        timestamp last_updated
        varchar warehouse_city
        varchar inventory_status
    }

    reviews {
        varchar review_id PK
        varchar customer_id FK
        varchar product_id FK
        integer rating
        varchar review_title
        text review_text
        timestamp review_date
        boolean verified_purchase
        varchar review_sentiment
    }

    website_events {
        varchar event_id PK
        varchar customer_id FK
        varchar event_type
        timestamp event_timestamp
        text page_url
    }
```
