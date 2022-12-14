class Lesson {

    constructor(text, displayId, inputId, keyboardId) {
        this.inputId = inputId
        this.text = text
        this.display = new Display(displayId, text)
        this.initializeInput()
        this.keyPresses = []
        this.chars = ""
        this.kb = new Keyboard(keyboardId)
        this.kb.render()
    }

    initializeInput() {
        const INPUT = $(this.inputId)
        $('#display').parent().click(() => INPUT.focus())
        INPUT.on('keydown', (event) => {
            let keyPress = new KeyPress(event.key, event.timeStamp)
            this.keyPresses.push(keyPress)
            this.kb.press(keyPress.key)

            let curIndex = this.chars.length
            if (keyPress.key === "Backspace") {
                this.chars = this.chars.slice(0, -1)

                this.display.pop()
            } else {
                let char = keyPress.key === "Enter" ? "\n" : keyPress.key
                this.chars += char
                keyPress.correct = this.text[curIndex] === char
                if (keyPress.correct) {
                    this.display.push(keyPress.correct)
                } else {
                    this.display.push(keyPress.correct)
                }
            }

            if (this.chars === this.text) {
                this.finish()
            }
        })
        INPUT.on('keyup', (event) => {
            this.kb.release(event.key)
        })
        INPUT.focus()
        this.startStatsUpdater()
    }

    finish() {
        console.log("Finished!")
        const INPUT = $(this.inputId)
        this.kb.releaseAll()
        INPUT.off()
        this.stopStatsUpdater()

        // show stats
        let stats = this.calculateStats()
        console.table(stats)
        // save stats
        $('body').modal({
            title: 'Results',
            class: 'mini',
            closeIcon: true,
            content: `You finished in ${stats.time}ms with ${stats.accuracy * 100}% accuracy and ${stats["chars per minute"]} chars per minute`,
            actions: [{
                text: 'Alright, got it',
                class: 'green'
            }]
        }).modal('show');
    }

    calculateStats() {
        let stats = {
            "time": this.getTime(),
            "accuracy": this.getAccuracy(),
            "chars per minute": this.getCharsPerMinute()
        }
        return stats
    }

    getAccuracy() {
        let correct = this.keyPresses.filter((kp) => kp.correct === true)
        let validChars = this.keyPresses.filter((kp) => kp.correct !== null)
        return correct.length / validChars.length
    }

    getTime() {
        if (this.keyPresses.length === 0) {
            return 0
        }
        return this.keyPresses[this.keyPresses.length - 1].timestamp - this.keyPresses[0].timestamp
    }

    getCharsPerMinute() {
        return this.chars.length / this.getTime() * 1000 * 60
    }

    startStatsUpdater() {
        this.statsUpdaterTimer = setInterval(() => {
            let stats = this.calculateStats()
            const STATS = $('#stats')
            STATS.empty()
            STATS.append(`<p>Time: ${(stats.time / 1000).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}s</p>`)
            STATS.append(`<p>Accuracy: ${(stats.accuracy * 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%</p>`)
            STATS.append(`<p>Chars per minute: ${stats["chars per minute"].toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>`)
        }, 1000)
    }

    stopStatsUpdater() {
        clearInterval(this.statsUpdaterTimer)
    }

}