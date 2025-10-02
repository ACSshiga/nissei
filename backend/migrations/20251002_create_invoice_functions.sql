-- 請求書作成のストアドプロシージャ（トランザクション保証）
CREATE OR REPLACE FUNCTION create_invoice_with_items(
    p_invoice_number VARCHAR(50),
    p_issue_date DATE,
    p_total_amount DECIMAL(12,2),
    p_status VARCHAR(50),
    p_items JSONB
) RETURNS UUID AS $$
DECLARE
    v_invoice_id UUID;
    v_item JSONB;
BEGIN
    -- 請求書を作成
    INSERT INTO invoices (invoice_number, issue_date, total_amount, status)
    VALUES (p_invoice_number, p_issue_date, p_total_amount, p_status)
    RETURNING id INTO v_invoice_id;

    -- 明細を一括作成
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        INSERT INTO invoice_items (
            invoice_id,
            management_no,
            machine_no,
            actual_hours,
            sort_order
        ) VALUES (
            v_invoice_id,
            (v_item->>'management_no')::VARCHAR,
            (v_item->>'machine_no')::VARCHAR,
            (v_item->>'actual_hours')::DECIMAL,
            (v_item->>'sort_order')::INTEGER
        );
    END LOOP;

    RETURN v_invoice_id;
END;
$$ LANGUAGE plpgsql;
