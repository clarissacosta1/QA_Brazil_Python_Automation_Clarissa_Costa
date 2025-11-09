import data
from helpers import is_url_reachable

import data
from helpers import is_url_reachable

class TestUrbanRoutes:

    @classmethod
    def setup_class(cls):
        if is_url_reachable(data.URBAN_ROUTES_URL):
            print("Conectado ao servidor Urban Routes")
        else:
            print("Não foi possível conectar ao Urban Routes. Verifique se o servidor ainda está ligado e ainda em execução")

    def test_set_route(self):
        #adicionar em S8
        pass
    def test_select_plan(self):
        # adicionar em S8
        pass
    def test_fill_phone_number(self):
        # adicionar em S8
        pass
    def test_fill_card(self):
        # adicionar em S8
        pass
    def test_fill_card_with_number(self):
        # adicionar em S8
        pass
    def test_comment_for_driver(self):
        # adicionar em S8
        pass
    def test_order_blanket_and_handkerchiefs(self):
        # adicionar em S8
        pass

    def test_order_2_ice_creams(self):
        #adicionar em S8
        for i in range(2):
            # Código que será executado a cada iteração
            print(f"Adicionar sorvete {i + 1}")
            #Adicionar em s8
    pass

    def test_car_search_model_appears(self):
        # adicionar em S8
        pass

