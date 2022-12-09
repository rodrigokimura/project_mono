class KeyPress {
    constructor(key, timestamp, correct = null) {
        this.key = key
        this.timestamp = timestamp
        this.correct = correct
    }
    static register(key, timestamp) {
        keys.push(new KeyPress(key, timestamp))
    }
    static getKeys() {
        return keys
    }
}