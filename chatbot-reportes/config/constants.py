"""Catálogos y contrato de datos del reporte ciudadano."""

REPORT_HEADERS = [
    "report_id",
    "received_at",
    "event_at",
    "locality_code",
    "event_type",
    "stolen_item_category",
    "modality",
    "weapon_type",
    "latitude_private",
    "longitude_private",
    "address_private",
    "description_private",
    "source",
    "moderation_status",
    "consent",
    "consent_at",
    "phone_hash",
    "review_notes_private",
]

# Código oficial de localidad usado por Bogotá D.C.
LOCALITIES = {
    "1": ("01", "Usaquén"),
    "2": ("02", "Chapinero"),
    "3": ("03", "Santa Fe"),
    "4": ("04", "San Cristóbal"),
    "5": ("05", "Usme"),
    "6": ("06", "Tunjuelito"),
    "7": ("07", "Bosa"),
    "8": ("08", "Kennedy"),
    "9": ("09", "Fontibón"),
    "10": ("10", "Engativá"),
    "11": ("11", "Suba"),
    "12": ("12", "Barrios Unidos"),
    "13": ("13", "Teusaquillo"),
    "14": ("14", "Los Mártires"),
    "15": ("15", "Antonio Nariño"),
    "16": ("16", "Puente Aranda"),
    "17": ("17", "La Candelaria"),
    "18": ("18", "Rafael Uribe Uribe"),
    "19": ("19", "Ciudad Bolívar"),
    "20": ("20", "Sumapaz"),
}

EVENT_TYPES = {
    "1": ("hurto_consumado", "Hurto consumado"),
    "2": ("intento_hurto", "Intento de hurto"),
}

ITEM_CATEGORIES = {
    "1": ("celular", "Celular"),
    "2": ("dinero_billetera", "Dinero o billetera"),
    "3": ("bicicleta", "Bicicleta"),
    "4": ("motocicleta", "Motocicleta"),
    "5": ("vehiculo", "Vehículo"),
    "6": ("computador_tableta", "Computador o tableta"),
    "7": ("documentos", "Documentos"),
    "8": ("joyas_accesorios", "Joyas o accesorios"),
    "9": ("otro", "Otro"),
    "10": ("no_aplica", "No aplica (intento)"),
}

MODALITIES = {
    "1": ("atraco", "Atraco o intimidación"),
    "2": ("cosquilleo", "Cosquilleo"),
    "3": ("raponazo", "Raponazo"),
    "4": ("engano", "Engaño"),
    "5": ("oportunidad", "Factor de oportunidad"),
    "6": ("halado", "Halado"),
    "7": ("otra", "Otra"),
    "8": ("no_sabe", "No sabe"),
}

WEAPON_TYPES = {
    "1": ("ninguna", "Ninguna"),
    "2": ("arma_blanca", "Arma blanca"),
    "3": ("arma_fuego", "Arma de fuego"),
    "4": ("objeto_contundente", "Objeto contundente"),
    "5": ("otra", "Otra"),
    "6": ("no_sabe", "No sabe"),
}

STATES = {
    "CONSENT": "consent",
    "LOCALITY": "locality",
    "EVENT_TYPE": "event_type",
    "EVENT_AT": "event_at",
    "ITEM": "item",
    "MODALITY": "modality",
    "WEAPON": "weapon",
    "ADDRESS": "address",
    "LOCATION": "location",
    "DESCRIPTION": "description",
    "CONFIRM": "confirm",
}
