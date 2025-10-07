# custom_stock_history/models/daily_stock_history.py
from odoo import models, fields, tools

class DailyStockHistory(models.Model):
    _name = 'daily.stock.history'
    _description = 'Histórico de Stock Diario (Vista SQL)'
    _auto = False
    _order = 'location_id, product_id, date'

    # --- Campos de la vista ---
    date = fields.Date(string="Fecha", readonly=True)
    product_id = fields.Many2one('product.product', string="Producto", readonly=True)
    category_id = fields.Many2one('product.category', string="Categoría", related='product_id.categ_id', readonly=True)
    location_id = fields.Many2one('stock.location', string="Ubicación", readonly=True)
    uom_id = fields.Many2one('uom.uom', string="UdM", related='product_id.uom_id', readonly=True)
    
    income = fields.Float(string="Ingreso", readonly=True)
    outcome = fields.Float(string="Salida", readonly=True)
    balance = fields.Float(string="Balance", readonly=True, help="Ingreso del día - Salida del día")
    accumulated = fields.Float(string="Acumulado", readonly=True, help="Saldo acumulado del producto en la ubicación")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                WITH daily_moves AS (
                    -- Parte de INGRESOS (movimientos a ubicaciones internas)
                    SELECT
                        (sml.date AT TIME ZONE 'UTC')::date AS date,
                        sml.product_id,
                        sml.location_dest_id AS location_id,
                        SUM(sml.quantity) AS income,
                        0.0 AS outcome
                    FROM
                        stock_move_line sml
                    JOIN
                        stock_location sl_dest ON sml.location_dest_id = sl_dest.id
                    WHERE
                        sml.state = 'done' AND sl_dest.usage = 'internal'
                    GROUP BY
                        1, 2, 3
                    
                    UNION ALL
                    
                    -- Parte de SALIDAS (movimientos desde ubicaciones internas)
                    SELECT
                        (sml.date AT TIME ZONE 'UTC')::date AS date,
                        sml.product_id,
                        sml.location_id AS location_id,
                        0.0 AS income,
                        SUM(sml.quantity) AS outcome
                    FROM
                        stock_move_line sml
                    JOIN
                        stock_location sl_src ON sml.location_id = sl_src.id
                    WHERE
                        sml.state = 'done' AND sl_src.usage = 'internal'
                    GROUP BY
                        1, 2, 3
                ),
                aggregated_moves AS (
                    -- Juntar los ingresos y salidas en una sola línea por día
                    SELECT
                        date,
                        product_id,
                        location_id,
                        SUM(income) as income,
                        SUM(outcome) as outcome,
                        SUM(income) - SUM(outcome) as balance
                    FROM
                        daily_moves
                    GROUP BY
                        date, product_id, location_id
                )
                -- Calcular el acumulado usando una función de ventana
                SELECT
                    row_number() OVER () AS id,
                    am.date,
                    am.product_id,
                    am.location_id,
                    am.income,
                    am.outcome,
                    am.balance,
                    SUM(am.balance) OVER (PARTITION BY am.product_id, am.location_id ORDER BY am.date) AS accumulated
                FROM
                    aggregated_moves am
            )
        """ % (self._table,))