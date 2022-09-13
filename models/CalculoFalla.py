import time
from CalculoTotal import CalculoTotal
import logging as log
from logs.logger import logger


class CalculoFalla:
    """
    Esta clase tiene el objetivo de ejecutar el CalculoTotal iterando la potencia firme hasta alcanzar una falla deseada.

    Ejecutará el CalculoTotal con ciertos valores de entrada y obtendrá la falla. Si esta no es la deseada, cambiará la potencia (aumentándola o disminuyéndola) y volverá a ejecutar el CalculoTotal con esta nueva potencia.
    """

    def __init__(self,input_data,falla_buscada, nivel_min,nivel_max, rendimiento,potencia_instalada, potencia_firme=50) -> None:
        

        # ----------------- INITIAL VARS -----------------------

        if falla_buscada == 0:
            self.falla_buscada = 0.1
        else:
            self.falla_buscada = falla_buscada
        
        self.input_data = input_data
        self.nivel_min = nivel_min
        self.nivel_max = nivel_max
        self.rendimiento = rendimiento
        self.potencia_instalada = potencia_instalada

        # ----------------- ITERATION VARS --------------------

        self.iteraciones = 0
        self.tiempo_inicial_corrida = time.time()
        self.tiempo_corrida_segundos = 0
        self.potencia_firme = potencia_firme
        self.falla_obtenida = 0
        self.falla_paso_previo = 0
        self.diferencia_porcentual_paso_previo = 1.1
        self.error = False
        self.multiplicador = 1.1
        
        # --------------- CALC ---------------------

        self.convergencia_cercana = False
        if self.potencia_firme == 50:
            self.magnitud_alcanzada = False
        else:
            self.magnitud_alcanzada = True

        self.potencia_superior = {"Potencia":0,"Falla":0}
        self.potencia_inferior = {"Potencia":0,"Falla":0}
        try:
            self._calcular_falla()
        except Exception as e:
            raise Exception(f" {e}\nDb: {self.falla_buscada}")

    def _ajuste_falla(self):

        """
        Realiza los ajustes de la Potencia Firme para converger al déficit buscado.
        
        - Se parte de una Potencia Firme que es igual a 50MW por defecto para la cual corresponderá un déficit.
        - Mientras el déficit sea igual a cero, se aumentará la Potencia en 50MW y se recalculará el déficit.
        - Cuando el déficit sea mayor a cero se considera que se alcanzó la magnitud de la Potencia y se la comienza a aumentar con un multiplicador igual a la suma de 1.1 y la diferencia porcentual (diferencia entre déficit obtenido y el buscado).
        - Cuando se encuentre un déficit mayor al buscado, se considera que la convergencia es cercana, ya que hay una Potencia entre dos de las ya evaluadas para la cual se corresponde el déficit buscado. A partir de este punto se converge realizando un promedio ponderado.
        """

        diferencia_porcentual = abs(self.falla_obtenida_exacta - self.falla_buscada)/100

        logger.info(f'Iteración: {self.iteraciones} || Potencia Firme: {round(self.potencia_firme,2)} || Déficit Obtenido: {self.falla_obtenida_exacta} / {self.falla_buscada}')
        logger.handlers[0].close()


        if self.falla_obtenida_exacta > 0 and self.magnitud_alcanzada == False:
            self.magnitud_alcanzada = True
            logger.warning("Magnitud Alcanzada: Falla mayor a cero")

        if self.falla_obtenida_exacta > self.falla_buscada:
            self.potencia_superior["Potencia"] = self.potencia_firme
            self.potencia_superior["Falla"] = self.falla_obtenida_exacta
        else:
            self.potencia_inferior["Potencia"] = self.potencia_firme
            self.potencia_inferior["Falla"] = self.falla_obtenida_exacta

        
        if self.magnitud_alcanzada:
            if (self.falla_obtenida_exacta - self.falla_buscada) * (self.falla_paso_previo - self.falla_buscada) < 0 and self.convergencia_cercana == False:
                self.convergencia_cercana = True
                logger.warning("Convergencia cercana")
            if self.convergencia_cercana:
                if self.falla_buscada == 0.1:
                    self.potencia_firme=(self.potencia_superior["Potencia"]+self.potencia_inferior["Potencia"])/2
                else:
                    dif_falla_sup = abs(self.potencia_superior["Falla"] - self.falla_buscada)
                    dif_falla_inf = abs(self.potencia_inferior["Falla"] - self.falla_buscada)
                    self.potencia_firme = (self.potencia_superior["Potencia"]*1/dif_falla_sup+self.potencia_inferior["Potencia"]*1/dif_falla_inf)/(1/dif_falla_sup+1/dif_falla_inf)

            else:
                cambio = self.multiplicador + diferencia_porcentual
                if self.falla_obtenida_exacta > self.falla_buscada:
                    self.potencia_firme /= cambio
                else:
                    self.potencia_firme *= cambio
            self.diferencia_porcentual_paso_previo = diferencia_porcentual
        else:
            self.potencia_firme +=50

        

    def _calcular_falla(self):

        """
        Realiza el CalculoTotal hasta que el déficit obtenido sea igual al déficit buscado
        """

        no_falla = True
        while True:
            if self.iteraciones > 20:
                logger.critical('Demasiadas iteraciones, puede existir problemas de convergencia para las condiciones ingresadas')
            self.iteraciones +=1
            try:
                
                self.calculo_total = CalculoTotal(
                    input_data=self.input_data,
                    nivel_min=self.nivel_min,
                    nivel_max=self.nivel_max,
                    potencia_firme=self.potencia_firme,
                    rendimiento=self.rendimiento,
                    potencia_instalada=self.potencia_instalada
                    )

                self.falla_obtenida = round(self.calculo_total.falla,2)
                self.falla_obtenida_exacta = self.calculo_total.falla

            
                if self.falla_obtenida != round(self.falla_buscada,1):
                    # Si la falla obtenida es distinta a la buscada realizo un ajuste y luego el while vuelve a ejecutarse
                    self._ajuste_falla()
                    self.falla_paso_previo = self.falla_obtenida_exacta

                else:
                    # Si nada de lo anterior pasó, significa que llegamos a la falla buscada.
                    self.potencia_firme = round(self.potencia_firme,2)
                    self.energia_firme = self.calculo_total.energia_firme
                    self.energia_secundaria = self.calculo_total.energia_secundaria
                    self.energia_falla = self.calculo_total.energia_falla
                    logger.warning("Déficit Encontrado")
                    logger.info(f'Potencia Firme: {self.potencia_firme}')
                    logger.info(f'Déficit Obtenido: {self.falla_obtenida_exacta}')
                    logger.info(f'Rendimiento: {self.rendimiento}')
                    logger.info(f'Nivel Mínimo: {self.nivel_min}')
                    logger.info(f'Nivel Máximo: {self.nivel_max}')
                    logger.info(f"Iteraciones: {self.iteraciones}")
                    logger.handlers[0].close()
                    
                    #calculo_total.duracion()
                    break

            except Exception as e:
                error = str(e)
                if error.find("Final") and no_falla:
                    logger.error("Error")
                    self.potencia_firme = max(self.potencia_superior["Potencia"],self.potencia_superior["Potencia"]) *1.01
                    self.multiplicador = 1.01
                    no_falla = False
                else:
                    raise Exception(e)

        self.tiempo_corrida_segundos = round((time.time() - self.tiempo_inicial_corrida),4)
        logger.info(f"Tiempo: {self.tiempo_corrida_segundos}")
        logger.warning("Fin de la iteración")
        logger.handlers[0].close()

if __name__ == '__main__':

    falla_buscada = 5
    nivel_min = 142
    nivel_max = 160
    rendimiento = 0.9

    calculo_falla = CalculoFalla(
            falla_buscada = falla_buscada,
            nivel_min = nivel_min,
            nivel_max=nivel_max,
            rendimiento=rendimiento
    )