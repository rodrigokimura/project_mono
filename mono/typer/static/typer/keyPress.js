class KeyPress {
    constructor(key, timestamp, correct = null) {
        this.key = key
        this.timestamp = timestamp
        this.correct = correct
    }
    toJSON() {
        return {
            key: this.key,
            timestamp: Math.round(this.timestamp),
            correct: this.correct
        }
    }
}