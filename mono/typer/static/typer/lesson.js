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
    }

    finish() {
        console.log("Finished!")

        // block input
        // $(this.inputId).prop("disabled", true)

        // show stats
        let stats = this.calculateStats()
        console.table(stats)
        // save stats
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
        return this.keyPresses[this.keyPresses.length - 1].timestamp - this.keyPresses[0].timestamp
    }

    getCharsPerMinute() {
        return this.chars.length / this.getTime() * 1000 * 60
    }
}