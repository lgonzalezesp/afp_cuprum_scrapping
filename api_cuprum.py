from flask import Flask, make_response
from flask_restful import Resource, Api
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import requests
import json
import os

from AFP import AFP
from Account import Account

app = Flask(__name__)
api = Api(app)


class Cuprum(Resource):
    def get(self, rut, password):

        timeout = float(os.environ["TIMEOUT"])

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get('https://www.cuprum.cl/wwwCuprum/Login.aspx')
        driver.find_element_by_id('_ctl0_MainContent_rut').send_keys(rut)
        driver.find_element_by_id('_ctl0_MainContent_password').send_keys(password)
        driver.find_element_by_id('login').click()

        try:
            element_present = EC.presence_of_element_located((By.ID, 'loader'))
            WebDriverWait(driver, timeout).until(element_present)
            jwt = driver.execute_script("return localStorage.getItem('jwtSTPC')");

        except TimeoutException:
            return make_response("Timed out waiting for page to load", 404)

        json_data = self.getInfoAccount(rut, jwt)

        cuentas = json_data['Cuentas']
        total = json_data['SaldoTotal']

        accounts = []

        for cuenta in cuentas:
            account = Account(cuenta['Cuentas'],
                              cuenta['Price'],
                              cuenta['Fondos'][0]['Nombre'])
            accounts.append(account.__dict__)

        afp = AFP(accounts, total)

        self.closeDriver(driver)

        return afp.__dict__

    def closeDriver(self, driver):
        driver.stop_client()
        driver.close()

    def getInfoAccount(self, rut, jwt):

        url = "https://www.cuprum.cl/SaldoTotalPorCuentaBFF/bff/SaldoTotalPorCuenta"
        querystring = {"rut": rut}
        headers = {
            'Authorization': jwt,
            'cache-control': "no-cache",
            'Postman-Token': "2485594c-8f02-41c5-8ef9-2c80f5f87f09"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        return json.loads(response.text)


api.add_resource(Cuprum, '/cuprum/<rut>/<password>')  # Route_1

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
