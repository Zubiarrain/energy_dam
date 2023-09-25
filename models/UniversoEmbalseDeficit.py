# Modules imports
from UniversoEmbalse import UniversoEmbalse

class UniversoEmbalseDeficit(UniversoEmbalse):
    """
    Esta clase analiza el universo de funcionamiento de un embalse a partir de ciertas condiciones de borde como un rango de niveles, de déficits y de rendimientos. 
    """
    def __init__(self, consigna_range, n_range, rendimiento_range,potencia_instalada, max_ndif = None):
        
        super().__init__(consigna_range, n_range, rendimiento_range,potencia_instalada, max_ndif)

        self._calculate()
        self._export_excel()
        #self.duracion()


if __name__ == "__main__":

    u = UniversoEmbalseDeficit(
        consigna_range=[5,20,5],
        n_range=[170,180,0.5],
        rendimiento_range=[0.89,0.92,0.01],
        potencia_instalada=950
    )

