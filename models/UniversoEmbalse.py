# Python imports
import pandas as pd
from pandas import ExcelWriter

# Modules imports
from helpers.help import create_plot
from helpers.help import extract_excel_data
from CalculoFalla import CalculoFalla

class UniversoEmbalse:
    """
    Esta clase analiza el universo de funcionamiento de un embalse a partir de ciertas condiciones de borde como un rango de niveles, de déficits y de rendimientos. 
    """
    def __init__(self, consigna_range, n_range, rendimiento_range,potencia_instalada, max_ndif = None):

        # ------------- INIT self.vars -------------------
        
        self.consigna_range = consigna_range
        self.n_range = n_range
        self.rendimiento_range = rendimiento_range
        self.potencia_instalada = potencia_instalada
        self.max_ndif = max_ndif

        self.duracion_data = False
        self.vars =[self.n_range, self.n_range, self.consigna_range, self.rendimiento_range]
        self.iteration_vars = [None]*len(self.vars)

        # -------------------------------------------

        # ------------- SAVE VALUES -------------------

        self.data_n_min = []
        self.data_n_max = []
        self.data_deficit = []
        self.data_rendimiento = []
        self.data_potencia = []
        self.data_energia_firme = []
        self.data_energia_secundaria = []
        self.data_energia_falla = []
        self.data_energia_total = []
        self.data_tiempo_corrida = []

        self.dicts = []
        self.info = []
        self.duracion_acumulada = []
        self.potencias = []

        # ---------------------------------------------

    def _save_info(self,calculo_falla):

        if self.duracion_data:
            duracion_info = calculo_falla.calculo_total.duracion()

            self.dicts.append(duracion_info)
            info = f"Nm= {self.iteration_vars[0]} - NM= {self.iteration_vars[1]} - P= {self.iteration_vars[2]} - D= {round(calculo_falla.calculo_total.falla,2)} "
            self.info.append(info)
            self.duracion_acumulada.append(duracion_info['Duracion Acumulada'])
            self.potencias.append(duracion_info['Potencia'])

        self.data_n_min.append(self.iteration_vars[0])
        self.data_n_max.append(self.iteration_vars[1])
        self.data_deficit.append(self.iteration_vars[2])
        self.data_rendimiento.append(self.iteration_vars[3])
        self.data_potencia.append(calculo_falla.potencia_firme)
        self.data_energia_firme.append(calculo_falla.energia_firme)
        self.data_energia_secundaria.append(calculo_falla.energia_secundaria)
        self.data_energia_falla.append(calculo_falla.energia_falla)
        self.data_energia_total.append(calculo_falla.energia_firme+calculo_falla.energia_secundaria+calculo_falla.energia_falla)
        self.data_tiempo_corrida.append(calculo_falla.tiempo_corrida_segundos)

    def _consigna(self):
        calculo_falla = CalculoFalla(
            input_data=extract_excel_data("input_energia.xlsx"),
            falla_buscada = self.iteration_vars[2],
            nivel_min = self.iteration_vars[0],
            nivel_max= self.iteration_vars[1],
            potencia_instalada=self.potencia_instalada,
            rendimiento = self.iteration_vars[3],
            potencia_firme=150
        )

        self._save_info(calculo_falla)

    
    def _calculate(self):
        
        """Realiza modelos de embalse con consigna Caudal para todo el rango de variables que se ingresaron en la instancia"""

        def iteration(i,previous_i=None):
            i_num = 0
            min_var = self.vars[i][0]
            max_var = self.vars[i][1]
            step_var = self.vars[i][2]
            if i == 1:
                # Evitar que el Nmax sea menor al Nmin
                min_var += step_var * previous_i
            while min_var <= max_var:
                self.iteration_vars[i] = min_var
                if i == len(self.vars)-1:
                    self._consigna()
                else:
                    iteration(i+1,i_num)

                min_var += step_var
                i_num += 1

        iteration(0)


    def _export_excel(self):

        """Exporta a Excel los principales datos de todos los modelos analizados. También se exportan los datos de la duración de cada modelo si es que esta variable se coloca como True"""

        dict = {
            "N_min": self.data_n_min,
            "N_max": self.data_n_max,
            "Déficit": self.data_deficit,
            "Rendimiento": self.data_rendimiento,
            "Potencia": self.data_potencia,
            "Energia_firme": self.data_energia_firme,
            "Energia_secundaria": self.data_energia_secundaria,
            "Energia_falla": self.data_energia_falla,
            "Energia_total":self.data_energia_total,
            "Tiempo_corrida": self.data_tiempo_corrida
        }

        df = pd.DataFrame(dict)
        writer = ExcelWriter("outputs/results.xlsx")
        df.to_excel(writer, "results")
        writer.save()

        if self.duracion_data:
            for dict in self.dicts:
                index = self.dicts.index(dict)
                df = pd.DataFrame(dict)
                df.to_excel(writer, f"duracion{index} ", index=False)
                writer.save()

    
    def duracion(self):

        """Genera un gráfico con todas las curvas duración de los modelos analizados"""

        create_plot(self.duracion_acumulada,self.potencias,self.info, f'Curva Duración','Duración[%]','Pot [MW]','')




if __name__ == "__main__":

    u = UniversoEmbalse(
        consigna_range=[5,5,5],
        n_range=[176,176,0.5],
        rendimiento_range=[0.9,0.9,0.01],
        potencia_instalada=950
    )

