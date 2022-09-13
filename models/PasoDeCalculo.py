from helpers.help import extract_excel_data,interpolation


class PasoDeCalculo:
    """
    Esta clase recibirá como datos de entrada las condiciones iniciales para un determinado paso de calculo de un modelo de embalse y los procesará y devolverá las condiciones finales de dicho paso de calculo
    """

    def __init__(self,time,nivel_inicial,volumen_inicial,area_inicial,caudal_entrante,evaporacion,precipitacion,nivel_volumen,nivel_min,nivel_max,potencia_firme,nivel_restitucion,caudal_nivelRes, rendimiento, potencia_instalada):

        # ------------ INIT VARS ------------------
        self.time = time
        self.nivel_inicial = nivel_inicial
        self.volumen_inicial = volumen_inicial
        self.area_inicial = area_inicial
        self.caudal_entrante = caudal_entrante
        self.evaporacion = evaporacion
        self.precipitacion = precipitacion
        self.nivel_volumen = nivel_volumen
        self.nivel_min = nivel_min
        self.nivel_max = nivel_max
        self.potencia_firme = potencia_firme
        self.caudal_nivelRes = caudal_nivelRes
        self.rendimiento = rendimiento
        self.nivel_restitucion = round(nivel_restitucion,4)
        self.densidad_agua_kg_m3 = 1000
        self.potencia_instalada = potencia_instalada

        self._caudal_salto_nres_iteracion()
        self._condiciones_finales()
        self._verification()

        # Si no tenemos falla o secundario, el tiempo firme será del 100%, de lo contrario, será menor a este
        self.tiempo_firme = 1 - self.tiempo_falla - self.tiempo_secundario
        self.energia_firme = self.potencia_firme*(self.tiempo_secundario+self.tiempo_firme)*24
        
        if self.tiempo_firme == 0:
            self.potencia_firme = 0
    
    def _caudal_salto_nres_iteracion(self):

        """ Se realiza la iteración Q-Nres-H hasta que el nivel de restitucion calculado al cuarto decimal sea igual al del paso anterior. """
        self.salto = 0

        while True:
            self.salto =  self.nivel_inicial - self.nivel_restitucion
            self.caudal_objetivo = self.potencia_firme/(self.rendimiento*self.densidad_agua_kg_m3*self.salto*9.8)*1000000
            nivel_restitucion_iterado = round(interpolation(self.caudal_nivelRes[0],self.caudal_nivelRes[1],self.caudal_objetivo,'x', "Q. obj"),4)

            if nivel_restitucion_iterado == self.nivel_restitucion:
                break
            else:
                self.nivel_restitucion = nivel_restitucion_iterado
    
    def _condiciones_finales(self):

        """Calculo de las condiciones finales a partir de las condiciones iniciales"""

        self.caudal_balance = (self.precipitacion-self.evaporacion)*self.area_inicial*1000/(24*60*60)
        self.delta_caudal = self.caudal_entrante + self.caudal_balance - self.caudal_objetivo
        self.delta_volumen = self.delta_caudal*24*60*60/1000000
        self.volumen_final = self.volumen_inicial + self.delta_volumen
        # Por defecto, las condiciones de falla y secundarias son cero
        self.tiempo_falla = 0
        self.potencia_falla = 0
        self.energia_falla = 0

        self.tiempo_secundario = 0
        self.potencia_secundaria = 0
        self.energia_secundaria = 0

        if self.volumen_final <= self.nivel_volumen[1][-1]:
            self.nivel_final = interpolation(self.nivel_volumen[0],self.nivel_volumen[1],self.volumen_final,'y',"Vol. Final")
        else:
            pendiente = (self.nivel_volumen[1][-1]-self.nivel_volumen[1][-2])/(self.nivel_volumen[0][-1]-self.nivel_volumen[0][-2])
            self.nivel_final = (self.volumen_final-self.nivel_volumen[1][-2])/pendiente + self.nivel_volumen[0][-2]
            
    def _verification(self):

        """Verifica si el nivel final es mayor al nivel maximo o menor al mínimo."""
        
        if self.nivel_final < self.nivel_min:
            # Si el nivel final es menor al mínimo, tendrémos tiempo de falla, caudal de falla y el nivel se limita al nivel mínimo
            try:
                nivel_restitucion = round(interpolation(self.caudal_nivelRes[0],self.caudal_nivelRes[1],self.caudal_entrante,'x', "Qe"),4)
                
            except:
                # Realiza una extrapolación inferior
                pendiente = (self.caudal_nivelRes[0][-1]-self.caudal_nivelRes[0][-2])/(self.caudal_nivelRes[1][-1]-self.caudal_nivelRes[1][-2])
                nivel_restitucion = (self.caudal_entrante-self.caudal_nivelRes[0][-2])/pendiente + self.caudal_nivelRes[1][-2]
                
            self.salto = self.nivel_inicial - nivel_restitucion
            self.tiempo_falla = (self.nivel_min - self.nivel_final) / (self.nivel_inicial-self.nivel_final)
            self.potencia_falla = (self.caudal_entrante + self.caudal_balance)*9.8*self.salto*self.rendimiento*self.densidad_agua_kg_m3/1000000
            self.energia_falla = self.potencia_falla*self.tiempo_falla*24
            self.nivel_final = self.nivel_min

        elif self.nivel_final > self.nivel_max:
            # Si el nivel final es mayor al máximo, tendrémos tiempo secundario, caudal secundario y el nivel se limita al nivel máximo
            try:
                nivel_restitucion = round(interpolation(self.caudal_nivelRes[0],self.caudal_nivelRes[1],self.caudal_entrante,'x', "Qe"),4)
                
            except:
                # Realiza una extrapolación superior
                pendiente = (self.caudal_nivelRes[0][-1]-self.caudal_nivelRes[0][-2])/(self.caudal_nivelRes[1][-1]-self.caudal_nivelRes[1][-2])
                nivel_restitucion = (self.caudal_entrante-self.caudal_nivelRes[0][-2])/pendiente + self.caudal_nivelRes[1][-2]

            self.salto = self.nivel_inicial - nivel_restitucion

            self.tiempo_secundario = (self.nivel_final-self.nivel_max) / (self.nivel_final-self.nivel_inicial)
            self.potencia_secundaria = (self.caudal_entrante + self.caudal_balance)*9.8*self.salto*self.rendimiento*self.densidad_agua_kg_m3/1000000
            if self.potencia_secundaria > self.potencia_instalada:
                self.potencia_secundaria = self.potencia_instalada
            self.energia_secundaria = (self.potencia_secundaria - self.potencia_firme )*self.tiempo_secundario*24
            self.nivel_final = self.nivel_max

if __name__ == '__main__':
    
    input_data = extract_excel_data()
    nivel_volumen = [input_data["Nivel[m]"],input_data["Volumen[Hm3]"]]
    caudal_nivelRes = [input_data["Caudal[m³/s]"],input_data["Nivel_res[m]"]]
    paso_de_calculo_1 = PasoDeCalculo(
                                0,
                                192,
                                35864.38,
                                337.46,
                                242,
                                8.18,
                                0.0673,
                                nivel_volumen,
                                140,
                                192.5,
                                15.91,
                                113.5,
                                caudal_nivelRes,
                                0.9
                                )
    print(paso_de_calculo_1.energia_firme)