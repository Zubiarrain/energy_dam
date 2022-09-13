# Modules imports
from helpers.help import extract_excel_data
from CalculoTotal import CalculoTotal
from logs.logger import logger
from UniversoEmbalse import UniversoEmbalse

class UniversoEmbalsePotencia(UniversoEmbalse):
    """
    Esta clase analiza el universo de funcionamiento de un embalse a partir de ciertas condiciones de borde como un rango de niveles, de déficits y de rendimientos. 
    """
    def __init__(self, consigna_range, n_range, rendimiento_range,potencia_instalada, max_ndif = None):
        
        super().__init__(consigna_range, n_range, rendimiento_range,potencia_instalada, max_ndif)
        # ------------- INIT VARS -------------------

        self._calculate()
        self._export_excel()
        #self.duracion()
    
    def _consigna(self):
        calculo_total = CalculoTotal(
            input_data=extract_excel_data("input_energia.xlsx"),
            nivel_min = self.iteration_vars[0],
            nivel_max= self.iteration_vars[1],
            potencia_firme=self.iteration_vars[2],
            rendimiento = self.iteration_vars[3],
            potencia_instalada=self.potencia_instalada
        )

        self._save_info(calculo_total)

    def _save_info(self,calculo_total):

        if self.duracion_data:

            duracion_info = calculo_total.duracion()
            self.dicts.append(duracion_info)
            info = f"Nm= {self.iteration_vars[0]} - NM= {self.iteration_vars[1]} - P= {self.iteration_vars[2]} - D= {round(calculo_total.falla,2)} "
            self.info.append(info)
            self.duracion_acumulada.append(duracion_info['Duracion Acumulada'])
            self.potencias.append(duracion_info['Potencia'])

        self.data_n_min.append(self.iteration_vars[0])
        self.data_n_max.append(self.iteration_vars[1])
        self.data_potencia.append(self.iteration_vars[2])
        self.data_rendimiento.append(self.iteration_vars[3])
        self.data_deficit.append(calculo_total.falla)
        self.data_energia_firme.append(calculo_total.energia_firme)
        self.data_energia_secundaria.append(calculo_total.energia_secundaria)
        self.data_energia_falla.append(calculo_total.energia_falla)
        self.data_energia_total.append(calculo_total.energia_firme+calculo_total.energia_secundaria+calculo_total.energia_falla)
        self.data_tiempo_corrida.append(calculo_total.tiempo_corrida_segundos)
        logger.info(f"Nm= {self.iteration_vars[0]} - NM= {self.iteration_vars[1]} - P= {self.iteration_vars[2]} -R= {self.iteration_vars[3]} - D= {round(calculo_total.falla,2)}  - T= {calculo_total.tiempo_corrida_segundos} ")
        logger.handlers[0].close()



if __name__ == "__main__":

    u = UniversoEmbalsePotencia(
        consigna_range=[130,250,40],
        n_range=[174.5,176.5,0.5],
        rendimiento_range=[0.89,0.92,0.01],
        potencia_instalada=950
    )


