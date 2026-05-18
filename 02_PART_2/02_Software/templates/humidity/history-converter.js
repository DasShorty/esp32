let history = global.get('humid-history') || [];

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

let twentyFourHoursAgo = Date.now() - (24 * 60 * 60 * 1000);
history = history.filter(record => record.timestamp >= twentyFourHoursAgo);

global.set('humid-history', history);

msg.payload = history;
return msg;