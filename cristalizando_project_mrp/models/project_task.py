# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectTask(models.Model):
    #Este archivo extiende el modelo 'project.task' de Odoo.
    _inherit = 'project.task'

    # ---Definición de Campos ---
    obra_nr = fields.Char(
        string="Número de Obra",
        related="project_id.obra_nr",
        store=True,  
        readonly=True
    )

    obra_docu_nr = fields.Integer(
        string="Nro. Documento de Obra",
        readonly=True,
        copy=False,
        default=0
    )
    obra_docu_tip = fields.Selection(
        [('orfa', 'OrFa'), ('ormofa', 'OrMoFa'), ('orco', 'OrCo'),
         ('orsein', 'OrSeIn'), ('ormufa', 'OrMuFa'), ('orin', 'OrIn'),
         ('ormoln', 'OrMoIn')],
        string="Tipo de Documento",
        required=True,
        default='orfa'
    )
    obra_docu_fem = fields.Date(
        string="Fecha de Emisión",
        default=fields.Date.context_today
    )

    color_id = fields.Many2one(
        'project.color', 
        string="Color",
        related='project_id.color_proyect',
        store=True,
        readonly=True
    )
    
    lnarti_id = fields.Many2one(
        'project.lnarti', 
        string="Línea de Artículo",
        related='project_id.lnart_proyect',
        store=True,
        readonly=True
    )
    
    obra_tipo_id = fields.Many2one(
        'project.obratipo', 
        string="Tipo de Material",
        related='project_id.obratipo_proyect',
        store=True,
        readonly=True
    )
    
    obra_docu_indi_otro4 = fields.Text(
        string="Detalle de la Orden"
    )
    
    obra_docu_indi_vol = fields.Selection(
        [('0', '0%'),
         ('20', '20%'),
         ('30', '30%'),
         ('40', '40%'),
         ('50', '50%'),
         ('60', '60%')],
        string="Nivel de Daño",
        default='0',
        required=True
    )
    
    obra_docu_fc_cmpr_colo = fields.Date(
        string="Fecha de Compromiso de Entrega"
    )

    obra_docu_estd_id = fields.Many2one(
        'project.obraestado',
        string="Estado de la Orden",
        related='project_id.estado_obra_proyect',
        store=True,
        readonly=True
    )

    obra_docu_fc_renegociada = fields.Date(
        string="Fecha de Entrega Renegociada",
        tracking=True
    )

    estado_interiores_id = fields.Many2one(
        'project.obraestado',
        string="Estado de Interiores"
    )
    estado_perfiles_id = fields.Many2one(
        'project.obraestado',
        string="Estado de Perfiles"
    )
    estado_accesorios_id = fields.Many2one(
        'project.obraestado',
        string="Estado de Accesorios"
    )

    obra_docu_vano_libr_cn = fields.Integer(
        string="Cantidad de Vanos Libres"
    )

    obra_docu_cla_comp = fields.Integer(string="Clasificación de Documento")
    
    # Nota: Estos campos son contenedores para los datos que se importarán desde Excel.(morado y verde)
    #los tiempos los pongo como float por que no se la unidad que van a usar
    tiempo_medicion_obra = fields.Float(string="Tiempo de Medición de Obra")
    tiempo_armado_ot = fields.Float(string="Tiempo de Armado de OT")
    tiempo_corte = fields.Float(string="Tiempo de Corte")
    tiempo_fabricacion = fields.Float(string="Tiempo de Fabricación")
    tiempo_acarreo_materiales = fields.Float(string="Tiempo de Acarreo de Materiales")
    tiempo_insumos = fields.Float(string="Tiempo de Insumos")
    tiempo_transporte_personas = fields.Float(string="Tiempo de Transporte a Obra Personas")
    tiempo_viaticos = fields.Float(string="Tiempo de Viáticos")
    tiempo_colocacion = fields.Float(string="Tiempo de Colocación")
    tiempo_cierre_obra = fields.Float(string="Tiempo de Cierre de Obra")

    currency_id = fields.Many2one(
        'res.currency', 
        related='company_id.currency_id', 
        string="Currency"
    )
    #necesito un campo de divisa
    monto_total_etapa = fields.Monetary(
        string="Monto Total de Etapa",
        currency_field='currency_id'
    )

    ml_producto_terminado = fields.Float(string="ML Producto Terminado")
    m2_producto_terminado = fields.Float(string="M2 Producto Terminado")
    m3_producto_terminado = fields.Float(string="M3 Producto Terminado")

    
    ratio_fabricacion = fields.Float(string="Ratio de Fabricación", digits=(12, 2))
    ratio_colocacion = fields.Float(string="Ratio de Colocación", digits=(12, 2))

    #Ojo aqui preguntar 
    tipo_contenedor_transporte = fields.Selection(
        [('iveco_1', 'IVECO 1'),
         ('iveco_2', 'IVECO 2'),
         ('iveco_3', 'IVECO 3'),
         ('modulo_a', 'MODULO A'),
         ('modulo_b', 'MODULO B')],
        string="Tipo de Contenedor de Transporte"
    )

    cantidad_viajes_contenedor = fields.Float(
        string="Cantidad de Viajes",
        digits=(12, 2)
    )
    
    #Necesitamos saber la capacidad (volumen) de cada tipo de contenedor para calcularlo
    porcentaje_carga = fields.Float(string="Porcentaje de Carga")
    cantidad_hojas = fields.Integer(string="Cantidad de Hojas")
    cantidad_panos_fijos = fields.Integer(string="Cantidad de Paños Fijos")
    cantidad_mosquiteros = fields.Integer(string="Cantidad de Mosquiteros")
    ml_pano_fijo = fields.Float(string="Cantidad de ML de Paño Fijo")


    vendedor_id = fields.Many2one(
        'project.syusro',
        string="Vendedor a Cargo",
        related='project_id.obra_vend_cd',
        store=True,
        readonly=True
    )

    jefe_obra_id = fields.Many2one(
        'project.syusro',
        string="Jefe de Obra",
        related='project_id.obra_jefe_cd',
        store=True,
        readonly=True
    )
    
    tecnico_id = fields.Many2one(
        'project.syusro',
        string="Técnico a Cargo",
        related='project_id.obra_tec_cd',
        store=True,
        readonly=True
        
    )
    capataz_id = fields.Many2one(
        'project.syusro',
        string="Capataz a Cargo",
        related='project_id.obra_capa_cd',
        store=True,
        readonly=True
    )

    responsable_separar_accesorios_id = fields.Many2one(
        'project.syusro',
        string="Responsable de Separar Accesorios"
    )
    
    responsable_separar_perfiles_id = fields.Many2one(
        'project.syusro',
        string="Responsable de Separar Perfiles"
    )
    
    verificacion_legajo_jo_fecha = fields.Datetime(
        string="Verificación Legajo por Jefe de Obra"
    )
    
    verificacion_legajo_capataz_fecha = fields.Datetime(
        string="Verificación Legajo por Capataz"
    )
    
    explicacion_legajo_capataz_fecha = fields.Datetime(
        string="Explicación Legajo a Capataz"
    )
    
    verificacion_carpinteria_jo_fecha = fields.Datetime(
        string="Verificación Carpintería por Jefe de Obra"
    )

    responsable_corte_vidrios_id = fields.Many2one(
        'project.syusro',
        string="Responsable de Corte de Vidrios"
    )
    responsable_armado_dvh_id = fields.Many2one(
        'project.syusro',
        string="Responsable de Armado DVH"
    )
    responsable_entrega_accesorios_id = fields.Many2one(
        'project.syusro',
        string="Responsable de Entrega de Accesorios"
    )
    
    # --- Campos de Datos y Cálculos ---
    obra_docu_indi_kg = fields.Float(
        string="Kg de Orden de Fabricación",
        compute='_compute_kg_orden_trabajo',
        store=True,
        readonly=True,
        digits=(12, 2)
    )

    dias_renegociados = fields.Integer(
        string="Días Renegociados",
        compute='_compute_dias_renegociados',
        store=True
    )
    dias_para_entrega = fields.Integer(
        string="Días Para la Entrega",
        compute='_compute_dias_para_entrega'
    )

    task_line_ids = fields.One2many(
        'project.task.line',
        'task_id',
        string="Insumos Utilizados"
    )
    # --- Campos Booleanos ---
    
    is_nivel_dano_readonly = fields.Boolean(
        string="Nivel Daño es Readonly",
        compute='_compute_is_nivel_dano_readonly'
    )
    
    # ---Lógica de Negocio (Métodos) ---

    @api.depends() 
    def _compute_kg_orden_trabajo(self):
        for task in self:
            task.obra_docu_indi_kg = 0.00 #valor por defecto hasta preguntar

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('obra_docu_fc_cmpr_colo'):
                vals['obra_docu_fc_renegociada'] = vals['obra_docu_fc_cmpr_colo']
                
        tasks = super(ProjectTask, self).create(vals_list)

        for task in tasks:
            if task.project_id:
                task_count = self.search_count([('project_id', '=', task.project_id.id)])
                task.obra_docu_nr = task_count
        
        return tasks

    @api.onchange('obra_docu_tip')
    def _onchange_obra_docu_tip(self):
        """ Propósito: Actualizar la 'Clasificación' en la pantalla en tiempo real. """
        if self.obra_docu_tip and self.obra_docu_tip != 'ormofa':
            self.obra_docu_cla_comp = 1100
        else:
            self.obra_docu_cla_comp = 0

    @api.depends('obra_docu_cla_comp')
    def _compute_is_nivel_dano_readonly(self):
        """
        Calcula si el campo 'Nivel de Daño' debe ser de solo lectura.
        Será readonly (True) si la clasificación es 1100.
        """
        for task in self:
            if task.obra_docu_cla_comp == 1100:
                task.is_nivel_dano_readonly = True
            else:
                task.is_nivel_dano_readonly = False

    @api.depends('obra_docu_fc_cmpr_colo', 'obra_docu_fc_renegociada')
    def _compute_dias_renegociados(self):
        """Calcula la diferencia en días entre la fecha de compromiso y la renegociada."""
        for task in self:
            if task.obra_docu_fc_cmpr_colo and task.obra_docu_fc_renegociada:
                delta = task.obra_docu_fc_renegociada - task.obra_docu_fc_cmpr_colo
                task.dias_renegociados = delta.days
            else:
                task.dias_renegociados = 0

    @api.depends('obra_docu_fc_renegociada')
    def _compute_dias_para_entrega(self):
        """Calcula los días restantes hasta la fecha de entrega renegociada."""
        today = fields.Date.context_today(self)
        for task in self:
            if task.obra_docu_fc_renegociada:
                delta = task.obra_docu_fc_renegociada - today
                task.dias_para_entrega = delta.days
            else:
                task.dias_para_entrega = 0
