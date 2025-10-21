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