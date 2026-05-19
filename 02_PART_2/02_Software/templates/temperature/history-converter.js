let history = global.get('temp-history') || [];

let timeLabel = new Date().toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
});

history.push({
    time: timeLabel,
    value: msg.payload,
    timestamp: new Date()
});

let hourAgo = Date.now() - (60 * 60 * 1000);
history = history.filter(record => record.timestamp >= hourAgo);

global.set('temp-history', history);

msg.payload = history;
return msg;
