# Technische Einschränkungen des Regex-Generators

Diese Dokumentation beschreibt die bewussten Designentscheidungen und Limitierungen, die bei der Implementierung des regulären Ausdrucksgenerators gelten.  
Der Fokus liegt auf **technischer Stabilität**, **Vorhersagbarkeit** und **Effizienz**.

---

## 1. Unterstützte Dateiformate

Aus Gründen der Komplexität und Verarbeitbarkeit wird die Eingabe auf eine begrenzte Auswahl allgemeiner Formate reduziert:

- **CSV (Comma-Separated Values)**  
  – Zeilenbasierte Datenstruktur mit Spaltenbezug  
  – Ideal für tabellarische Mustererkennung

- **JSON (JavaScript Object Notation)**  
  – Schlüssel-Wert-Struktur mit klar definierten Token  
  – Unterstützt einfache hierarchische Datenfelder

- **XML (Extensible Markup Language)**  
  – Markup-Struktur mit geöffneten und geschlossenen Tags  
  – Unterstützt Attribut- und Textinhalte

- **HTML (Hypertext Markup Language)**  
  – Teilbaumstruktur vergleichbar mit XML  
  – Unterstützt oberflächliche semantische Erkennung (z. B. `<div>`, `<p>`)

> Andere komplexe Formate (z. B. YAML, INI, Protobuf, Binärdatenformate) sind **nicht zugelassen**.  
> Dies erfolgt zugunsten einer klaren formalen Modellierung im Rahmen regulärer Sprachen.

---

## 2. Beschränkung der Verschachtelungstiefe

Zur Wahrung der Effizienz und zur Einhaltung der theoretischen Grenzen regulärer Sprachen gilt:

- Jedes zugelassene Dateiformat darf **maximal drei Ebenen tief** verschachtelt sein.  
- Beispielhafte gültige Strukturen:

```
{
    "player": {
        "name": "Max",
        "age": 20,
        "games": [
            "Minecraft",
            "Valorant",
            "Battlefield 6" 
        ] 
    }
}
```

```
<root>
    <entry>
        <value>42</value>
    </entry>
</root>
```

> Strukturen mit mehr als zwei hierarchischen Ebenen (z.B. verschachtelte Arrays, rekursive Objekte oder mehrfache Tag‑Verschachtelung) **überschreiten den definierten Formalismus** und werden daher vom Generator **nicht unterstützt**.

---

## 3. Ziel und Begründung

Diese Einschränkungen stellen sicher, dass:

1. **Reguläre Ausdrücke deterministisch** generiert werden können.  
2. **Formalsprachlich korrekte Modelle** (endliche Automaten) erhalten bleiben.  
3. Die **Berechnungskomplexität konstant** in Bezug auf Eingabelänge und Ebenentiefe bleibt.  
4. Der **praktische Nutzen** für weit verbreitete Formate wie CSV, JSON, XML und HTML gewährleistet ist.

---


## 4. API Dokumentation
### Endpunkte

Die Base URL lautet: `/v1/api/endpoint/` bzw. https://regex-generator-backend.onrender.com/v1/api/endpoint.  
Bei standalone ausführung des Python-Projekts ist die API über den Port `50123` aufzurufen.  


1. /match
2. /generate
3. /detecttype
  
### 1. Match-Endpunkt
Überprüft ob der übergebene text dem regex pattern entspricht.

- **Resource**: `/match`
- **Methode:** POST
- **Request Body:** JSON
- **Request Schema:** 
```
{
    "regex": "string",
    "text": string""
}
```
- **Response Body:** JSON
- **Response Schema:** 
```
{
    "value": true|false,
    "message": "string"
}
```
- **Response Codes:** 200, 400

  
### 2. Generate-Endpunkt
Generiert einen Regex basierend auf dem übergebenen text.

- **Resource**: `/generate`
- **Methode:** POST
- **Request Body:** JSON
- **Request Schema:** 
```
{
    "filetype": "JSON|XML|HTML|CSV",
    "text": "string"
}
```
- **Response Body:** JSON
- **Response Schema:** 
```
{
    "value": "string",
    "message": "string"
}
```
- **Response Codes:** 200, 400
  
  
### 3. DetectFileType-Endpunkt
Generiert einen Regex basierend auf dem übergebenen text.

- **Resource**: `/detectfiletype`
- **Methode:** POST
- **Request Body:** JSON
- **Request Schema:** 
```
{
    "text": "string",
    "ml": true|false
}
```
- **Response Body:** JSON
- **Response Schema:** 
```
{
    "value": "JSON|XML|HTML|CSV",
    "message": "string"
}
```
- **Response Codes:** 200, 400