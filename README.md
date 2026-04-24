# Kirjasovellus

Kirjojen arvostelu sovellus, jonne voi julkaista lukemiaan kirjoja nimellä ja antaa oma arvio / kommentoida muiden arvioita.

## Sovelluksen ominaisuuksia: 
- sovellukseen luodaan käyttäjä ja kirjaudutaan sisään, jos haluaa tehdä julkaisun tai kommentin.
- käyttäjä voi lisätä, poistaa ja muokata omia arvosteluja / kommentteja.
- käyttäjä voi tutkia omia ja muiden ihmisten lisäämiä arvosteluja ja kommentteja.
- sovelluksessa voi hakusanalla hakea kirjoja, joita on arvosteltu.
- sovelluksessa voi tutkia omaa ja muiden ihmisten profiileja sekä heidän julkaisemia arvosteluja, jotka näkyvät siellä.
- käyttäjä voi valita arvostelun kirjalle luokittelun esim. tietokirjallisuus vai kaunikirjallisuus.
- toissijaisena tietokohteena toimii muiden julkaisujen kommentointi.
  
## Sovelluksen asennus:
Asenna `flask`-kirjasto:

```
$ pip install flask
```

Alusta tietokanta:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Käynnistä sovellus:

```
$ flask run
```
