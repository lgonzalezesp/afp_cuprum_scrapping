# API AFP Cuprum
API que obtiene el saldo total de la cuenta AFP Cuprum, realizada con Python Web Scrapping.

## Stack

 - Python 3.6
 
## Variables de entorno

| Variable      | Description | Ejemplo|
| ----------- | ----------- |----------|
| TIMEOUT      | Tiempo de espera en ejecutar la API interna de AFP Cuprum| 30 |

## Ejecutar de forma local

    python3 api_cuprum.py

## API Request

    /cuprum/{RUT}/{PASSWORD}

| Variable      | Description | Ejemplo|
| ----------- | ----------- |----------|
| RUT      | Rut del usuario, sin puntos, con guión y digito verificador| 17123123-2 |
| PASSWORD   | Contraseña del usuario | 123123123|

## API Response
    {
        "accounts": [
            {
                "kind": "E",
                "name": "Ahorro Obligatorio",
                "price": 123123.0
            },
            {
                "kind": "E",
                "name": "Cotizaciones Voluntarias",
                "price": 123123.0
            }
        ],
        "total": 123123.0
    }

| Variable      | Description | Ejemplo|
| ----------- | ----------- |----------|
| kind      | Fondo | A,B,C,D |
| name   | Nombre o descripción | Ahorro Obligatorio|
| price   | Monto de la cuenta | 123123.0|
| total   | Monto total de las cuentas | 123123.0|



## Pruebas locales

Ejecutar la API en python

    python3 api_cuprum.py
    
Ejecutar la API

    http localhost:5009/cuprum/123123123-2/123123123