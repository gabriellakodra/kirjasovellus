# Kirjasovellus

Kirjojen arvostelu sovellus, jonne voi julkaista lukemiaan kirjoja nimellä ja antaa oma arvio sekä kommentoida muiden arvioita.

## Sovelluksen ominaisuuksia: 
- sovellukseen luodaan käyttäjä ja kirjaudutaan sisään, jos haluaa tehdä julkaisun tai kommentin.
- käyttäjä voi lisätä, poistaa ja muokata omia arvosteluja ja kommentteja.
- käyttäjä voi tutkia omia ja muiden ihmisten lisäämiä arvosteluja ja kommentteja.
- sovelluksessa voi hakusanalla hakea julkaisuja ostikon, sisällön ja komenttien perusteella sekä etsiä käyttäjänimiä.
- sovelluksessa voi tutkia omaa ja muiden ihmisten profiileja sekä heidän julkaisemia arvosteluja, jotka näkyvät siellä.
- käyttäjä voi halutessaan valita kirjalle luokaksi arvosanan 1-5 sekä ilmoittaa genren.
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
