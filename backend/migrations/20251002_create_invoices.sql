-- 請求書機能のマイグレーション
-- 作成日: 2025-10-02

-- invoices（請求書ヘッダ）
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  year INTEGER NOT NULL,                        -- 年: 2025
  month INTEGER NOT NULL,                       -- 月: 1~12
  status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- 'draft' | 'closed'
  closed_at TIMESTAMP,                          -- 確定日時
  closed_by UUID REFERENCES users(id),          -- 確定者
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(year, month)                           -- 年月でユニーク
);

CREATE INDEX idx_invoices_year_month ON invoices(year, month);
CREATE INDEX idx_invoices_status ON invoices(status);

-- invoice_items（請求書明細）
CREATE TABLE invoice_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id),
  management_no VARCHAR(100) NOT NULL,          -- 管理No
  work_content TEXT NOT NULL,                   -- 委託業務内容（機番）
  total_hours DECIMAL(10,2) NOT NULL,           -- 実工数（時間）
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(invoice_id, project_id)
);

CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_project_id ON invoice_items(project_id);

COMMENT ON TABLE invoices IS '請求書ヘッダ';
COMMENT ON TABLE invoice_items IS '請求書明細';
COMMENT ON COLUMN invoices.status IS 'draft: 下書き, closed: 確定済み';
COMMENT ON COLUMN invoice_items.total_hours IS '該当月の合計工数（時間単位）';
