const temperature = msg.temperature;
const fanSwitchToggle = msg.fanRule;
const fanSwitch = msg.fan;

if (fanSwitchToggle) {

    if (temperature > 30) {
        return msg.payload.fanStatus = true;
    }

    return msg.payload.fanStatus = false;
}

msg.payload.fanStatus = fanSwitch;

return msg;