// noinspection JSAnnotator,JSUnresolvedReference

// Initialisiere die Speichervariablen, falls sie noch nicht existieren
let stats = context.get('humid-stats') || {sum: 0, count: 0, lastHour: new Date().getHours()};
let history = context.get('humid-history') || [];

// Aktuellen Wert zur Summe addieren
stats.sum += msg.payload;
stats.count++;

let currentHour = new Date().getHours();

// Prüfen, ob eine neue Stunde angebrochen ist
if (currentHour !== stats.lastHour) {
    // Mittelwert berechnen
    let average = stats.sum / stats.count;

    // Zeitstempel für die X-Achse (z.B. "14:00")
    let timeLabel = stats.lastHour.toString().padStart(2, '0') + ":00";

    // Neuen Datenpunkt in die Historie pushen
    history.push({time: timeLabel, value: parseFloat(average.toFixed(1))});

    // Begrenzung auf die letzten 24 Stunden
    if (history.length > 24) {
        history.shift();
    }

    // Reset für die neue Stunde
    stats.sum = 0;
    stats.count = 0;
    stats.lastHour = currentHour;

    // Daten speichern
    context.set('humid-stats', stats);
    context.set('humid-history', history);

    // Nachricht mit dem kompletten Array an das Chart-Template senden
    msg.payload = history;
    return msg;
} else {
    // Innerhalb der Stunde: Nur speichern, nichts senden (oder optional "null" zurückgeben)
    context.set('humid-stats', stats);
    return null;
}