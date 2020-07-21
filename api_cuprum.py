import json
import os

import requests
from flask import Flask, make_response
from flask_restful import Resource, Api
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from AFP import AFP
from Account import Account
from Kind import Kind
app = Flask(__name__)
api = Api(app)


class Cuprum(Resource):
    def get(self, rut, password):

        timeout = float(os.environ["TIMEOUT"])

        pathDriver = os.environ["PATH_DRIVER"]

        driver = webdriver.Chrome(pathDriver)
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

        account = self.getInfoAccount(rut, jwt)

        kindsTmp = self.getSaldoTotalPorCuentaBff(rut, jwt)

        cuentas = account['Cuentas']
        total = account['SaldoTotal']

        accounts = []

        for cuenta in cuentas:
            kinds = []

            output_dict = [x for x in kindsTmp if x['nombre'] == cuenta['Cuentas']]

            if len(output_dict) > 0:
                kinds = self.getKinds(output_dict[0]['fondos'])
            account = Account(cuenta['Cuentas'],
                              cuenta['Price'],
                              kinds)
            accounts.append(account.__dict__)

        afp = AFP(accounts, total)

        self.closeDriver(driver)

        return afp.__dict__

    def getKinds(self, output_dict, ):
        kinds = []

        for kind in output_dict:
            name = kind['nombre']
            price = kind['saldo']

            kinds.append(Kind(name, price).__dict__)
        return kinds

    def closeDriver(self, driver):

        cookies_list = driver.get_cookies()
        cookies_dict = {}
        for cookie in cookies_list:
            cookies_dict[cookie['name']] = cookie['value']

        driver.stop_client()
        driver.close()

    def getInfoAccount(self, rut, jwt):

        url = "https://www.cuprum.cl/SaldoTotalPorCuentaBFF/bff/SaldoTotalPorCuenta"
        querystring = {"rut": rut}
        headers = {
            'Authorization': jwt,
            'cache-control': "no-cache",
        }
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=200)

        return json.loads(response.text)

    def getSaldoTotalPorCuentaBff(self, rut, jwt):

        url = "https://www.cuprum.cl/SaldoTotalPorCuentaBFF/bff/DetalleDeCuenta/ObtenerDatosCuenta"
        querystring = {"rut": rut, "cuenta": "CCO"}
        headers = {
            'Authorization': jwt,
            'cache-control': "no-cache",
        }
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=200)

        return json.loads(response.text)


api.add_resource(Cuprum, '/cuprum/<rut>/<password>')  # Route_1

if __name__ == '__main__':
    app.run(port=os.environ["PORT"])
