"""webif Object.

A webif object that contains a webif item and communicates with the webif.
It contains a webif client for setting and getting webif values
"""

# import warnings
import asyncio
import logging
import time
import warnings
import aiohttp

from bs4 import BeautifulSoup
from pymodbus import ExceptionResponse, ModbusException
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import FORMATS, TYPES


class WebifConnection:
    _ip = ""
    _username = ""
    _password = ""
    _session = None
    _payload = {"user": _username, "pass": _password}
    _base_url = "http://" + _ip
    _login_url = "/login.html"

    _values = {}

    def __init__(self) -> None:
        self._ip = "10.10.1.225"
        self._username = "Mad_One"
        self._password = "5315herb"
        self._base_url = "http://" + self._ip
        # jar = aiohttp.CookieJar(unsafe=True)
        # self._session = aiohttp.ClientSession(cookie_jar=jar)

    def __del__(self) -> None:
        ...
        # await self._session.close()

    async def login(self) -> None:
        async with self._session.post(
            "http://10.10.1.225/login.html",
            data={"user": "Mad_One", "pass": "5315herb"},
        ) as response:
            if response.status == 200:
                self._connected = True
            else:
                self._connected = False
            print(response.url)
            print(await response.text())

    async def return_test_data(self) -> dict[str, str]:
        return {"Webifsensor": "TESTWERT"}

    async def close(self) -> None:
        await self._session.close()

    async def get_info(self) -> None:
        """Return Info -> Heizkreis1."""

        async with self._session.get(
            "/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401"
        ) as response:
            if response.status != 200:
                warnings.warn("Error: " & str(response.status))
                return
            else:
                print(await response.text())
            main_page = BeautifulSoup(
                markup=await response.text(), features="html.parser"
            )
            navs = main_page.find("div", class_="col-3")
            values_nav = navs[2]
            self._values["Info"] = {"Heizkreis": self.get_values(soup=values_nav)}
            print(self._values)

    def get_links(self, soup: BeautifulSoup) -> dict:
        """Return links from given nav container."""
        soup_links = soup.find_all("a")
        links = {}
        for link in soup_links:
            # print(link)
            # print(link.name)
            name = link.find("h5").text.strip()
            url = link["href"]
            links[name] = url
            # print(name + ": " + url)
            # link = link.find("a")
            # print(name + ":" + link)
        return links

    def get_values(soup: BeautifulSoup) -> dict:
        """Return values from given nav container."""
        soup_links = soup.find_all("div", class_="nav-link browseobj")
        # print(soup_links)
        values = {}
        for item in soup_links:
            # print(link)
            # print(item.name)
            name = item.find("h5").text.strip()
            value = item.findAll(string=True, recursive=False)
            values[name] = value[1].strip()
            # print(name + ": " + url)
            # link = link.find("a")
            # print(name + ":" + link)
        return values

    def get_link_values(soup: BeautifulSoup) -> dict:
        """Return values from given nav container witch are inside a link."""
        soup_links = soup.find_all("a", class_="nav-link browseobj")
        # print(soup_links)
        values = {}
        for item in soup_links:
            # print(link)
            # print(item.name)
            name = item.find("h5").text.strip()
            value = item.findAll(string=True, recursive=False)
            values[name] = value[1].strip()
            # print(name + ": " + url)
            # link = link.find("a")
            # print(name + ":" + link)
        return values
