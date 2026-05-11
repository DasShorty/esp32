// noinspection JSAnnotator

const maxLogs = 10;

let log = context.get('motion-eventLog') || [];

if (msg.payload === true || msg.payload === 1 || msg.payload === "on") {

    let now = new Date();
    let timeString = now.toLocaleTimeString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });

    if (log.filter((element) => element.time === timeString).length === 0) {
        log.unshift({
            time: timeString,
            id: Date.now()
        });

        if (log.length > maxLogs) {
            log = log.slice(0, maxLogs);
        }
    }

    context.set('motion-eventLog', log);
}

msg.payload = log;
return msg;