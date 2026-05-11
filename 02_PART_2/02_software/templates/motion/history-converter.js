// noinspection JSAnnotator

let stats = context.get('motion-stats') || { count: 0, lastHour: new Date().getHours() };
let history = context.get('motion-history') || [];

// Wenn Bewegung erkannt (msg.payload ist true oder 1)
if (msg.payload === true || msg.payload === 1 || msg.payload === "on") {
    stats.count++;
}

let currentHour = new Date().getHours();

// Stundenwechsel
if (currentHour !== stats.lastHour) {
    let timeLabel = stats.lastHour.toString().padStart(2, '0') + ":00";

    history.push({ time: timeLabel, value: stats.count });

    if (history.length > 24) history.shift();

    // Reset für neue Stunde
    stats.count = 0;
    stats.lastHour = currentHour;

    context.set('motion-stats', stats);
    context.set('motion-history', history);

    msg.payload = history;
    return msg;
}

context.set('motion-stats', stats);
// Wir senden das aktuelle Array trotzdem, damit der "RUHE/AKTIV" Status im Widget live bleibt
msg.payload = history;
return msg;