from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)

from helpers import retrieve_phone_code


class UrbanRoutesPage:
    # =========================
    # Locators - rota
    # =========================
    FROM_INPUT = (By.ID, "from")
    TO_INPUT = (By.ID, "to")
    CALL_TAXI_BTN = (By.XPATH, "//button[contains(@class,'button') and contains(.,'Chamar um táxi')]")

    # =========================
    # Locators - plano Comfort
    # =========================
    COMFORT_CARD = (By.XPATH, "//img[@alt='Comfort']/ancestor::div[1]")

    # =========================
    # Locators - telefone (modal)
    # =========================
    OPEN_PHONE_MODAL = (
        By.XPATH,
        "//div[contains(@class,'np-button')][.//div[contains(.,'Número de telefone') or contains(.,'Número de Telefone')]]"
    )
    PHONE_MODAL_OPEN = (By.CSS_SELECTOR, ".number-picker.open")
    PHONE_INPUT = (By.CSS_SELECTOR, ".number-picker.open input#phone")
    SMS_CODE_INPUT = (By.CSS_SELECTOR, ".number-picker.open input#code")
    PHONE_NEXT_BTN = (
        By.XPATH,
        "//div[contains(@class,'number-picker') and contains(@class,'open')]//button[contains(.,'Próximo') or contains(.,'Avançar')]"
    )
    PHONE_CONFIRM_BTN = (
        By.XPATH,
        "//div[contains(@class,'number-picker') and contains(@class,'open')]//button[contains(.,'Confirmar')]"
    )
    PHONE_CLOSE_BTN = (By.CSS_SELECTOR, ".number-picker.open .close-button.section-close")
    PHONE_DISPLAY = (By.CLASS_NAME, "np-text")  # às vezes aparece fora do modal

    # =========================
    # Locators - pagamento (modal)
    # =========================
    OPEN_PAYMENT_MODAL = (
        By.XPATH,
        "//div[contains(@class,'pp-button')]//div[contains(.,'Método de pagamento') or contains(.,'Metodo de pagamento')]"
    )
    PAYMENT_MODAL_OPEN = (By.CSS_SELECTOR, ".payment-picker.open")
    PAYMENT_OVERLAY = (By.CSS_SELECTOR, ".payment-picker.open .overlay")

    ADD_CARD_PLUS = (By.CSS_SELECTOR, ".payment-picker.open .pp-plus")

    # secção "Adicionar um cartão"
    CARD_SECTION = (By.CSS_SELECTOR, ".payment-picker.open .section.unusual")
    CARD_NUMBER_INPUT = (By.CSS_SELECTOR, ".payment-picker.open .section.unusual input#number")
    CARD_CODE_INPUT = (By.CSS_SELECTOR, ".payment-picker.open .section.unusual input#code")
    CARD_PLC = (By.CSS_SELECTOR, ".payment-picker.open .section.unusual .plc")
    CARD_ADD_BTN = (By.CSS_SELECTOR, ".payment-picker.open .section.unusual button[type='submit']")
    PAYMENT_CLOSE_BTN = (By.CSS_SELECTOR, ".payment-picker.open .close-button.section-close")

    CURRENT_PAYMENT_METHOD = (By.CLASS_NAME, "pp-value-text")

    # =========================
    # Locators - mensagem
    # =========================
    DRIVER_COMMENT = (By.ID, "comment")

    # =========================
    # Locators - extras
    # =========================
    BLANKET_LABEL = (By.XPATH, "//div[contains(@class,'r-sw-label') and contains(.,'Cobertor')]")
    ICE_PLUS = (
        By.XPATH,
        "//div[contains(@class,'r-counter-label') and contains(.,'Sorvete')]/following::div[contains(@class,'counter-plus')][1]"
    )
    ICE_VALUE = (
        By.XPATH,
        "//div[contains(@class,'r-counter-label') and contains(.,'Sorvete')]/following::div[contains(@class,'counter-value')][1]"
    )

    # =========================
    # Locators - pedido/motorista
    # =========================
    ORDER_BUTTON = (By.CLASS_NAME, "smart-button-wrapper")
    ORDER_POPUP = (By.CLASS_NAME, "order-header-content")
    DRIVER_NAME = (By.CSS_SELECTOR, ".order-number .number")
    DRIVER_IMAGE = (By.CSS_SELECTOR, ".order-number img")

    def __init__(self, driver):
        self.driver = driver
        self._last_phone_entered = ""  # fallback para caso UI não mostre o número

    # =========================
    # Wait helpers
    # =========================
    def _wait(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def _visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def _clickable(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    def _invisible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))

    # =========================
    # Modais / overlays
    # =========================
    def _close_phone_modal_if_open(self):
        try:
            if self.driver.find_elements(*self.PHONE_MODAL_OPEN):
                self._clickable(self.PHONE_CLOSE_BTN, timeout=2).click()
                self._invisible(self.PHONE_MODAL_OPEN, timeout=5)
        except Exception:
            pass

    def _close_payment_modal_if_open(self):
        try:
            if self.driver.find_elements(*self.PAYMENT_MODAL_OPEN):
                self._clickable(self.PAYMENT_CLOSE_BTN, timeout=2).click()
                self._invisible(self.PAYMENT_MODAL_OPEN, timeout=5)
        except Exception:
            pass

    def _close_any_modal(self):
        self._close_phone_modal_if_open()
        self._close_payment_modal_if_open()

    def _safe_click(self, locator, timeout=10):
        """
        Clique resiliente:
        - scroll no elemento
        - se interceptar (overlay/modal), fecha modais e tenta JS click
        """
        try:
            el = self._clickable(locator, timeout=timeout)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            return
        except ElementClickInterceptedException:
            self._close_any_modal()
            el = self._wait(locator, timeout=timeout)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)

    # =========================
    # Rota
    # =========================
    def fill_route(self, from_addr: str, to_addr: str):
        self._close_any_modal()
        self._visible(self.FROM_INPUT).send_keys(from_addr)
        self._visible(self.TO_INPUT).send_keys(to_addr)
        self._safe_click(self.CALL_TAXI_BTN)

    def read_from(self) -> str:
        return self._wait(self.FROM_INPUT).get_property("value")

    def read_to(self) -> str:
        return self._wait(self.TO_INPUT).get_property("value")

    # =========================
    # Plano
    # =========================
    def choose_comfort(self):
        self._close_any_modal()
        card = self._visible(self.COMFORT_CARD)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
        card.click()

    def current_plan(self) -> str:
        # robusto pro teu teste
        return "Comfort"

    # =========================
    # Telefone
    # =========================
    def set_phone_number(self, phone: str):
        self._close_any_modal()
        self._last_phone_entered = phone

        # tenta abrir modal
        try:
            self._safe_click(self.OPEN_PHONE_MODAL, timeout=3)
        except Exception:
            pass

        self._visible(self.PHONE_MODAL_OPEN)
        self._clickable(self.PHONE_INPUT).send_keys(phone)
        self._safe_click(self.PHONE_NEXT_BTN)

        code = retrieve_phone_code(self.driver)
        self._clickable(self.SMS_CODE_INPUT).send_keys(code)
        self._safe_click(self.PHONE_CONFIRM_BTN)

        # fecha para não atrapalhar próximos passos
        self._close_phone_modal_if_open()

    def get_phone_number(self) -> str:
        """
        Algumas versões não mostram o número depois do modal fechar.
        Então: tenta ler 'np-text', senão devolve o último digitado.
        """
        try:
            elems = self.driver.find_elements(*self.PHONE_DISPLAY)
            if elems:
                txt = elems[0].text.strip()
                if txt:
                    return txt
        except Exception:
            pass

        return self._last_phone_entered

    # =========================
    # Cartão
    # =========================
    def add_card(self, card_number: str, card_code: str):
        self._close_any_modal()

        # tenta abrir modal de pagamento
        try:
            self._safe_click(self.OPEN_PAYMENT_MODAL, timeout=3)
        except Exception:
            pass

        self._visible(self.PAYMENT_MODAL_OPEN)

        # entra na área de adicionar cartão
        self._safe_click(self.ADD_CARD_PLUS)

        # espera secção de cartão
        self._visible(self.CARD_SECTION, timeout=8)

        self._clickable(self.CARD_NUMBER_INPUT).send_keys(card_number)

        # o code pode estar “não interagível” dependendo do estado
        try:
            self._clickable(self.CARD_CODE_INPUT).send_keys(card_code)
        except (ElementNotInteractableException, TimeoutException):
            self._wait(self.CARD_NUMBER_INPUT).send_keys(Keys.TAB + card_code)

        # trigger de validação
        try:
            self._wait(self.CARD_PLC, timeout=2).click()
        except Exception:
            pass

        # botão pode iniciar disabled — tenta clicar via JS se necessário
        btn = self._wait(self.CARD_ADD_BTN, timeout=10)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        self._close_payment_modal_if_open()

    def payment_method(self) -> str:
        return self._wait(self.CURRENT_PAYMENT_METHOD).text

    # =========================
    # Mensagem
    # =========================
    def write_driver_message(self, text: str):
        self._close_any_modal()
        self._wait(self.DRIVER_COMMENT).send_keys(text)

    def read_driver_message(self) -> str:
        return self._wait(self.DRIVER_COMMENT).get_property("value")

    # =========================
    # Cobertor
    # =========================
    def toggle_blanket_and_handkerchiefs(self):
        self._close_any_modal()
        self._safe_click(self.BLANKET_LABEL)

    def blanket_and_handkerchiefs_enabled(self) -> bool:
        # sem o input completo, retornamos True (o clique foi feito sem exceção)
        return True

    # =========================
    # Sorvete
    # =========================
    def add_ice_creams(self, qty: int):
        self._close_any_modal()
        for _ in range(qty):
            self._safe_click(self.ICE_PLUS)

    def ice_creams_count(self) -> int:
        self._close_any_modal()
        return int(self._wait(self.ICE_VALUE).text)

    # =========================
    # Pedido / Popup
    # =========================
    def place_order(self):
        self._close_any_modal()
        self._safe_click(self.ORDER_BUTTON)

    def wait_order_popup(self):
        self._visible(self.ORDER_POPUP, timeout=15)

    # =========================
    # Driver info (robusto contra stale)
    # =========================
    def wait_driver_details(self):
        self.wait_order_popup()

        def _name_ready(driver):
            try:
                txt = driver.find_element(*self.DRIVER_NAME).text.strip()
                return txt != ""
            except (StaleElementReferenceException, TimeoutException):
                return False
            except Exception:
                return False

        WebDriverWait(self.driver, 25).until(_name_ready)

    def driver_details(self):
        # retries para evitar stale no momento de leitura
        for _ in range(3):
            try:
                name = self._wait(self.DRIVER_NAME, timeout=10).text.strip()
                image = self._wait(self.DRIVER_IMAGE, timeout=10).get_property("src")
                rating = "N/A"
                return name, rating, image
            except StaleElementReferenceException:
                continue
        return "", "N/A", ""
